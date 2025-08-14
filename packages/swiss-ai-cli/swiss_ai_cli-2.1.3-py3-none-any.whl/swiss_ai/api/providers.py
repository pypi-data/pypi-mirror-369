#!/usr/bin/env python3
"""
Provider adapters for Swiss AI CLI
Implements a pluggable interface for different model API providers.
"""

from __future__ import annotations

import os
import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, AsyncGenerator

import aiohttp
import json

logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    success: bool
    content: str
    model_used: str
    usage: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error: Optional[str] = None


class BaseProvider:
    name: str = "base"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> ProviderResponse:  # pragma: no cover - interface
        raise NotImplementedError
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:  # pragma: no cover - interface
        """Stream chat completion chunks - fallback implementation"""
        # Fallback: get complete response and yield it as one chunk
        resp = await self.chat_completion(messages, model, temperature, max_tokens, stream=False)
        if resp.success:
            yield resp.content


class OpenRouterProvider(BaseProvider):
    name = "openrouter"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("openrouter_api_key")
        )
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> ProviderResponse:
        if not self.api_key:
            return ProviderResponse(False, "No OpenRouter API key configured", model, error="Missing API key")

        await self._ensure_session()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://swiss-ai-cli.dev",
            "X-Title": "Swiss AI CLI",
            # Allow provider override via header for OpenRouter multi-provider routing
            # When SWISS_AI_FORCE_PROVIDER is set, pass it through so OR can choose proper backend
            **({"X-Provider": os.getenv("SWISS_AI_FORCE_PROVIDER")} if os.getenv("SWISS_AI_FORCE_PROVIDER") else {}),
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            # Respect OpenRouter provider hints when model ids are vendor-prefixed
            # e.g., "openai/gpt-4o" or "anthropic/claude-3.7"
            # OpenRouter will route based on model, but header hint is also included above.
        }

        start_time = asyncio.get_event_loop().time()
        try:
            assert self._session is not None
            async with self._session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                elapsed = asyncio.get_event_loop().time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if data.get("choices"):
                        content = data["choices"][0]["message"]["content"]
                        return ProviderResponse(True, content, model, usage=data.get("usage", {}), execution_time=elapsed)
                    return ProviderResponse(False, "No response content", model, execution_time=elapsed, error="Empty response")
                error_text = await response.text()
                logger.error(f"OpenRouter error {response.status}: {error_text}")
                return ProviderResponse(False, f"API Error: {response.status}", model, execution_time=elapsed, error=error_text)
        except asyncio.TimeoutError:
            return ProviderResponse(False, "Request timed out", model, execution_time=30.0, error="Timeout")
        except Exception as e:
            logger.error(f"OpenRouter client error: {e}")
            elapsed = asyncio.get_event_loop().time() - start_time
            return ProviderResponse(False, f"Error: {e}", model, execution_time=elapsed, error=str(e))
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion chunks"""
        if self._session is None:
            await self._ensure_session()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://swiss-ai.dev",
            "X-Title": "Swiss AI CLI",
            **({"X-Provider": os.getenv("SWISS_AI_FORCE_PROVIDER")} if os.getenv("SWISS_AI_FORCE_PROVIDER") else {}),
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            assert self._session is not None
            async with self._session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"OpenRouter streaming error {response.status}: {error_text}")
                    return

                # Read line by line from the streaming response
                buffer = ""
                async for chunk in response.content.iter_any():
                    buffer += chunk.decode('utf-8')
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            if data_str == '[DONE]':
                                return
                            try:
                                chunk_data = json.loads(data_str)
                                if chunk_data.get("choices") and len(chunk_data["choices"]) > 0:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue  # Skip invalid JSON chunks
        except Exception as e:
            logger.error(f"OpenRouter streaming error: {e}")
            return


class GoogleAIProvider(BaseProvider):
    name = "googleai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY".lower())
        try:
            import google.generativeai as genai  # type: ignore

            self._genai = genai
        except Exception:  # pragma: no cover - optional
            self._genai = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> ProviderResponse:
        if self._genai is None:
            return ProviderResponse(False, "google-generativeai not installed", model, error="Missing dependency: google-generativeai")
        if not self.api_key:
            return ProviderResponse(False, "No Google API key configured", model, error="Missing API key")

        # Combine messages into a single prompt; Google API varies by SDK version
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        user_parts = [m["content"] for m in messages if m.get("role") == "user"]
        prompt = "\n\n".join(system_parts + user_parts)

        try:
            self._genai.configure(api_key=self.api_key)
            model_obj = self._genai.GenerativeModel(model)
            # Google SDK is sync; run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            start_time = loop.time()
            def _invoke():
                return model_obj.generate_content(prompt, generation_config={"temperature": temperature, "max_output_tokens": max_tokens})
            resp = await loop.run_in_executor(None, _invoke)
            elapsed = loop.time() - start_time
            text = getattr(resp, "text", None) or (resp.candidates[0].content.parts[0].text if getattr(resp, "candidates", None) else "")
            if not text:
                return ProviderResponse(False, "Empty response", model, execution_time=elapsed, error="Empty response")
            return ProviderResponse(True, text, model, execution_time=elapsed)
        except Exception as e:  # pragma: no cover - depends on SDK
            logger.error(f"GoogleAI error: {e}")
            return ProviderResponse(False, f"Error: {e}", model, error=str(e))


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("anthropic_api_key")
        try:
            import anthropic  # type: ignore

            self._anthropic = anthropic
        except Exception:  # pragma: no cover - optional
            self._anthropic = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> ProviderResponse:
        if self._anthropic is None:
            return ProviderResponse(False, "anthropic not installed", model, error="Missing dependency: anthropic")
        if not self.api_key:
            return ProviderResponse(False, "No Anthropic API key configured", model, error="Missing API key")

        try:
            client = self._anthropic.Anthropic(api_key=self.api_key)
            # Map messages to Anthropic's message format
            sys_msgs = [m["content"] for m in messages if m.get("role") == "system"]
            user_msgs = [m for m in messages if m.get("role") in ("user", "assistant")]
            system_prompt = "\n\n".join(sys_msgs) if sys_msgs else None
            start_time = asyncio.get_event_loop().time()
            resp = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.messages.create(
                    model=model,
                    system=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": m["role"], "content": m["content"]} for m in user_msgs],
                ),
            )
            elapsed = asyncio.get_event_loop().time() - start_time
            content = "".join(part.text for part in (resp.content or []) if getattr(part, "type", "text") == "text")
            if not content:
                return ProviderResponse(False, "Empty response", model, execution_time=elapsed, error="Empty response")
            return ProviderResponse(True, content, model, execution_time=elapsed)
        except Exception as e:  # pragma: no cover - depends on SDK
            logger.error(f"Anthropic error: {e}")
            return ProviderResponse(False, f"Error: {e}", model, error=str(e))


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key")
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> ProviderResponse:
        if not self.api_key:
            return ProviderResponse(False, "No OpenAI API key configured", model, error="Missing API key")

        await self._ensure_session()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model.replace("openai/", ""),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        start_time = asyncio.get_event_loop().time()
        try:
            assert self._session is not None
            async with self._session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                elapsed = asyncio.get_event_loop().time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if data.get("choices"):
                        content = data["choices"][0]["message"]["content"]
                        return ProviderResponse(True, content, model, usage=data.get("usage", {}), execution_time=elapsed)
                    return ProviderResponse(False, "No response content", model, execution_time=elapsed, error="Empty response")
                error_text = await response.text()
                logger.error(f"OpenAI error {response.status}: {error_text}")
                return ProviderResponse(False, f"API Error: {response.status}", model, execution_time=elapsed, error=error_text)
        except asyncio.TimeoutError:
            return ProviderResponse(False, "Request timed out", model, execution_time=30.0, error="Timeout")
        except Exception as e:
            logger.error(f"OpenAI client error: {e}")
            elapsed = asyncio.get_event_loop().time() - start_time
            return ProviderResponse(False, f"Error: {e}", model, execution_time=elapsed, error=str(e))


class XAIProvider(BaseProvider):
    name = "xai"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.x.ai"):
        self.api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("xai_api_key")
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> ProviderResponse:
        if not self.api_key:
            return ProviderResponse(False, "No xAI API key configured", model, error="Missing API key")

        await self._ensure_session()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model.replace("xai/", ""),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        start_time = asyncio.get_event_loop().time()
        try:
            assert self._session is not None
            async with self._session.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                elapsed = asyncio.get_event_loop().time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if data.get("choices"):
                        content = data["choices"][0]["message"]["content"]
                        return ProviderResponse(True, content, model, usage=data.get("usage", {}), execution_time=elapsed)
                    return ProviderResponse(False, "No response content", model, execution_time=elapsed, error="Empty response")
                error_text = await response.text()
                logger.error(f"xAI error {response.status}: {error_text}")
                return ProviderResponse(False, f"API Error: {response.status}", model, execution_time=elapsed, error=error_text)
        except asyncio.TimeoutError:
            return ProviderResponse(False, "Request timed out", model, execution_time=30.0, error="Timeout")
        except Exception as e:
            logger.error(f"xAI client error: {e}")
            elapsed = asyncio.get_event_loop().time() - start_time
            return ProviderResponse(False, f"Error: {e}", model, execution_time=elapsed, error=str(e))


def infer_provider_from_model(model_id: str) -> str:
    """Infer provider by model id prefix for convenience."""
    if model_id.startswith("openai/") or model_id.startswith("gpt-"):
        return "openai"
    if model_id.startswith("google/"):
        return "googleai"
    if model_id.startswith("anthropic/") or model_id.startswith("claude"):
        return "anthropic"
    if model_id.startswith("moonshot/") or "kimi-k2" in model_id:
        # Kimi often sits behind OpenRouter; keep through openrouter unless direct API added
        return "openrouter"
    if model_id.startswith("qwen/") or model_id.startswith("qwq-"):
        # Many qwen models are available via OpenRouter; default there
        return "openrouter"
    if model_id.startswith("xai/") or model_id.startswith("grok"):
        return "xai"
    # Default: go through OpenRouter which proxies many providers
    return "openrouter"


