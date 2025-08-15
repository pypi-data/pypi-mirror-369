"""
UnrealOn LLM Provider

Simple provider module for UnrealOn LLM functionality.
"""

# Core LLM functionality
from unrealon_llm.src.core import SmartLLMClient

# HTML parsing and analysis
from unrealon_llm.src.utils.html_cleaner import SmartHTMLCleaner
from unrealon_llm.src.modules.html_processor import (
    ListingProcessor,
    DetailsProcessor,
    UnrealOnLLM,
)

# Logging and configuration
from unrealon_llm.src.llm_config import setup_llm_logging, configure_llm_logging
from unrealon_llm.src.llm_logging import (
    get_llm_logger,
    LLMEventType,
    LLMContext,
    initialize_llm_logger,
)

# Configuration and DTOs
from unrealon_llm.src.dto import (
    # Core configuration
    LLMConfig,
    AnalysisConfig,
    TranslationConfig,
    # Enums
    LLMProvider,
    OptimizationLevel,
    CacheStrategy,
    MessageRole,
    PatternType,
    SelectorType,
    LanguageCode,
    DataType,
    SchemaFormat,
    ProcessingStage,
    # Core models
    TokenUsage,
    ChatMessage,
    LLMResponse,
    LanguageDetection,
    CostBreakdown,
    HealthStatus,
    ProcessingMetrics,
    # HTML Analysis models
    DetectedPattern,
    SelectorInfo,
    HTMLAnalysisRequest,
    HTMLAnalysisResult,
    SelectorValidationResult,
    CompleteAnalysisResult,
)

# Utilities
from unrealon_llm.src.utils.data_extractor import SmartDataExtractor
from unrealon_llm.src.utils.smart_counter import SmartTokenCounter
from unrealon_llm.src.utils.language_detector import LanguageDetector


# Direct exports for convenience
__all__ = [
    # Factory class
    "UnrealOnLLM",
    # Core classes
    "SmartLLMClient",
    "SmartHTMLCleaner",
    "SmartDataExtractor",
    "SmartTokenCounter",
    "LanguageDetector",
    "ListingProcessor",
    "DetailsProcessor",
    # Configuration classes
    "LLMConfig",
    "AnalysisConfig",
    "TranslationConfig",
    # Enums
    "LLMProvider",
    "OptimizationLevel",
    "CacheStrategy",
    "MessageRole",
    "PatternType",
    "SelectorType",
    "LanguageCode",
    "DataType",
    "SchemaFormat",
    "ProcessingStage",
    # Core models
    "TokenUsage",
    "ChatMessage",
    "LLMResponse",
    "LanguageDetection",
    "CostBreakdown",
    "HealthStatus",
    "ProcessingMetrics",
    # HTML Analysis models
    "DetectedPattern",
    "SelectorInfo",
    "HTMLAnalysisRequest",
    "HTMLAnalysisResult",
    "SelectorValidationResult",
    "CompleteAnalysisResult",
    # Logging
    "setup_llm_logging",
    "configure_llm_logging",
    "get_llm_logger",
    "initialize_llm_logger",
    "LLMEventType",
    "LLMContext",
]
