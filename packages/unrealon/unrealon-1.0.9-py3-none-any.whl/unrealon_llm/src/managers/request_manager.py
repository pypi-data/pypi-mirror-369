"""
Request Manager

Manages HTTP requests to LLM providers with retry logic and error handling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

import aiohttp

from unrealon_llm.src.dto import (
    ChatMessage,
    LLMConfig,
    LLMProvider,
    LLMResponse,
    MessageRole,
    TokenUsage,
)
from unrealon_llm.src.exceptions import (
    APIError,
    AuthenticationError,
    MissingAPIKeyError,
    ModelUnavailableError,
    NetworkError,
    RateLimitError,
    wrap_api_error,
)
from unrealon_llm.src.utils.data_extractor import safe_extract_json

logger = logging.getLogger(__name__)


class RequestManager:
    """HTTP request manager for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Provider URLs
        self.provider_urls = {
            LLMProvider.OPENROUTER: "https://openrouter.ai/api/v1/chat/completions",
            LLMProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
            LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def execute_with_retry(
        self,
        provider: LLMProvider,
        messages: List[ChatMessage],
        model: str,
        max_tokens: Optional[int],
        temperature: float,
        response_format: Optional[str],
        **kwargs
    ) -> LLMResponse:
        """Execute request with retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._execute_request(
                    provider, messages, model, max_tokens, temperature, response_format, **kwargs
                )
            except RateLimitError as e:
                last_error = e
                if attempt < self.config.max_retries:
                    # Wait before retry (exponential backoff)
                    wait_time = (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    continue
                raise e
            except (NetworkError, APIError) as e:
                last_error = e
                if attempt < self.config.max_retries:
                    wait_time = (2 ** attempt)
                    logger.warning(f"Request failed, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise e
        
        # If we get here, all retries failed
        raise last_error
    
    async def _execute_request(
        self,
        provider: LLMProvider,
        messages: List[ChatMessage],
        model: str,
        max_tokens: Optional[int],
        temperature: float,
        response_format: Optional[str],
        **kwargs
    ) -> LLMResponse:
        """Execute actual HTTP request to provider"""
        await self._ensure_session()
        
        # Get API key for provider
        api_key = self._get_api_key_for_provider(provider)
        if not api_key:
            raise MissingAPIKeyError(provider.value)
        
        # Extract response_model before building payload (don't send to API)
        response_model = kwargs.pop('response_model', None)
        if not response_model:
            raise ValueError("response_model is required for LLM requests")
        
        # Build request payload
        payload = self._build_request_payload(
            provider, messages, model, max_tokens, temperature, response_format, **kwargs
        )
        
        # Build headers
        headers = self._build_headers(provider, api_key)
        
        # Get provider URL
        url = self.provider_urls[provider]
        
        start_time = datetime.now()
        
        try:
            async with self._session.post(url, json=payload, headers=headers) as response:
                response_data = await response.json()
                
                # Handle errors
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status == 404:
                    raise ModelUnavailableError(model)
                elif response.status >= 400:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    raise APIError(f"Provider error: {error_msg}")
                
                response.raise_for_status()
                
                # Parse response
                return self._parse_response(provider, response_data, model, start_time, response_model)
                
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")
    
    def _build_request_payload(
        self,
        provider: LLMProvider,
        messages: List[ChatMessage],
        model: str,
        max_tokens: Optional[int],
        temperature: float,
        response_format: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Build request payload for provider"""
        payload = {
            "model": model,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Convert messages to provider format
        if provider == LLMProvider.ANTHROPIC:
            # Anthropic uses different message format
            payload["messages"] = [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages if msg.role != MessageRole.SYSTEM
            ]
            
            # System message goes in separate field
            system_messages = [msg.content for msg in messages if msg.role == MessageRole.SYSTEM]
            if system_messages:
                payload["system"] = system_messages[0]
        else:
            # OpenAI/OpenRouter format
            payload["messages"] = [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages
            ]
        
        # Add response format if specified
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        
        # Add any additional parameters
        payload.update(kwargs)
        
        return payload
    
    def _build_headers(self, provider: LLMProvider, api_key: str) -> Dict[str, str]:
        """Build headers for provider"""
        headers = {
            "Content-Type": "application/json",
        }
        
        if provider == LLMProvider.ANTHROPIC:
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    def _parse_response(
        self,
        provider: LLMProvider,
        response_data: Dict[str, Any],
        model: str,
        start_time: datetime,
        response_model: Type[BaseModel]
    ) -> LLMResponse:
        """Parse provider response to LLMResponse"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if provider == LLMProvider.ANTHROPIC:
            # Anthropic response format
            content = response_data.get("content", [{}])[0].get("text", "")
            usage = response_data.get("usage", {})
            
            token_usage = TokenUsage(
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            )
        else:
            # OpenAI/OpenRouter format
            choice = response_data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            usage = response_data.get("usage", {})
            
            token_usage = TokenUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )
        
        # Safe model extraction with response model validation - COMPLIANT with LLM_REQUIREMENTS.md
        try:
            # Always validate with provided response model and return model instance
            extracted_model = safe_extract_json(content, expected_schema=response_model)
        except Exception as e:
            # If validation fails, create empty model instance
            extracted_model = response_model()
        
        return LLMResponse(
            id=response_data.get("id", f"llm_{int(datetime.now().timestamp())}"),
            model=model,
            content=content,
            finish_reason=response_data.get("choices", [{}])[0].get("finish_reason"),
            processing_time_seconds=processing_time,
            token_usage=token_usage,
            extracted_model=extracted_model
        )
    
    def get_provider_for_model(self, model: str) -> LLMProvider:
        """Determine provider from model name"""
        if model.startswith("claude"):
            return LLMProvider.ANTHROPIC
        elif model.startswith("gpt"):
            return LLMProvider.OPENAI
        else:
            return LLMProvider.OPENROUTER  # Default to OpenRouter
    
    def _get_api_key_for_provider(self, provider: LLMProvider) -> Optional[str]:
        """Get API key for provider"""
        if provider == LLMProvider.OPENROUTER:
            return self.config.openrouter_api_key
        elif provider == LLMProvider.OPENAI:
            return self.config.openai_api_key
        elif provider == LLMProvider.ANTHROPIC:
            return self.config.anthropic_api_key
        return None
