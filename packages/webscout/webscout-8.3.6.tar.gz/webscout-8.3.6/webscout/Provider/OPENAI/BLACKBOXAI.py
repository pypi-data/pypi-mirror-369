# from pickle import NONE
import requests
import random
import string
import base64
from datetime import datetime, timedelta
from typing import Generator, List, Dict, Optional, Any, Union
import uuid
import time
import codecs
import gzip
import zstandard as zstd
import brotli
import zlib
from webscout.Provider.OPENAI.utils import (
    ChatCompletion, Choice,
    ChatCompletionMessage, CompletionUsage, count_tokens,
    ChatCompletionChunk, ChoiceDelta  # Ensure ChoiceDelta is always imported at the top
)
try:
    from webscout.litagent import LitAgent
    agent = LitAgent()
except ImportError:
    print("Warning: LitAgent not available, using default user agent")
    class MockAgent:
        def random(self):
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    agent = MockAgent()

from webscout.Provider.OPENAI.base import OpenAICompatibleProvider, BaseChat, BaseCompletions

class StreamingDecompressor:
    """
    A streaming decompressor that can handle partial compressed data in real-time.
    This allows for true streaming decompression without buffering entire response.
    """
    def __init__(self, content_encoding: str):
        self.encoding = content_encoding.lower().strip() if content_encoding else None
        self.decompressor = None
        self.text_decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self.zstd_buffer = b""  # Buffer for zstd incomplete frames
        
        if self.encoding == 'gzip':
            self.decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)  # gzip format
        elif self.encoding == 'deflate':
            self.decompressor = zlib.decompressobj()  # deflate format
        elif self.encoding == 'zstd':
            self.decompressor = zstd.ZstdDecompressor()
        elif self.encoding == 'br':
            self.decompressor = brotli.Decompressor()
    
    def decompress_chunk(self, chunk: bytes) -> str:
        """
        Decompress a chunk of data and return decoded text.
        Handles partial compressed data properly for real-time streaming.
        """
        try:
            if not chunk:
                return ""
            
            if not self.encoding or self.encoding not in ['gzip', 'deflate', 'zstd', 'br']:
                # No compression or unsupported - decode directly
                return self.text_decoder.decode(chunk, final=False)
            
            if self.encoding in ['gzip', 'deflate']:
                # Use zlib decompressor for gzip/deflate
                decompressed_data = self.decompressor.decompress(chunk)
                return self.text_decoder.decode(decompressed_data, final=False)
            
            elif self.encoding == 'zstd':
                # Zstandard streaming decompression with buffering for incomplete frames
                self.zstd_buffer += chunk
                try:
                    # Try to decompress the current buffer
                    decompressed_data = self.decompressor.decompress(self.zstd_buffer)
                    # If successful, clear the buffer and return decoded text
                    self.zstd_buffer = b""
                    return self.text_decoder.decode(decompressed_data, final=False)
                except zstd.ZstdError:
                    # Frame is incomplete, keep buffering
                    # Try to decompress any complete frames from buffer start
                    try:
                        # Process buffer in chunks to find complete frames
                        buffer_len = len(self.zstd_buffer)
                        if buffer_len > 4:  # Minimum zstd frame size
                            # Try smaller chunks of the buffer
                            for end_pos in range(4, buffer_len + 1):
                                try:
                                    partial_data = self.decompressor.decompress(self.zstd_buffer[:end_pos])
                                    # If we got here, we found a complete frame
                                    self.zstd_buffer = self.zstd_buffer[end_pos:]
                                    return self.text_decoder.decode(partial_data, final=False)
                                except zstd.ZstdError:
                                    continue
                    except Exception:
                        pass
                    return ""
            
            elif self.encoding == 'br':
                # Brotli streaming decompression
                try:
                    decompressed_data = self.decompressor.decompress(chunk)
                    return self.text_decoder.decode(decompressed_data, final=False)
                except brotli.error:
                    # If brotli fails, it might need more data or be at end
                    return ""
        
        except Exception as e:
            # If decompression fails, try to decode the chunk as-is (fallback)
            try:
                return self.text_decoder.decode(chunk, final=False)
            except UnicodeDecodeError:
                return ""
    
    def finalize(self) -> str:
        """
        Finalize the decompression and return any remaining decoded text.
        """
        try:
            remaining_text = ""
            
            if self.encoding in ['gzip', 'deflate'] and self.decompressor:
                # Flush any remaining compressed data
                remaining_data = self.decompressor.flush()
                if remaining_data:
                    remaining_text = self.text_decoder.decode(remaining_data, final=True)
                else:
                    remaining_text = self.text_decoder.decode(b"", final=True)
            elif self.encoding == 'zstd':
                # Process any remaining buffered data
                if self.zstd_buffer:
                    try:
                        remaining_data = self.decompressor.decompress(self.zstd_buffer)
                        remaining_text = self.text_decoder.decode(remaining_data, final=True)
                    except:
                        # If buffered data can't be decompressed, finalize decoder
                        remaining_text = self.text_decoder.decode(b"", final=True)
                else:
                    remaining_text = self.text_decoder.decode(b"", final=True)
            else:
                # Finalize the text decoder for other encodings
                remaining_text = self.text_decoder.decode(b"", final=True)
            
            return remaining_text
        except Exception:
            # Ensure we always finalize the text decoder
            try:
                return self.text_decoder.decode(b"", final=True)
            except:
                return ""

