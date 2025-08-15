"""
Smart LLM Client

Simplified and modular LLM client using manager components.
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from unrealon_llm.src.dto import (
    ChatMessage,
    LLMConfig,
    LLMResponse,
    MessageRole,
)
from unrealon_llm.src.exceptions import (
    APIError,
    CostLimitExceededError,
    TokenLimitExceededError,
    ValidationError,
)
from unrealon_llm.src.llm_logging import get_llm_logger, LLMEventType
from unrealon_llm.src.managers import CacheManager, CostManager, RequestManager
from unrealon_llm.src.utils import generate_correlation_id, extract_llm_response_data
from unrealon_llm.src.utils.models_cache import get_models_cache
from unrealon_llm.src.utils.smart_counter import SmartTokenCounter
from unrealon_sdk.src.dto.logging import SDKContext, SDKEventType

logger = logging.getLogger(__name__)


class SmartLLMClient:
    """
    Simplified LLM client with modular manager components
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize smart LLM client
        
        Args:
            config: LLM configuration
        """
        self.config = config
        
        # Get LLM logger
        self.llm_logger = get_llm_logger()
        
        # Initialize models cache
        self.models_cache = get_models_cache(
            openrouter_api_key=config.openrouter_api_key,
            openai_api_key=config.openai_api_key,
            anthropic_api_key=config.anthropic_api_key
        )
        
        # Initialize managers
        self.cost_manager = CostManager(config.daily_cost_limit_usd)
        
        cache_ttl = config.cache_ttl_hours * 3600
        cache_size = config.max_cache_size_mb * 10  # Approximate conversion
        self.cache_manager = CacheManager(max_size=cache_size, ttl_seconds=cache_ttl)
        self.cache_manager.set_enabled(config.enable_global_cache)
        
        self.request_manager = RequestManager(config)
        
        # Token counter
        self.smart_counter = SmartTokenCounter(self.models_cache)
        
        # Log initialization
        if self.llm_logger:
            self.llm_logger._dev_logger.log_info(
                LLMEventType.LLM_CLIENT_INITIALIZED,
                f"Smart LLM Client initialized with {config.default_model}",
                context=SDKContext(
                    component_name="SmartLLMClient",
                    layer_name="UnrealOn_LLM"
                ),
                details={"model": config.default_model}
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.request_manager._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.request_manager.close()
    
    async def close(self):
        """Close client resources"""
        await self.request_manager.close()
    
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.1,
        response_format: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute chat completion with managers
        
        Args:
            messages: Chat messages
            model: Model to use (defaults to config default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            response_format: Response format ("json" for JSON)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM response with metadata
            
        Raises:
            Various LLM exceptions based on failure type
        """
        # Use default model if not specified
        if model is None:
            model = self.config.default_model
        
        # Validate inputs
        if not messages:
            raise ValidationError("Messages list cannot be empty")
        
        # Smart count and cost estimation
        estimated_output_tokens = max_tokens or 500
        input_tokens, estimated_cost = await self.smart_counter.count_messages_and_estimate(
            messages, model, estimated_output_tokens
        )
        
        # Check token limits
        context_limit = await self.smart_counter.get_model_context_limit(model)
        if context_limit and input_tokens > context_limit:
            raise TokenLimitExceededError(input_tokens, context_limit)
        
        # Check cost limits
        if not self.cost_manager.can_afford(estimated_cost):
            raise CostLimitExceededError(
                self.cost_manager.total_cost + Decimal(str(estimated_cost)),
                self.cost_manager.daily_limit
            )
        
        # Check cache
        cache_key = self.cache_manager.generate_cache_key(messages, model, temperature, response_format)
        cached_response = self.cache_manager.get(cache_key)
        
        if cached_response:
            # Log cache hit
            if self.llm_logger:
                provider = self.request_manager.get_provider_for_model(model)
                self.llm_logger.log_llm_request_completed(
                    provider=provider.value,
                    model=model,
                    prompt_tokens=input_tokens,
                    completion_tokens=cached_response.token_usage.completion_tokens if cached_response.token_usage else 0,
                    cost_usd=0.0,  # Cached responses are free
                    duration_ms=0.0,  # Cached responses are instant
                    cached=True,
                    details={
                        "cache_key": cache_key[:50],
                        "message_count": len(messages),
                    }
                )
                self.llm_logger.log_cache_operation("hit", cache_key)
            
            logger.debug("Returning cached response")
            return cached_response
        
        # Generate request ID for tracking
        request_id = generate_correlation_id()
        
        # Log request start
        if self.llm_logger:
            provider = self.request_manager.get_provider_for_model(model)
            self.llm_logger.log_llm_request_start(
                provider=provider.value,
                model=model,
                prompt_tokens=input_tokens,
                request_id=request_id,
                details={
                    "message_count": len(messages),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "estimated_cost": estimated_cost,
                }
            )
        
        # Execute request
        start_time = datetime.now()
        
        try:
            # Determine provider from model
            provider = self.request_manager.get_provider_for_model(model)
            
            # Execute request
            response = await self.request_manager.execute_with_retry(
                provider, messages, model, max_tokens, temperature, response_format, **kwargs
            )
            
            # Calculate actual cost and duration
            actual_cost = 0.0
            # Only fetch models if not already cached
            if not self.models_cache.models:
                await self.models_cache.fetch_all_models()
            model_info = self.models_cache.get_model(model)
            if model_info and response.token_usage:
                actual_cost = model_info.estimate_cost(
                    response.token_usage.prompt_tokens,
                    response.token_usage.completion_tokens
                )
                response.cost_usd = actual_cost
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Track cost
            self.cost_manager.track_request(actual_cost, model, "chat_completion", self.llm_logger)
            
            # Log successful completion
            if self.llm_logger:
                self.llm_logger.log_llm_request_completed(
                    provider=provider.value,
                    model=model,
                    prompt_tokens=response.token_usage.prompt_tokens if response.token_usage else input_tokens,
                    completion_tokens=response.token_usage.completion_tokens if response.token_usage else 0,
                    cost_usd=actual_cost,
                    duration_ms=duration_ms,
                    request_id=request_id,
                    cached=False,
                    details={
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "response_length": len(response.content) if response.content else 0,
                    }
                )
            
            # Cache response
            self.cache_manager.store(cache_key, response)
            if self.llm_logger:
                self.llm_logger.log_cache_operation("store", cache_key[:50])
            
            return response
            
        except Exception as e:
            # Log failure
            if self.llm_logger:
                provider = self.request_manager.get_provider_for_model(model)
                self.llm_logger.log_llm_request_failed(
                    provider=provider.value,
                    model=model,
                    error_message=str(e),
                    request_id=request_id,
                    exception=e,
                    details={
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    }
                )
            
            # Re-raise the error
            raise e
    
    async def simple_chat(
        self,
        message: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple chat interface that returns just the response text
        
        Args:
            message: User message
            system_message: Optional system message
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            Response text
        """
        messages = []
        
        if system_message:
            messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_message
            ))
        
        messages.append(ChatMessage(
            role=MessageRole.USER,
            content=message
        ))
        
        response = await self.chat_completion(messages, model=model, **kwargs)
        return response.content
    
    async def json_chat(
        self,
        message: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        expected_schema: Optional[type] = None,
        required_fields: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat interface that returns safely parsed and validated JSON response
        
        Args:
            message: User message
            system_message: Optional system message
            model: Model to use
            expected_schema: Pydantic model class for validation
            required_fields: List of required fields in response
            **kwargs: Additional parameters
            
        Returns:
            Safely parsed and validated JSON response
            
        Raises:
            ResponseParsingError: If response is not valid JSON
            ValidationError: If schema validation fails
        """
        if system_message:
            system_message += "\n\nIMPORTANT: Respond only with valid JSON. Follow the exact structure requested."
        else:
            system_message = "Respond only with valid JSON. Follow the exact structure requested."
        
        response_text = await self.simple_chat(
            message, 
            system_message=system_message,
            model=model,
            response_format="json",
            **kwargs
        )
        
        # Use safe JSON parsing
        validated_response = extract_llm_response_data(
            response_text,
            expected_schema=expected_schema,
            required_fields=required_fields
        )
        
        # Log successful JSON validation
        if self.llm_logger:
            self.llm_logger._dev_logger.log_info(
                SDKEventType.COMMAND_COMPLETED,
                f"JSON response validated successfully",
                context=SDKContext(
                    metadata={
                        "schema_type": expected_schema.__name__ if expected_schema else "untyped",
                        "fields_count": len(validated_response) if isinstance(validated_response, dict) else 0,
                    }
                ),
            )
        
        return validated_response
    
    async def validated_json_chat(
        self,
        message: str,
        schema_class: Type[BaseModel],
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """
        Type-safe JSON chat with full Pydantic validation
        
        Args:
            message: User message
            schema_class: Pydantic model class for strict validation
            system_message: Optional system message
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValidationError: If response doesn't match schema
            ResponseParsingError: If response is not valid JSON
        """
        if system_message:
            system_message += f"\n\nIMPORTANT: Respond only with valid JSON matching this exact schema: {schema_class.__name__}"
        else:
            system_message = f"Respond only with valid JSON matching this exact schema: {schema_class.__name__}"
        
        # Add schema documentation to prompt
        if hasattr(schema_class, 'model_json_schema'):
            schema_doc = schema_class.model_json_schema()
            system_message += f"\n\nSchema:\n{json.dumps(schema_doc, indent=2)}"
        
        response_text = await self.simple_chat(
            message,
            system_message=system_message,
            model=model,
            response_format="json",
            **kwargs
        )
        
        # Use safe parsing with strict Pydantic validation
        validated_instance = extract_llm_response_data(
            response_text,
            expected_schema=schema_class
        )
        
        # Log successful validation
        if self.llm_logger:
            self.llm_logger._dev_logger.log_info(
                SDKEventType.COMMAND_COMPLETED,
                f"Pydantic validation successful: {schema_class.__name__}",
                context=SDKContext(
                    metadata={
                        "schema_type": schema_class.__name__,
                        "fields_count": len(validated_instance.model_fields) if hasattr(validated_instance, 'model_fields') else 0,
                    }
                ),
            )
        
        return validated_instance
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get cost tracking statistics"""
        return self.cost_manager.get_stats()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_manager.get_stats()
