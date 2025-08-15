"""
HTML Processor Factory

Factory class for creating HTML processors.
"""

from unrealon_llm.src.core import SmartLLMClient
from unrealon_llm.src.dto import LLMConfig

from .listing_processor import ListingProcessor
from .details_processor import DetailsProcessor


class UnrealOnLLM:
    """Factory class for creating UnrealOn LLM components"""

    @staticmethod
    def create_client(
        openrouter_api_key: str,
        default_model: str = "anthropic/claude-3.5-sonnet",
        daily_cost_limit: float = 5.0,
        enable_caching: bool = True,
        cache_ttl_minutes: int = 30,
    ) -> SmartLLMClient:
        """
        Create LLM client

        Args:
            openrouter_api_key: OpenRouter API key
            default_model: Default model to use
            daily_cost_limit: Daily cost limit in USD
            enable_caching: Enable response caching
            cache_ttl_minutes: Cache TTL in minutes

        Returns:
            Configured SmartLLMClient instance
        """
        config = LLMConfig(
            openrouter_api_key=openrouter_api_key,
            default_model=default_model,
            daily_cost_limit_usd=daily_cost_limit,
            request_timeout_seconds=60,
            max_retries=3,
            enable_global_cache=enable_caching,
            cache_ttl_hours=max(1, int(cache_ttl_minutes / 60)),
        )

        return SmartLLMClient(config)

    @staticmethod
    def create_listing_processor(
        openrouter_api_key: str,
        default_model: str = "anthropic/claude-3.5-sonnet",
        daily_cost_limit: float = 1.0,
        enable_caching: bool = False,  # Disable cache for HTML processors
    ) -> ListingProcessor:
        """
        Create listing processor

        Args:
            openrouter_api_key: OpenRouter API key
            default_model: Default model to use
            daily_cost_limit: Daily cost limit in USD
            enable_caching: Enable response caching (disabled by default for HTML processing)

        Returns:
            Configured ListingProcessor instance
        """
        llm_client = UnrealOnLLM.create_client(
            openrouter_api_key=openrouter_api_key,
            default_model=default_model,
            daily_cost_limit=daily_cost_limit,
            enable_caching=enable_caching,
        )
        return ListingProcessor(llm_client)

    @staticmethod
    def create_details_processor(
        openrouter_api_key: str,
        default_model: str = "anthropic/claude-3.5-sonnet",
        daily_cost_limit: float = 1.0,
        enable_caching: bool = False,  # Disable cache for HTML processors
    ) -> DetailsProcessor:
        """
        Create details processor

        Args:
            openrouter_api_key: OpenRouter API key
            default_model: Default model to use
            daily_cost_limit: Daily cost limit in USD
            enable_caching: Enable response caching (disabled by default for HTML processing)

        Returns:
            Configured DetailsProcessor instance
        """
        llm_client = UnrealOnLLM.create_client(
            openrouter_api_key=openrouter_api_key,
            default_model=default_model,
            daily_cost_limit=daily_cost_limit,
            enable_caching=enable_caching,
        )
        return DetailsProcessor(llm_client)