def decompress_response(response_content: bytes, content_encoding: str) -> str:
    """
    Decompress response content based on the Content-Encoding header.
    
    Args:
        response_content: The raw response content as bytes
        content_encoding: The Content-Encoding header value
        
    Returns:
        str: The decompressed and decoded content as UTF-8 string
        
    Raises:
        IOError: If decompression fails
    """
    try:
        if not content_encoding:
            # No compression, decode directly
            return response_content.decode('utf-8')
        
        encoding = content_encoding.lower().strip()
        
        if encoding == 'zstd':
            # Decompress using zstandard
            dctx = zstd.ZstdDecompressor()
            decompressed_data = dctx.decompress(response_content)
            return decompressed_data.decode('utf-8')
        
        elif encoding == 'gzip':
            # Decompress using gzip
            decompressed_data = gzip.decompress(response_content)
            return decompressed_data.decode('utf-8')
        
        elif encoding == 'br':
            # Decompress using brotli
            decompressed_data = brotli.decompress(response_content)
            return decompressed_data.decode('utf-8')
        
        elif encoding == 'deflate':
            # Decompress using zlib (deflate)
            import zlib
            decompressed_data = zlib.decompress(response_content)
            return decompressed_data.decode('utf-8')
        
        else:
            # Unknown or unsupported encoding, try to decode as-is
            return response_content.decode('utf-8')
            
    except Exception as e:
        raise IOError(f"Failed to decompress response with encoding '{content_encoding}': {str(e)}") from e

def to_data_uri(image_data):
    """Convert image data to a data URI format"""
    if isinstance(image_data, str):
        # Assume it's already a data URI
        return image_data

    # Encode binary data to base64
    encoded = base64.b64encode(image_data).decode('utf-8')

    # Determine MIME type (simplified)
    mime_type = "image/jpeg"  # Default
    if image_data.startswith(b'\x89PNG'):
        mime_type = "image/png"
    elif image_data.startswith(b'\xff\xd8'):
        mime_type = "image/jpeg"
    elif image_data.startswith(b'GIF'):
        mime_type = "image/gif"

    return f"data:{mime_type};base64,{encoded}"

def clean_text(text):
    """Clean text by removing null bytes and control characters except newlines and tabs."""
    import re
    if not isinstance(text, str):
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Keep newlines, tabs, and other printable characters, remove other control chars
    # This regex matches control characters except \n, \r, \t
    return re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)


