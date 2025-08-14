#!/usr/bin/env python3
"""
OpenRouter API Client for Swiss AI CLI
Handles actual AI model API calls
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass
from ..models.selector import ModelInfo
from ..models.aliases import normalize_model_id
from .providers import (
    ProviderResponse,
    BaseProvider,
    OpenRouterProvider,
    GoogleAIProvider,
    AnthropicProvider,
    OpenAIProvider,
    XAIProvider,
    infer_provider_from_model,
)

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Response from API call"""
    success: bool
    content: str
    model_used: str
    usage: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error: Optional[str] = None

class OpenRouterClient:
    """Deprecated direct OpenRouter client (kept for compatibility)."""
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1"):
        self._provider = OpenRouterProvider(api_key=api_key, base_url=base_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._provider.close()

    async def chat_completion(self, messages: List[Dict[str, str]], model: str, temperature: float = 0.1, max_tokens: int = 4096, stream: bool = False) -> APIResponse:
        r = await self._provider.chat_completion(messages, model, temperature, max_tokens, stream)
        return APIResponse(r.success, r.content, r.model_used, r.usage, r.execution_time, r.error)

    async def simple_completion(self, prompt: str, model: str, **kwargs) -> APIResponse:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model, **kwargs)

class ExaSearchClient:
    """Client for Exa search integration via MCP"""
    
    def __init__(self):
        self.console = None  # Will be set if available
    
    async def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web using Exa (currently disabled)"""
        # Exa integration temporarily disabled
        return {
            "success": False,
            "error": "Exa search temporarily unavailable",
            "source": "exa_web_search"
        }
    
    async def research_company(self, company_name: str, num_results: int = 3) -> Dict[str, Any]:
        """Research a company using Exa (currently disabled)"""
        # Exa integration temporarily disabled
        return {
            "success": False,
            "error": "Exa company research temporarily unavailable",
            "source": "exa_company_research"
        }

class SwissAIAPIClient:
    """Main API client that combines OpenRouter and Exa functionality"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        # Provider instances (lazy)
        self._providers: Dict[str, BaseProvider] = {}
        self.exa = ExaSearchClient()

    def _normalize_model_id(self, model: str) -> str:
        return normalize_model_id(model)

    def _get_provider(self, provider_hint: Optional[str]) -> BaseProvider:
        name = provider_hint or os.getenv("SWISS_AI_PROVIDER") or "openrouter"
        if name not in self._providers:
            if name == "googleai":
                self._providers[name] = GoogleAIProvider()
            elif name == "anthropic":
                self._providers[name] = AnthropicProvider()
            elif name == "openai":
                self._providers[name] = OpenAIProvider()
            elif name == "xai":
                self._providers[name] = XAIProvider()
            else:
                # Fallback to OpenRouter (default)
                self._providers[name] = OpenRouterProvider()
        return self._providers[name]
    
    async def chat_with_model(
        self, 
        user_input: str, 
        model: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """Chat with a model, optionally including web search context"""
        model = self._normalize_model_id(model)
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context if available
        if context:
            messages.append({"role": "system", "content": f"Additional context:\n{context}"})
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Determine provider: explicit override or inferred from model id
        provider_name = os.getenv("SWISS_AI_FORCE_PROVIDER") or infer_provider_from_model(model)
        provider = self._get_provider(provider_name)
        resp: ProviderResponse = await provider.chat_completion(messages, model, **kwargs)
        return APIResponse(resp.success, resp.content, resp.model_used, resp.usage, resp.execution_time, resp.error)
    
    async def simple_chat(self, prompt: str, model: str, **kwargs) -> APIResponse:
        """Simple chat method"""
        model = self._normalize_model_id(model)
        provider_name = os.getenv("SWISS_AI_FORCE_PROVIDER") or infer_provider_from_model(model)
        provider = self._get_provider(provider_name)
        messages = [{"role": "user", "content": prompt}]
        resp: ProviderResponse = await provider.chat_completion(messages, model, **kwargs)
        return APIResponse(resp.success, resp.content, resp.model_used, resp.usage, resp.execution_time, resp.error)
    
    async def simple_chat_stream(self, prompt: str, model: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        """Simple streaming chat method"""
        model = self._normalize_model_id(model)
        provider_name = os.getenv("SWISS_AI_FORCE_PROVIDER") or infer_provider_from_model(model)
        provider = self._get_provider(provider_name)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async for chunk in provider.chat_completion_stream(messages, model, **kwargs):
                yield chunk
        except NotImplementedError:
            # Fallback to non-streaming if provider doesn't support streaming
            resp: ProviderResponse = await provider.chat_completion(messages, model, **kwargs)
            if resp.success:
                yield resp.content
    
    async def search_and_summarize(self, query: str, model: str) -> APIResponse:
        """Search the web and summarize results"""
        try:
            # Get search results
            search_results = await self.exa.search_web(query, num_results=5)
            
            if not search_results.get("success"):
                return APIResponse(
                    success=False,
                    content=f"Search failed: {search_results.get('error', 'Unknown error')}",
                    model_used=model,
                    error="Search failed"
                )
            
            # Prepare context for summarization
            context = "Search results to summarize:\n\n"
            for i, result in enumerate(search_results.get("results", []), 1):
                if isinstance(result, dict):
                    title = result.get("title", "No title")
                    content = result.get("text", result.get("content", "No content"))[:500]
                    url = result.get("url", "No URL")
                    context += f"{i}. {title}\nURL: {url}\nContent: {content}...\n\n"
            
            # Ask model to summarize
            prompt = f"Please provide a comprehensive summary of these search results for the query '{query}':\n\n{context}"
            
            async with self.openrouter as client:
                return await client.simple_completion(prompt, self._normalize_model_id(model), max_tokens=2048)
                
        except Exception as e:
            logger.error(f"Search and summarize error: {e}")
            return APIResponse(
                success=False,
                content=f"Error during search and summarize: {str(e)}",
                model_used=model,
                error=str(e)
            )