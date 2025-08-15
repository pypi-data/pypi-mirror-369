"""
Models Cache Utilities

Automatically fetch and cache LLM model information with pricing from providers.
Eliminates hardcoding and provides up-to-date model data and pricing.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from cachetools import TTLCache

from unrealon_llm.src.dto import LLMProvider
from unrealon_llm.src.exceptions import APIError, CacheError, ConfigurationError

logger = logging.getLogger(__name__)


class ModelInfo:
    """Model information with pricing and capabilities"""

    def __init__(
        self,
        id: str,
        name: str,
        provider: str,
        context_length: int = 0,
        prompt_price: float = 0.0,
        completion_price: float = 0.0,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_available: bool = True,
        currency: str = "USD",
    ):
        self.id = id
        self.name = name
        self.provider = provider
        self.context_length = context_length
        self.prompt_price = prompt_price  # Price per 1M tokens
        self.completion_price = completion_price  # Price per 1M tokens
        self.description = description or ""
        self.tags = tags or []
        self.is_available = is_available
        self.currency = currency

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for given token usage"""
        input_cost = (input_tokens / 1_000_000) * self.prompt_price
        output_cost = (output_tokens / 1_000_000) * self.completion_price
        return input_cost + output_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "context_length": self.context_length,
            "prompt_price": self.prompt_price,
            "completion_price": self.completion_price,
            "description": self.description,
            "tags": self.tags,
            "is_available": self.is_available,
            "currency": self.currency,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """Create ModelInfo from dictionary"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            provider=data.get("provider", ""),
            context_length=data.get("context_length", 0),
            prompt_price=data.get("prompt_price", 0.0),
            completion_price=data.get("completion_price", 0.0),
            description=data.get("description"),
            tags=data.get("tags", []),
            is_available=data.get("is_available", True),
            currency=data.get("currency", "USD"),
        )


class ModelsCache:
    """
    Automatic models cache with provider integration
    Fetches current model data and pricing from APIs
    """

    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        cache_ttl_hours: int = 24,  # Cache for 24 hours
        max_cache_size: int = 1000,
    ):
        """
        Initialize models cache with provider API keys

        Args:
            openrouter_api_key: OpenRouter API key
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            cache_ttl_hours: Cache TTL in hours
            max_cache_size: Maximum cache entries
        """
        self.openrouter_api_key = openrouter_api_key
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key

        # Initialize cache
        cache_ttl = cache_ttl_hours * 3600  # Convert to seconds
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)

        # Models storage
        self.models: Dict[str, ModelInfo] = {}
        self.last_fetch_time: Optional[datetime] = None

        # Cache keys
        self.MODELS_CACHE_KEY = "all_models"
        self.OPENROUTER_CACHE_KEY = "openrouter_models"
        self.OPENAI_CACHE_KEY = "openai_models"
        self.ANTHROPIC_CACHE_KEY = "anthropic_models"

        # Cache settings
        self.cache_ttl_hours = cache_ttl_hours

        # Provider endpoints
        self.provider_endpoints = {
            "openrouter": "https://openrouter.ai/api/v1/models",
            "openai": "https://api.openai.com/v1/models",
            "anthropic": "https://api.anthropic.com/v1/models",
        }

    async def fetch_all_models(
        self, force_refresh: bool = False
    ) -> Dict[str, ModelInfo]:
        """
        Fetch models from all available providers

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dictionary of model_id -> ModelInfo
        """
        # Quick check - if models already loaded, return them
        if not force_refresh and self.models:
            logger.info(f"🔥 Using already loaded {len(self.models)} models from memory cache")
            return self.models

        # Check cache first
        if not force_refresh and self.MODELS_CACHE_KEY in self.cache:
            logger.info("💾 Using models from TTL cache")
            cached_data = self.cache[self.MODELS_CACHE_KEY]
            self.models = {
                k: ModelInfo.from_dict(v) for k, v in cached_data["models"].items()
            }
            self.last_fetch_time = datetime.fromisoformat(cached_data["fetch_time"])
            return self.models

        logger.info("🌐 Fetching fresh models from all providers (no cache)")

        # Fetch from all available providers
        all_models = {}

        # Fetch OpenRouter models (priority provider)
        if self.openrouter_api_key:
            try:
                openrouter_models = await self._fetch_openrouter_models()
                all_models.update(openrouter_models)
                logger.info(f"Fetched {len(openrouter_models)} models from OpenRouter")
            except Exception as e:
                logger.warning(f"Failed to fetch OpenRouter models: {e}")

        # Fetch OpenAI models
        if self.openai_api_key:
            try:
                openai_models = await self._fetch_openai_models()
                all_models.update(openai_models)
                logger.info(f"Fetched {len(openai_models)} models from OpenAI")
            except Exception as e:
                logger.warning(f"Failed to fetch OpenAI models: {e}")

        # Fetch Anthropic models
        if self.anthropic_api_key:
            try:
                anthropic_models = await self._fetch_anthropic_models()
                all_models.update(anthropic_models)
                logger.info(f"Fetched {len(anthropic_models)} models from Anthropic")
            except Exception as e:
                logger.warning(f"Failed to fetch Anthropic models: {e}")

        # Add fallback models if no providers available
        if not all_models:
            logger.warning("No models fetched from providers, using fallback models")
            all_models = self._get_fallback_models()

        # Update cache
        self.models = all_models
        self.last_fetch_time = datetime.now()

        cache_data = {
            "models": {k: v.to_dict() for k, v in all_models.items()},
            "fetch_time": self.last_fetch_time.isoformat(),
        }
        self.cache[self.MODELS_CACHE_KEY] = cache_data

        logger.info(f"Total models cached: {len(all_models)}")
        return self.models

    async def _fetch_openrouter_models(self) -> Dict[str, ModelInfo]:
        """Fetch models from OpenRouter API"""
        if not self.openrouter_api_key:
            return {}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.provider_endpoints["openrouter"],
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    models = {}
                    for model_data in data.get("data", []):
                        model_info = self._parse_openrouter_model(model_data)
                        if model_info:
                            models[model_info.id] = model_info

                    return models

            except aiohttp.ClientError as e:
                raise APIError(f"OpenRouter API error: {e}")
            except Exception as e:
                raise APIError(f"Failed to fetch OpenRouter models: {e}")

    async def _fetch_openai_models(self) -> Dict[str, ModelInfo]:
        """Fetch models from OpenAI API"""
        if not self.openai_api_key:
            return {}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.provider_endpoints["openai"],
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    models = {}
                    for model_data in data.get("data", []):
                        model_info = self._parse_openai_model(model_data)
                        if model_info:
                            models[model_info.id] = model_info

                    return models

            except aiohttp.ClientError as e:
                raise APIError(f"OpenAI API error: {e}")
            except Exception as e:
                raise APIError(f"Failed to fetch OpenAI models: {e}")

    async def _fetch_anthropic_models(self) -> Dict[str, ModelInfo]:
        """Fetch models from Anthropic API"""
        # Anthropic doesn't provide a public models endpoint yet
        # Return known Anthropic models with approximate pricing
        return {
            "claude-3-opus-20240229": ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider="anthropic",
                context_length=200000,
                prompt_price=15.0,
                completion_price=75.0,
                description="Most powerful Claude 3 model",
                tags=["reasoning", "analysis", "coding"],
            ),
            "claude-3-sonnet-20240229": ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider="anthropic",
                context_length=200000,
                prompt_price=3.0,
                completion_price=15.0,
                description="Balanced Claude 3 model",
                tags=["general", "reasoning", "coding"],
            ),
            "claude-sonnet-4-20240307": ModelInfo(
                id="claude-sonnet-4-20240307",
                name="Claude 3 Haiku",
                provider="anthropic",
                context_length=200000,
                prompt_price=0.25,
                completion_price=1.25,
                description="Fastest Claude 3 model",
                tags=["speed", "general", "cost-effective"],
            ),
        }

    def _parse_openrouter_model(
        self, model_data: Dict[str, Any]
    ) -> Optional[ModelInfo]:
        """Parse OpenRouter model data"""
        try:
            model_id = model_data.get("id")
            if not model_id:
                return None

            pricing = model_data.get("pricing", {})

            return ModelInfo(
                id=model_id,
                name=model_data.get("name", model_id),
                provider="openrouter",
                context_length=model_data.get("context_length", 0),
                prompt_price=float(pricing.get("prompt", 0))
                * 1_000_000,  # Convert to per 1M
                completion_price=float(pricing.get("completion", 0))
                * 1_000_000,  # Convert to per 1M
                description=model_data.get("description"),
                tags=model_data.get("tags", []),
                is_available=model_data.get("available", True),
            )
        except (ValueError, TypeError):
            return None

    def _parse_openai_model(self, model_data: Dict[str, Any]) -> Optional[ModelInfo]:
        """Parse OpenAI model data"""
        try:
            model_id = model_data.get("id")
            if not model_id:
                return None

            # OpenAI pricing (approximate, should be updated regularly)
            pricing_map = {
                "gpt-4": {"prompt": 30.0, "completion": 60.0},
                "gpt-4-32k": {"prompt": 60.0, "completion": 120.0},
                "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
                "gpt-3.5-turbo-16k": {"prompt": 3.0, "completion": 4.0},
            }

            pricing = pricing_map.get(model_id, {"prompt": 2.0, "completion": 4.0})

            return ModelInfo(
                id=model_id,
                name=model_data.get("id", model_id),
                provider="openai",
                context_length=self._get_openai_context_length(model_id),
                prompt_price=pricing["prompt"],
                completion_price=pricing["completion"],
                description=f"OpenAI {model_id} model",
                tags=["openai", "chat"] if "gpt" in model_id else ["openai"],
            )
        except (ValueError, TypeError):
            return None

    def _get_openai_context_length(self, model_id: str) -> int:
        """Get context length for OpenAI models"""
        context_map = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
        }
        return context_map.get(model_id, 4096)

    def _get_fallback_models(self) -> Dict[str, ModelInfo]:
        """Fallback models when API fetching fails"""
        return {
            "gpt-3.5-turbo": ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="openai",
                context_length=4096,
                prompt_price=0.5,
                completion_price=1.5,
                description="OpenAI GPT-3.5 Turbo",
                tags=["openai", "chat", "cost-effective"],
            ),
            "claude-sonnet-4": ModelInfo(
                id="claude-sonnet-4",
                name="Claude 3 Haiku",
                provider="anthropic",
                context_length=200000,
                prompt_price=0.25,
                completion_price=1.25,
                description="Anthropic Claude 3 Haiku",
                tags=["anthropic", "fast", "cost-effective"],
            ),
            "llama-2-70b": ModelInfo(
                id="llama-2-70b",
                name="Llama 2 70B",
                provider="meta",
                context_length=4096,
                prompt_price=0.7,
                completion_price=0.8,
                description="Meta Llama 2 70B",
                tags=["meta", "open-source", "reasoning"],
            ),
        }

    # Query methods
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model by ID"""
        return self.models.get(model_id)

    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """Get models by provider"""
        return [model for model in self.models.values() if model.provider == provider]

    def get_free_models(self) -> List[ModelInfo]:
        """Get free models (no cost)"""
        return [
            model
            for model in self.models.values()
            if model.prompt_price == 0.0
            and model.completion_price == 0.0
            and model.is_available
        ]

    def get_budget_models(self, max_price_per_1m: float = 1.0) -> List[ModelInfo]:
        """Get budget-friendly models"""
        return [
            model
            for model in self.models.values()
            if model.prompt_price <= max_price_per_1m and model.is_available
        ]

    def get_premium_models(self, min_price_per_1m: float = 10.0) -> List[ModelInfo]:
        """Get premium models"""
        return [
            model
            for model in self.models.values()
            if model.prompt_price >= min_price_per_1m and model.is_available
        ]

    def search_models(self, query: str) -> List[ModelInfo]:
        """Search models by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for model in self.models.values():
            if not model.is_available:
                continue

            # Search in name
            if query_lower in model.name.lower():
                results.append(model)
                continue

            # Search in description
            if query_lower in model.description.lower():
                results.append(model)
                continue

            # Search in tags
            if any(query_lower in tag.lower() for tag in model.tags):
                results.append(model)
                continue

        return results

    def get_cheapest_model(self, provider: Optional[str] = None) -> Optional[ModelInfo]:
        """Get cheapest available model"""
        available_models = [m for m in self.models.values() if m.is_available]

        if provider:
            available_models = [m for m in available_models if m.provider == provider]

        if not available_models:
            return None

        return min(available_models, key=lambda m: m.prompt_price)

    def estimate_cost(
        self, model_id: str, input_tokens: int, output_tokens: int
    ) -> Optional[float]:
        """Estimate cost for model usage"""
        model = self.get_model(model_id)
        if not model:
            return None

        return model.estimate_cost(input_tokens, output_tokens)

    def get_models_summary(self) -> Dict[str, Any]:
        """Get summary of available models"""
        if not self.models:
            return {"error": "No models loaded"}

        available_models = [m for m in self.models.values() if m.is_available]

        # Provider breakdown
        provider_counts = {}
        for model in available_models:
            provider_counts[model.provider] = provider_counts.get(model.provider, 0) + 1

        # Price statistics
        prices = [m.prompt_price for m in available_models if m.prompt_price > 0]

        return {
            "total_models": len(self.models),
            "available_models": len(available_models),
            "providers": provider_counts,
            "free_models": len(self.get_free_models()),
            "budget_models": len(self.get_budget_models()),
            "premium_models": len(self.get_premium_models()),
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0,
            },
            "last_updated": (
                self.last_fetch_time.isoformat() if self.last_fetch_time else None
            ),
        }

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.models.clear()
        self.last_fetch_time = None
        logger.info("Models cache cleared")


# Global cache instance
_models_cache: Optional[ModelsCache] = None


def get_models_cache(
    openrouter_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
) -> ModelsCache:
    """Get global models cache instance"""
    global _models_cache

    if _models_cache is None:
        _models_cache = ModelsCache(
            openrouter_api_key=openrouter_api_key,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
        )

    return _models_cache


# Convenience functions
async def get_available_models(force_refresh: bool = False) -> Dict[str, ModelInfo]:
    """Get all available models"""
    cache = get_models_cache()
    return await cache.fetch_all_models(force_refresh=force_refresh)


async def get_model_info(model_id: str) -> Optional[ModelInfo]:
    """Get information for specific model"""
    cache = get_models_cache()
    await cache.fetch_all_models()
    return cache.get_model(model_id)


async def estimate_model_cost(
    model_id: str, input_tokens: int, output_tokens: int
) -> Optional[float]:
    """Estimate cost for model usage"""
    cache = get_models_cache()
    await cache.fetch_all_models()
    return cache.estimate_cost(model_id, input_tokens, output_tokens)


async def find_cheapest_model(provider: Optional[str] = None) -> Optional[ModelInfo]:
    """Find the cheapest available model"""
    cache = get_models_cache()
    await cache.fetch_all_models()
    return cache.get_cheapest_model(provider=provider)