class Completions(BaseCompletions):
    def __init__(self, client: 'BLACKBOXAI'):
        self._client = client

    def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        timeout: Optional[int] = None,
        proxies: Optional[dict] = None,
        **kwargs: Any
    ) -> Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]]:
        """
        Create a chat completion with BlackboxAI API.

        Args:
            model: The model to use (from AVAILABLE_MODELS)
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            stream: If True, yields streaming chunks
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter (0-1)
            **kwargs: Additional parameters to pass to the API

        Returns:
            Returns a ChatCompletion object or a generator for streaming
        """
        # Generate request ID and timestamp
        request_id = str(uuid.uuid4())
        created_time = int(time.time())

        # Extract system message if present
        system_message = "You are a helpful AI assistant."
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content")
                break

        # Look for any image content
        media = []
        for msg in messages:
            if msg.get("role") == "user":
                # Check for image attachments in content
                content = msg.get("content", [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "image_url":
                            image_url = item.get("image_url", {})
                            if isinstance(image_url, dict) and "url" in image_url:
                                url = image_url["url"]
                                if url.startswith("data:"):
                                    # It's already a data URI
                                    image_name = f"image_{len(media)}.png"
                                    media.append((url, image_name))
                                else:
                                    # Need to fetch and convert to data URI
                                    try:
                                        image_response = requests.get(url)
                                        if image_response.ok:
                                            image_name = f"image_{len(media)}.png"
                                            media.append((image_response.content, image_name))
                                    except Exception as e:
                                        pass

        # Check if streaming is requested and raise an error
        if stream:
            return self._create_streaming(
                request_id=request_id,
                created_time=created_time,
                model=model,
                messages=messages,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                media=media,
                timeout=timeout,
                proxies=proxies
            )

        # Use non-streaming implementation
        return self._create_non_streaming(
            request_id=request_id,
            created_time=created_time,
            model=model,
            messages=messages,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            media=media,
            timeout=timeout,
            proxies=proxies
        )


    def _create_non_streaming(
        self,
        *,
        request_id: str,
        created_time: int,
        model: str,
        messages: List[Dict[str, Any]],
        system_message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        media: List = None,
        timeout: Optional[int] = None,
        proxies: Optional[dict] = None
    ) -> ChatCompletion:
        """Implementation for non-streaming chat completions."""
        original_proxies = self._client.session.proxies.copy()
        # Only use proxies if they are explicitly provided and not causing issues
        if proxies is not None and proxies:
            self._client.session.proxies.update(proxies)
        else:
            # Clear proxies to avoid connection issues
            self._client.session.proxies = {}
        try:
            # Prepare user messages for BlackboxAI API format
            blackbox_messages = []
            for i, msg in enumerate(messages):
                if msg["role"] == "system":
                    continue  # System message handled separately

                msg_id = self._client.generate_id() if i > 0 else request_id
                blackbox_messages.append({
                    "id": msg_id,
                    "content": msg["content"],
                    "role": msg["role"]
                })

            # Add image data if provided
            if media and blackbox_messages:
                blackbox_messages[-1]['data'] = {
                    "imagesData": [
                        {
                            "filePath": f"/",
                            "contents": to_data_uri(image[0])
                        } for image in media
                    ],
                    "fileText": "",
                    "title": ""
                }

            # Generate request payload with session
            request_email = f"{self._client.generate_random_string(8)}@blackbox.ai"
            session_data = self._client.generate_session(request_email)

            # Create the API request payload
            payload = self._client.create_request_payload(
                messages=blackbox_messages,
                chat_id=request_id,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                session_data=session_data,
                model=model
            )

            # Make the API request with cookies and retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self._client.session.post(
                        self._client.api_endpoint,
                        json=payload,
                        headers=self._client.headers,
                        cookies=self._client.cookies,
                        timeout=timeout if timeout is not None else self._client.timeout
                    )
                    break  # Success, exit retry loop
                except (requests.exceptions.ConnectionError, requests.exceptions.ProxyError) as e:
                    if attempt == max_retries - 1:
                        raise IOError(f"BlackboxAI connection failed after {max_retries} attempts: {str(e)}") from e
                    # Clear proxies and retry
                    self._client.session.proxies = {}
                    time.sleep(1)  # Wait before retry

            # Process the response
            full_content = ""
            if response.status_code == 200:
                # Check for Content-Encoding header
                content_encoding = response.headers.get('Content-Encoding')
                
                # Decompress the response if needed
                try:
                    response_text = decompress_response(response.content, content_encoding)
                except IOError as e:
                    # If decompression fails, fall back to the original method
                    print(f"Warning: {e}. Falling back to original decoding method.")
                    decoder = codecs.getincrementaldecoder("utf-8")("replace")
                    response_text = decoder.decode(response.content, final=True)

                # Handle possible SSE format in response
                if "data: " in response_text:
                    # Extract content from SSE format
                    content_lines = []
                    for line in response_text.split('\n'):
                        if line.startswith("data: "):
                            line = line[6:].strip()
                            if line and not any(error_msg in line.lower() for error_msg in [
                                "service has been suspended",
                                "api request failed",
                                "you have reached your request limit"
                            ]):
                                content_lines.append(line)
                    full_content = "".join(content_lines)
                else:
                    # Regular response
                    full_content = response_text
            else:
                # Handle error response
                raise IOError(f"BlackboxAI request failed with status code {response.status_code}")

            # Clean and create the completion message
            cleaned_content = clean_text(full_content)
            message = ChatCompletionMessage(
                role="assistant",
                content=cleaned_content
            )

            # Create the choice with the message
            choice = Choice(
                index=0,
                message=message,
                finish_reason="stop"
            )

            # Estimate token usage using count_tokens
            prompt_tokens = count_tokens([str(msg.get("content", "")) for msg in messages])
            completion_tokens = count_tokens(cleaned_content)

            # Create the final completion object
            completion = ChatCompletion(
                id=request_id,
                choices=[choice],
                created=created_time,
                model=model,
                usage=CompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens
                )
            )

            return completion

        except Exception as e:
            raise IOError(f"BlackboxAI request failed: {str(e)}") from e
        finally:
            # Restore original proxies
            self._client.session.proxies = original_proxies

    def _create_streaming(
        self,
        *,
        request_id: str,
        created_time: int,
        model: str,
        messages: List[Dict[str, Any]],
        system_message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        media: List = None,
        timeout: Optional[int] = None,
        proxies: Optional[dict] = None
    ):
        """Implementation for streaming chat completions (OpenAI-compatible chunks)."""
        original_proxies = self._client.session.proxies.copy()
        # Only use proxies if they are explicitly provided and not causing issues
        if proxies is not None and proxies:
            self._client.session.proxies.update(proxies)
        else:
            # Clear proxies to avoid connection issues
            self._client.session.proxies = {}
        try:
            # Prepare user messages for BlackboxAI API format
            blackbox_messages = []
            for i, msg in enumerate(messages):
                if msg["role"] == "system":
                    continue  # System message handled separately
                msg_id = self._client.generate_id() if i > 0 else request_id
                blackbox_messages.append({
                    "id": msg_id,
                    "content": msg["content"],
                    "role": msg["role"]
                })
            # Add image data if provided
            if media and blackbox_messages:
                blackbox_messages[-1]['data'] = {
                    "imagesData": [
                        {
                            "filePath": f"/",
                            "contents": to_data_uri(image[0])
                        } for image in media
                    ],
                    "fileText": "",
                    "title": ""
                }
            # Generate request payload with session
            request_email = f"{self._client.generate_random_string(8)}@blackbox.ai"
            session_data = self._client.generate_session(request_email)
            payload = self._client.create_request_payload(
                messages=blackbox_messages,
                chat_id=request_id,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                session_data=session_data,
                model=model
            )
            # Make the API request with cookies, stream=True and retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self._client.session.post(
                        self._client.api_endpoint,
                        json=payload,
                        headers=self._client.headers,
                        cookies=self._client.cookies,
                        stream=True,
                        timeout=timeout if timeout is not None else self._client.timeout
                    )
                    break  # Success, exit retry loop
                except (requests.exceptions.ConnectionError, requests.exceptions.ProxyError) as e:
                    if attempt == max_retries - 1:
                        raise IOError(f"BlackboxAI connection failed after {max_retries} attempts: {str(e)}") from e
                    # Clear proxies and retry
                    self._client.session.proxies = {}
                    time.sleep(1)  # Wait before retry
            # Blackbox streams as raw text, no line breaks, so chunk manually
            chunk_size = 32  # Tune as needed for smoothness
            # ChoiceDelta is already imported at the top of the file
            
            # Check if the response is compressed and create appropriate decompressor
            content_encoding = response.headers.get('Content-Encoding')
            streaming_decompressor = StreamingDecompressor(content_encoding)
            
            # Stream with real-time decompression
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                
                # Decompress chunk in real-time
                text = streaming_decompressor.decompress_chunk(chunk)
                
                if text:
                    cleaned_chunk = clean_text(text)
                    if cleaned_chunk.strip():
                        delta = ChoiceDelta(content=cleaned_chunk, role="assistant")
                        choice = Choice(index=0, delta=delta, finish_reason=None)
                        chunk_obj = ChatCompletionChunk(
                            id=request_id,
                            choices=[choice],
                            created=created_time,
                            model=model,
                            system_fingerprint=None
                        )
                        yield chunk_obj
            
            # Finalize decompression and get any remaining text
            final_text = streaming_decompressor.finalize()
            if final_text.strip():
                cleaned_final = clean_text(final_text)
                delta = ChoiceDelta(content=cleaned_final, role="assistant")
                choice = Choice(index=0, delta=delta, finish_reason=None)
                chunk_obj = ChatCompletionChunk(
                    id=request_id,
                    choices=[choice],
                    created=created_time,
                    model=model,
                    system_fingerprint=None
                )
                yield chunk_obj
            
            # Send final chunk with finish_reason="stop"
            delta = ChoiceDelta(content="", role="assistant")
            choice = Choice(index=0, delta=delta, finish_reason="stop")
            final_chunk = ChatCompletionChunk(
                id=request_id,
                choices=[choice],
                created=created_time,
                model=model,
                system_fingerprint=None
            )
            yield final_chunk
            
        except Exception as e:
            # Handle errors gracefully by yielding an error chunk
            error_delta = ChoiceDelta(content=f"Error: {str(e)}", role="assistant")
            error_choice = Choice(index=0, delta=error_delta, finish_reason="stop")
            error_chunk = ChatCompletionChunk(
                id=request_id,
                choices=[error_choice],
                created=created_time,
                model=model,
                system_fingerprint=None
            )
            yield error_chunk
        finally:
            # Restore original proxies
            self._client.session.proxies = original_proxies


