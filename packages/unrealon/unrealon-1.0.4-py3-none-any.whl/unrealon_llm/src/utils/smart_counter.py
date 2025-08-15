"""
Smart Token Counter

Intelligent token counting and cost estimation using ModelsCache.
Combines pure token counting with live model data.
"""

import logging
from typing import List, Optional, Tuple

from unrealon_llm.src.dto import ChatMessage
from unrealon_llm.src.exceptions import ValidationError
from unrealon_llm.src.utils.models_cache import ModelsCache, ModelInfo
from unrealon_llm.src.utils.token_counter import TokenCounter

logger = logging.getLogger(__name__)


class SmartTokenCounter:
    """
    Intelligent token counter with model-aware cost estimation
    """
    
    def __init__(self, models_cache: ModelsCache):
        """
        Initialize smart counter
        
        Args:
            models_cache: Models cache for pricing information
        """
        self.models_cache = models_cache
        self.token_counter = TokenCounter()
    
    async def count_and_estimate(
        self, 
        text: str, 
        model: str,
        estimated_output_tokens: int = 0
    ) -> Tuple[int, float]:
        """
        Count tokens and estimate cost
        
        Args:
            text: Input text
            model: Model name
            estimated_output_tokens: Expected output tokens
            
        Returns:
            Tuple of (input_tokens, estimated_cost_usd)
        """
        # Count input tokens
        input_tokens = self.token_counter.count_tokens(text, model)
        
        # Get model info for cost estimation
        if self.models_cache:
            await self.models_cache.fetch_all_models()
            model_info = self.models_cache.get_model(model)
        else:
            model_info = None
        
        if model_info:
            cost = model_info.estimate_cost(input_tokens, estimated_output_tokens)
        else:
            # Fallback estimation
            cost = self._fallback_cost_estimation(input_tokens, estimated_output_tokens)
            logger.warning(f"Model {model} not found in cache, using fallback pricing")
        
        return input_tokens, cost
    
    async def count_messages_and_estimate(
        self,
        messages: List[ChatMessage],
        model: str,
        estimated_output_tokens: int = 0
    ) -> Tuple[int, float]:
        """
        Count message tokens and estimate cost
        
        Args:
            messages: Chat messages
            model: Model name
            estimated_output_tokens: Expected output tokens
            
        Returns:
            Tuple of (total_tokens, estimated_cost_usd)
        """
        # Count tokens including message overhead
        total_tokens = self.token_counter.count_message_tokens(messages, model)
        
        # Get model info for cost estimation
        if self.models_cache:
            await self.models_cache.fetch_all_models()
            model_info = self.models_cache.get_model(model)
        else:
            model_info = None
        
        if model_info:
            cost = model_info.estimate_cost(total_tokens, estimated_output_tokens)
        else:
            # Fallback estimation
            cost = self._fallback_cost_estimation(total_tokens, estimated_output_tokens)
            logger.warning(f"Model {model} not found in cache, using fallback pricing")
        
        return total_tokens, cost
    
    async def optimize_for_budget(
        self,
        text: str,
        model: str,
        max_cost_usd: float,
        estimated_output_tokens: int = 0
    ) -> str:
        """
        Optimize text to fit within budget
        
        Args:
            text: Input text
            model: Model name
            max_cost_usd: Maximum allowed cost
            estimated_output_tokens: Expected output tokens
            
        Returns:
            Optimized text that fits budget
        """
        # Get model pricing - first fetch models, then get model info
        if self.models_cache:
            await self.models_cache.fetch_all_models()
            model_info = self.models_cache.get_model(model)
        else:
            model_info = None
            
        if not model_info:
            logger.warning(f"Model {model} not found, using fallback optimization")
            return self.token_counter.optimize_text_for_tokens(text, 1000, model)
        
        # Calculate max input tokens for budget
        output_cost = (estimated_output_tokens / 1_000_000) * model_info.completion_price
        remaining_budget = max_cost_usd - output_cost
        
        if remaining_budget <= 0:
            raise ValidationError("Budget too low even for output tokens")
        
        max_input_tokens = int((remaining_budget / model_info.prompt_price) * 1_000_000)
        
        # Optimize text for token limit
        return self.token_counter.optimize_text_for_tokens(text, max_input_tokens, model)
    
    async def get_model_context_limit(self, model: str) -> Optional[int]:
        """Get context length limit for model"""
        if self.models_cache:
            await self.models_cache.fetch_all_models()
            model_info = self.models_cache.get_model(model)
            return model_info.context_length if model_info else None
        return None
    
    async def suggest_cheaper_alternative(
        self,
        current_model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Optional[Tuple[str, float, float]]:
        """
        Suggest cheaper model alternative
        
        Returns:
            Tuple of (model_name, current_cost, suggested_cost) or None
        """
        if self.models_cache:
            await self.models_cache.fetch_all_models()
            current_info = self.models_cache.get_model(current_model)
        else:
            current_info = None
            
        if not current_info:
            return None
        
        current_cost = current_info.estimate_cost(input_tokens, output_tokens)
        
        # Find cheaper models with similar context length
        min_context = min(current_info.context_length, input_tokens + output_tokens)
        
        # Note: get_budget_models is not an async method, let's check if models_cache has this method
        # For now, we'll implement a simple fallback
        budget_models = []
        if self.models_cache:
            # Find models with lower pricing
            all_models = list(self.models_cache.models.values())
            max_price = current_info.prompt_price * 0.8  # 20% cheaper
            budget_models = [
                m for m in all_models 
                if m.prompt_price <= max_price and m.context_length >= min_context and m.is_available
            ]
        
        for model_info in budget_models:
            if model_info.context_length >= min_context:
                suggested_cost = model_info.estimate_cost(input_tokens, output_tokens)
                if suggested_cost < current_cost:
                    return model_info.id, current_cost, suggested_cost
        
        return None
    
    def _fallback_cost_estimation(self, input_tokens: int, output_tokens: int) -> float:
        """Fallback cost estimation when model not found"""
        # Conservative estimation: $0.002 per 1K tokens (GPT-3.5-turbo-like pricing)
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * 0.002


# Convenience functions for backward compatibility
async def smart_count_tokens(
    text: str, 
    model: str, 
    models_cache: ModelsCache,
    estimate_output: int = 0
) -> Tuple[int, float]:
    """Quick smart token counting with cost estimation"""
    counter = SmartTokenCounter(models_cache)
    return await counter.count_and_estimate(text, model, estimate_output)


async def smart_count_messages(
    messages: List[ChatMessage],
    model: str,
    models_cache: ModelsCache,
    estimate_output: int = 0
) -> Tuple[int, float]:
    """Quick smart message counting with cost estimation"""
    counter = SmartTokenCounter(models_cache)
    return await counter.count_messages_and_estimate(messages, model, estimate_output)