class Chat(BaseChat):
    def __init__(self, client: 'BLACKBOXAI'):
        self.completions = Completions(client)


class BLACKBOXAI(OpenAICompatibleProvider):
    """
    OpenAI-compatible client for BlackboxAI API.

    Usage:
        client = BLACKBOXAI()
        response = client.chat.completions.create(
            model="GPT-4.1",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(response.choices[0].message.content)
    """
    # Default model
    default_model = "GPT-4.1"
    default_vision_model = default_model
    api_endpoint = "https://www.blackbox.ai/api/chat"
    timeout = None

    # New OpenRouter models list
    openrouter_models = [
        "Deepcoder 14B Preview",
        "DeepHermes 3 Llama 3 8B Preview",
        "DeepSeek R1 Zero",
        "Dolphin3.0 Mistral 24B",
        "Dolphin3.0 R1 Mistral 24B",
        "Flash 3",
        "Gemini 2.0 Flash Experimental",
        "Gemma 2 9B",
        "Gemma 3 12B",
        "Gemma 3 1B",
        "Gemma 3 27B",
        "Gemma 3 4B",
        "Kimi VL A3B Thinking",
        "Llama 3.1 8B Instruct",
        "Llama 3.1 Nemotron Ultra 253B v1",
        "Llama 3.2 11B Vision Instruct",
        "Llama 3.2 1B Instruct",
        "Llama 3.2 3B Instruct",
        "Llama 3.3 70B Instruct",
        "Llama 3.3 Nemotron Super 49B v1",
        "Llama 4 Maverick",
        "Llama 4 Scout",
        "Mistral 7B Instruct",
        "Mistral Nemo",
        "Mistral Small 3",
        "Mistral Small 3.1 24B",
        "Molmo 7B D",
        "Moonlight 16B A3B Instruct",
        "Qwen2.5 72B Instruct",
        "Qwen2.5 7B Instruct",
        "Qwen2.5 Coder 32B Instruct",
        "Qwen2.5 VL 32B Instruct",
        "Qwen2.5 VL 3B Instruct",
        "Qwen2.5 VL 72B Instruct",
        "Qwen2.5-VL 7B Instruct",
        "Qwerky 72B",
        "QwQ 32B",
        "QwQ 32B Preview",
        "QwQ 32B RpR v1",
        "R1",
        "R1 Distill Llama 70B",
        "R1 Distill Qwen 14B",
        "R1 Distill Qwen 32B",
    ]

    # New base models list
    models = [
        "gpt-4.1-mini", # Added new model
        default_model,
        "o3-mini",
        "gpt-4.1-nano",
        "Claude Opus 4",  # Added Claude Opus 4
        "Claude Sonnet 4",  # Added Claude Sonnet 4
        "Claude-sonnet-3.7",
        "Claude-sonnet-3.5",
        "Grok 3",  # Added Grok 3
        "Gemini 2.5 Pro",  # Added Gemini 2.5 Pro
        "UI-TARS 72B",  # Added UI-TARS 72B
        "DeepSeek-R1",
        "Mistral-Small-24B-Instruct-2501",
        *openrouter_models,
        # Trending agent modes (names)
        'Python Agent', 'HTML Agent', 'Builder Agent', 'Java Agent', 'JavaScript Agent',
        'React Agent', 'Android Agent', 'Flutter Agent', 'Next.js Agent', 'AngularJS Agent',
        'Swift Agent', 'MongoDB Agent', 'PyTorch Agent', 'Xcode Agent', 'Azure Agent',
        'Bitbucket Agent', 'DigitalOcean Agent', 'Docker Agent', 'Electron Agent',
        'Erlang Agent', 'FastAPI Agent', 'Firebase Agent', 'Flask Agent', 'Git Agent',
        'Gitlab Agent', 'Go Agent', 'Godot Agent', 'Google Cloud Agent', 'Heroku Agent'
    ]

    # Models that support vision capabilities
    vision_models = [default_vision_model, 'o3-mini', "Llama 3.2 11B Vision Instruct", "Gemini 2.5 Pro", "Claude Sonnet 4", "Claude Opus 4", "UI-TARS 72B"] # Added Llama vision, Gemini 2.5 Pro, Claude Sonnet 4, Claude Opus 4, and UI-TARS 72B

    # Models that can be directly selected by users
    userSelectedModel = ['o3-mini', 'Claude Opus 4', 'Claude Sonnet 4', 'Claude-sonnet-3.7', 'Claude-sonnet-3.5', 'Grok 3', 'Gemini 2.5 Pro', 'UI-TARS 72B', 'DeepSeek-R1', 'Mistral-Small-24B-Instruct-2501'] + openrouter_models

    # Agent mode configurations
    agentMode = {
        # OpenRouter Free
        'Deepcoder 14B Preview': {'mode': True, 'id': "agentica-org/deepcoder-14b-preview:free", 'name': "Deepcoder 14B Preview"},
        'DeepHermes 3 Llama 3 8B Preview': {'mode': True, 'id': "nousresearch/deephermes-3-llama-3-8b-preview:free", 'name': "DeepHermes 3 Llama 3 8B Preview"},
        'DeepSeek R1 Zero': {'mode': True, 'id': "deepseek/deepseek-r1-zero:free", 'name': "DeepSeek R1 Zero"},
        'Dolphin3.0 Mistral 24B': {'mode': True, 'id': "cognitivecomputations/dolphin3.0-mistral-24b:free", 'name': "Dolphin3.0 Mistral 24B"},
        'Dolphin3.0 R1 Mistral 24B': {'mode': True, 'id': "cognitivecomputations/dolphin3.0-r1-mistral-24b:free", 'name': "Dolphin3.0 R1 Mistral 24B"},
        'Flash 3': {'mode': True, 'id': "rekaai/reka-flash-3:free", 'name': "Flash 3"},
        'Gemini 2.0 Flash Experimental': {'mode': True, 'id': "google/gemini-2.0-flash-exp:free", 'name': "Gemini 2.0 Flash Experimental"},
        'Gemma 2 9B': {'mode': True, 'id': "google/gemma-2-9b-it:free", 'name': "Gemma 2 9B"},
        'Gemma 3 12B': {'mode': True, 'id': "google/gemma-3-12b-it:free", 'name': "Gemma 3 12B"},
        'Gemma 3 1B': {'mode': True, 'id': "google/gemma-3-1b-it:free", 'name': "Gemma 3 1B"},
        'Gemma 3 27B': {'mode': True, 'id': "google/gemma-3-27b-it:free", 'name': "Gemma 3 27B"},
        'Gemma 3 4B': {'mode': True, 'id': "google/gemma-3-4b-it:free", 'name': "Gemma 3 4B"},
        'Kimi VL A3B Thinking': {'mode': True, 'id': "moonshotai/kimi-vl-a3b-thinking:free", 'name': "Kimi VL A3B Thinking"},
        'Llama 3.1 8B Instruct': {'mode': True, 'id': "meta-llama/llama-3.1-8b-instruct:free", 'name': "Llama 3.1 8B Instruct"},
        'Llama 3.1 Nemotron Ultra 253B v1': {'mode': True, 'id': "nvidia/llama-3.1-nemotron-ultra-253b-v1:free", 'name': "Llama 3.1 Nemotron Ultra 253B v1"},
        'Llama 3.2 11B Vision Instruct': {'mode': True, 'id': "meta-llama/llama-3.2-11b-vision-instruct:free", 'name': "Llama 3.2 11B Vision Instruct"},
        'Llama 3.2 1B Instruct': {'mode': True, 'id': "meta-llama/llama-3.2-1b-instruct:free", 'name': "Llama 3.2 1B Instruct"},
        'Llama 3.2 3B Instruct': {'mode': True, 'id': "meta-llama/llama-3.2-3b-instruct:free", 'name': "Llama 3.2 3B Instruct"},
        'Llama 3.3 70B Instruct': {'mode': True, 'id': "meta-llama/llama-3.3-70b-instruct:free", 'name': "Llama 3.3 70B Instruct"},
        'Llama 3.3 Nemotron Super 49B v1': {'mode': True, 'id': "nvidia/llama-3.3-nemotron-super-49b-v1:free", 'name': "Llama 3.3 Nemotron Super 49B v1"},
        'Llama 4 Maverick': {'mode': True, 'id': "meta-llama/llama-4-maverick:free", 'name': "Llama 4 Maverick"},
        'Llama 4 Scout': {'mode': True, 'id': "meta-llama/llama-4-scout:free", 'name': "Llama 4 Scout"},
        'Mistral 7B Instruct': {'mode': True, 'id': "mistralai/mistral-7b-instruct:free", 'name': "Mistral 7B Instruct"},
        'Mistral Nemo': {'mode': True, 'id': "mistralai/mistral-nemo:free", 'name': "Mistral Nemo"},
        'Mistral Small 3': {'mode': True, 'id': "mistralai/mistral-small-24b-instruct-2501:free", 'name': "Mistral Small 3"}, # Matches Mistral-Small-24B-Instruct-2501
        'Mistral Small 3.1 24B': {'mode': True, 'id': "mistralai/mistral-small-3.1-24b-instruct:free", 'name': "Mistral Small 3.1 24B"},
        'Molmo 7B D': {'mode': True, 'id': "allenai/molmo-7b-d:free", 'name': "Molmo 7B D"},
        'Moonlight 16B A3B Instruct': {'mode': True, 'id': "moonshotai/moonlight-16b-a3b-instruct:free", 'name': "Moonlight 16B A3B Instruct"},
        'Qwen2.5 72B Instruct': {'mode': True, 'id': "qwen/qwen-2.5-72b-instruct:free", 'name': "Qwen2.5 72B Instruct"},
        'Qwen2.5 7B Instruct': {'mode': True, 'id': "qwen/qwen-2.5-7b-instruct:free", 'name': "Qwen2.5 7B Instruct"},
        'Qwen2.5 Coder 32B Instruct': {'mode': True, 'id': "qwen/qwen-2.5-coder-32b-instruct:free", 'name': "Qwen2.5 Coder 32B Instruct"},
        'Qwen2.5 VL 32B Instruct': {'mode': True, 'id': "qwen/qwen2.5-vl-32b-instruct:free", 'name': "Qwen2.5 VL 32B Instruct"},
        'Qwen2.5 VL 3B Instruct': {'mode': True, 'id': "qwen/qwen2.5-vl-3b-instruct:free", 'name': "Qwen2.5 VL 3B Instruct"},
        'Qwen2.5 VL 72B Instruct': {'mode': True, 'id': "qwen/qwen2.5-vl-72b-instruct:free", 'name': "Qwen2.5 VL 72B Instruct"},
        'Qwen2.5-VL 7B Instruct': {'mode': True, 'id': "qwen/qwen-2.5-vl-7b-instruct:free", 'name': "Qwen2.5-VL 7B Instruct"},
        'Qwerky 72B': {'mode': True, 'id': "featherless/qwerky-72b:free", 'name': "Qwerky 72B"},
        'QwQ 32B': {'mode': True, 'id': "qwen/qwq-32b:free", 'name': "QwQ 32B"},
        'QwQ 32B Preview': {'mode': True, 'id': "qwen/qwq-32b-preview:free", 'name': "QwQ 32B Preview"},
        'QwQ 32B RpR v1': {'mode': True, 'id': "arliai/qwq-32b-arliai-rpr-v1:free", 'name': "QwQ 32B RpR v1"},
        'R1': {'mode': True, 'id': "deepseek/deepseek-r1:free", 'name': "R1"}, # Matches DeepSeek-R1
        'R1 Distill Llama 70B': {'mode': True, 'id': "deepseek/deepseek-r1-distill-llama-70b:free", 'name': "R1 Distill Llama 70B"},
        'R1 Distill Qwen 14B': {'mode': True, 'id': "deepseek/deepseek-r1-distill-qwen-14b:free", 'name': "R1 Distill Qwen 14B"},
        'R1 Distill Qwen 32B': {'mode': True, 'id': "deepseek/deepseek-r1-distill-qwen-32b:free", 'name': "R1 Distill Qwen 32B"},
        # Default models from the new list
        'Claude Opus 4': {'mode': True, 'id': "anthropic/claude-opus-4", 'name': "Claude Opus 4"},
        'Claude Sonnet 4': {'mode': True, 'id': "anthropic/claude-sonnet-4", 'name': "Claude Sonnet 4"},
        'Claude-sonnet-3.7': {'mode': True, 'id': "Claude-sonnet-3.7", 'name': "Claude-sonnet-3.7"},
        'Claude-sonnet-3.5': {'mode': True, 'id': "Claude-sonnet-3.5", 'name': "Claude-sonnet-3.5"},
        'Grok 3': {'mode': True, 'id': "x-ai/grok-3-beta", 'name': "Grok 3"},
        'Gemini 2.5 Pro': {'mode': True, 'id': "google/gemini-2.5-pro-preview-03-25", 'name': "Gemini 2.5 Pro"},
        'UI-TARS 72B': {'mode': True, 'id': "bytedance-research/ui-tars-72b:free", 'name': "UI-TARS 72B"},
        'DeepSeek-R1': {'mode': True, 'id': "deepseek-reasoner", 'name': "DeepSeek-R1"}, # This is 'R1' in openrouter, but 'DeepSeek-R1' in base models
        'Mistral-Small-24B-Instruct-2501': {'mode': True, 'id': "mistralai/Mistral-Small-24B-Instruct-2501", 'name': "Mistral-Small-24B-Instruct-2501"},
        # Add default_model if it's not covered and has an agent mode
        default_model: {'mode': True, 'id': "openai/gpt-4.1", 'name': default_model}, # Assuming GPT-4.1 is agent-compatible
        'o3-mini': {'mode': True, 'id': "o3-mini", 'name': "o3-mini"}, # Assuming o3-mini is agent-compatible
        'gpt-4.1-nano': {'mode': True, 'id': "gpt-4.1-nano", 'name': "gpt-4.1-nano"}, # Assuming gpt-4.1-nano is agent-compatible
        'gpt-4.1-mini': {'mode': True, 'id': "gpt-4.1-mini", 'name': "gpt-4.1-mini"}, # Added agent mode for gpt-4.1-mini
    }

    # Trending agent modes
    trendingAgentMode = {
        'Python Agent': {'mode': True, 'id': "python"},
        'HTML Agent': {'mode': True, 'id': "html"},
        'Builder Agent': {'mode': True, 'id': "builder"},
        'Java Agent': {'mode': True, 'id': "java"},
        'JavaScript Agent': {'mode': True, 'id': "javascript"},
        'React Agent': {'mode': True, 'id': "react"},
        'Android Agent': {'mode': True, 'id': "android"},
        'Flutter Agent': {'mode': True, 'id': "flutter"},
        'Next.js Agent': {'mode': True, 'id': "next.js"},
        'AngularJS Agent': {'mode': True, 'id': "angularjs"},
        'Swift Agent': {'mode': True, 'id': "swift"},
        'MongoDB Agent': {'mode': True, 'id': "mongodb"},
        'PyTorch Agent': {'mode': True, 'id': "pytorch"},
        'Xcode Agent': {'mode': True, 'id': "xcode"},
        'Azure Agent': {'mode': True, 'id': "azure"},
        'Bitbucket Agent': {'mode': True, 'id': "bitbucket"},
        'DigitalOcean Agent': {'mode': True, 'id': "digitalocean"},
        'Docker Agent': {'mode': True, 'id': "docker"},
        'Electron Agent': {'mode': True, 'id': "electron"},
        'Erlang Agent': {'mode': True, 'id': "erlang"},
        'FastAPI Agent': {'mode': True, 'id': "fastapi"},
        'Firebase Agent': {'mode': True, 'id': "firebase"},
        'Flask Agent': {'mode': True, 'id': "flask"},
        'Git Agent': {'mode': True, 'id': "git"},
        'Gitlab Agent': {'mode': True, 'id': "gitlab"},
        'Go Agent': {'mode': True, 'id': "go"},
        'Godot Agent': {'mode': True, 'id': "godot"},
        'Google Cloud Agent': {'mode': True, 'id': "googlecloud"},
        'Heroku Agent': {'mode': True, 'id': "heroku"},
    }

    # Create AVAILABLE_MODELS as a list with just the model aliases (no "BLACKBOXAI/" prefix)
    AVAILABLE_MODELS = list(models)


    def __init__(
        self
    ):
        """
        Initialize the BlackboxAI provider with OpenAI compatibility.
        """
        # Initialize session
        self.session = requests.Session()
        # Remove any proxy configuration to avoid connection issues
        self.session.proxies = {}

        # Set headers based on GitHub reference
        self.headers = {
            'Accept': 'text/event-stream',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Origin': 'https://www.blackbox.ai',
            'Referer': 'https://www.blackbox.ai/',
            'Sec-CH-UA': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': agent.random(),
        }

        # Set cookies for the session
        self.cookies = {
            'cfzs_amplitude': self.generate_id(32),
            'cfz_amplitude': self.generate_id(32),
            '__cf_bm': self.generate_id(32),
        }

        # Initialize chat interface with completions
        self.chat = Chat(self)

    @property
    def models(self):
        class _ModelList:
            def list(inner_self):
                return type(self).AVAILABLE_MODELS
        return _ModelList()


    @classmethod
    def get_model(cls, model: str) -> str:
        """Return the model name, removing BLACKBOXAI/ prefix if present, or default_model."""
        if model.startswith("BLACKBOXAI/"):
            model = model[len("BLACKBOXAI/"):]
        if model in cls.AVAILABLE_MODELS:
            return model
        return cls.default_model

    @classmethod
    def generate_random_string(cls, length: int = 8) -> str:
        """Generate a random string of specified length."""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @classmethod
    def generate_id(cls, length: int = 7) -> str:
        """Generate a random ID of specified length."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @classmethod
    def generate_session(cls, email: str, id_length: int = 21, days_ahead: int = 30) -> dict:
        """
        Generate a dynamic session with proper ID and expiry format using a specific email.

        Args:
            email: The email to use for this session
            id_length: Length of the numeric ID (default: 21)
            days_ahead: Number of days ahead for expiry (default: 30)

        Returns:
            dict: A session dictionary with user information and expiry
        """
        # Generate a random name
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Skyler", "Dakota"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"

        # Generate numeric ID - using Google-like ID format
        numeric_id = ''.join(random.choice('0123456789') for _ in range(id_length))

        # Generate future expiry date
        future_date = datetime.now() + timedelta(days=days_ahead)
        expiry = future_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        # Generate random image ID for the new URL format
        chars = string.ascii_letters + string.digits + "-"
        random_img_id = ''.join(random.choice(chars) for _ in range(48))
        image_url = f"https://lh3.googleusercontent.com/a/ACg8oc{random_img_id}=s96-c"

        return {
            "user": {
                "name": name,
                "email": email,
                "image": image_url,
                "id": numeric_id
            },
            "expires": expiry,
            "isNewUser": False
        }

    def create_request_payload(
        self,
        messages: List[Dict[str, Any]],
        chat_id: str,
        system_message: str,
        max_tokens: int,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        session_data: Dict[str, Any] = None,
        model: str = None
    ) -> Dict[str, Any]:
        """Create the full request payload for the BlackboxAI API."""
        # Get the correct model ID and agent mode
        model_name = self.get_model(model or self.default_model)
        agent_mode = self.agentMode.get(model_name, {})

        # Generate a random customer ID for the subscription
        customer_id = "cus_" + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(14))

        # Create the full request payload
        return {
            "messages": messages,
            "agentMode": agent_mode,
            "id": chat_id,
            "previewToken": None,
            "userId": None,
            "codeModelMode": True,
            "trendingAgentMode": {},
            "isMicMode": False,
            "userSystemPrompt": system_message,
            "maxTokens": max_tokens,
            "playgroundTopP": top_p,
            "playgroundTemperature": temperature,
            "isChromeExt": False,
            "githubToken": "",
            "clickedAnswer2": False,
            "clickedAnswer3": False,
            "clickedForceWebSearch": False,
            "visitFromDelta": False,
            "isMemoryEnabled": False,
            "mobileClient": False,
            "userSelectedModel": model_name if model_name in self.userSelectedModel else None,
            "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94",
            "imageGenerationMode": False,
            "webSearchModePrompt": False,
            "deepSearchMode": False,
            "designerMode": False,
            "domains": None,
            "vscodeClient": False,
            "codeInterpreterMode": False,
            "customProfile": {
                "name": "",
                "occupation": "",
                "traits": [],
                "additionalInfo": "",
                "enableNewChats": False
            },
            "webSearchModeOption": {
                "autoMode": True,
                "webMode": False,
                "offlineMode": False
            },
            "session": session_data,
            "isPremium": True,
            "subscriptionCache": {
                "status": "PREMIUM",
                "customerId": customer_id,
                "expiryTimestamp": int((datetime.now() + timedelta(days=30)).timestamp()),
                "lastChecked": int(datetime.now().timestamp() * 1000),
                "isTrialSubscription": True
            },
            "beastMode": False,
            "reasoningMode": False,
            "designerMode": False,
            "workspaceId": ""
        }
if __name__ == "__main__":
    # Example usage
    client = BLACKBOXAI()
    response = client.chat.completions.create(
        model="GPT-4.1",
        messages=[{"role": "user", "content": "Tell me about india in points"}],
        stream=True
    )
    for chunk in response:
        print(chunk.choices[0].delta.content, end='', flush=True)
