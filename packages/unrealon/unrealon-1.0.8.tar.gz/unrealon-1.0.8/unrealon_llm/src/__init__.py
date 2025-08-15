"""
🤖 UnrealOn LLM v1.0 - Large Language Model Integration

Advanced LLM integration tools for AI-powered parsing and data processing.
Service-based architecture following KISS principles.

Key Features:
- 🧠 Smart LLM client with multiple providers support
- 🕷️ HTML processing and pattern extraction
- 🌐 Translation and language detection
- 📊 Cost management and token counting
- 🎯 Type-safe operations with Pydantic v2
- 📝 Enterprise logging integration
- ⚡ Caching and optimization strategies
"""

# Core client
from .core import SmartLLMClient

# All DTOs and models (comprehensive export from dto module)
from .dto import *

# Managers
from .managers import (
    CacheManager,
    CostManager, 
    RequestManager,
)

# HTML Processing modules
from .modules.html_processor import (
    BaseHTMLProcessor,
    ListingProcessor,
    DetailsProcessor,
    UnrealOnLLM,
    UniversalExtractionSchema,
    ProcessingInfo,
    ExtractionResult,
)

# Utilities
from .utils import (
    # Language Detection
    LanguageDetector,
    detect_language, 
    detect_multiple_languages,
    is_language,
    # Token Counting
    SmartTokenCounter,
    smart_count_tokens,
    smart_count_messages,
    # HTML Cleaning
    SmartHTMLCleaner,
    clean_html_for_llm,
    extract_js_data_only,
    # Data Extraction
    SmartDataExtractor,
    safe_extract_json,
    extract_llm_response_data,
    create_data_extractor,
    # Common Utilities
    generate_correlation_id,
    generate_request_id,
)

# Configuration
from .llm_config import (
    LoggingConfig,
    setup_llm_logging,
    get_logging_config_from_env, 
    configure_llm_logging,
)

# Logging
from .llm_logging import (
    LLMEventType,
    LLMContext, 
    LLMLogger,
    initialize_llm_logger,
    get_llm_logger,
)

# Exceptions
from .exceptions import (
    # Base exceptions
    LLMError,
    APIError,
    # API-specific errors
    OpenRouterAPIError,
    OpenAIAPIError,
    AnthropicAPIError,
    RateLimitError,
    APIQuotaExceededError,
    ModelUnavailableError,
    NetworkError,
    AuthenticationError,
    # Cost and token errors
    CostLimitExceededError,
    TokenLimitExceededError,
    # HTML processing errors
    HTMLParsingError,
    HTMLTooLargeError,
    PatternDetectionError,
    SelectorGenerationError,
    SelectorValidationError,
    # Translation errors
    TranslationError,
    LanguageDetectionError,
    TranslationQualityError,
    # Schema errors
    SchemaGenerationError,
    TypeInferenceError,
    CodeGenerationError,
    # Cache errors
    CacheError,
    CacheCorruptionError,
    # Configuration errors
    ConfigurationError,
    MissingAPIKeyError,
    InvalidConfigurationError,
    # Processing errors
    ProcessingPipelineError,
    ResponseParsingError,
    RetryExhaustedError,
    # Helper functions
    raise_if_cost_exceeded,
    raise_if_tokens_exceeded,
    raise_if_html_too_large,
    wrap_api_error,
    ErrorCodes,
)

# Description
__description__ = "Large Language Model integration tools for UnrealOn SDK"

# Main exports
__all__ = [
    # Core client
    "SmartLLMClient",
    
    # Managers
    "CacheManager",
    "CostManager", 
    "RequestManager",
    
    # HTML Processing
    "BaseHTMLProcessor",
    "ListingProcessor",
    "DetailsProcessor",
    "UnrealOnLLM",
    "UniversalExtractionSchema",
    "ProcessingInfo",
    "ExtractionResult",
    
    # Utilities
    "LanguageDetector",
    "detect_language", 
    "detect_multiple_languages",
    "is_language",
    "SmartTokenCounter",
    "smart_count_tokens",
    "smart_count_messages",
    "SmartHTMLCleaner",
    "clean_html_for_llm",
    "extract_js_data_only",
    "SmartDataExtractor",
    "safe_extract_json",
    "extract_llm_response_data",
    "create_data_extractor",
    "generate_correlation_id",
    "generate_request_id",
    
    # Configuration
    "LoggingConfig",
    "setup_llm_logging",
    "get_logging_config_from_env", 
    "configure_llm_logging",
    
    # Logging
    "LLMEventType",
    "LLMContext", 
    "LLMLogger",
    "initialize_llm_logger",
    "get_llm_logger",
    
    # Exceptions
    "LLMError",
    "APIError",
    "OpenRouterAPIError",
    "OpenAIAPIError",
    "AnthropicAPIError",
    "RateLimitError",
    "APIQuotaExceededError",
    "ModelUnavailableError",
    "NetworkError",
    "AuthenticationError",
    "CostLimitExceededError",
    "TokenLimitExceededError",
    "HTMLParsingError",
    "HTMLTooLargeError",
    "PatternDetectionError",
    "SelectorGenerationError",
    "SelectorValidationError",
    "TranslationError",
    "LanguageDetectionError",
    "TranslationQualityError",
    "SchemaGenerationError",
    "TypeInferenceError",
    "CodeGenerationError",
    "CacheError",
    "CacheCorruptionError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "InvalidConfigurationError",
    "ProcessingPipelineError",
    "ResponseParsingError",
    "RetryExhaustedError",
    "raise_if_cost_exceeded",
    "raise_if_tokens_exceeded",
    "raise_if_html_too_large",
    "wrap_api_error",
    "ErrorCodes",
]

# Note: All DTO models are also exported via 'from .dto import *'
# This includes all enums, configuration models, core models,
# HTML analysis models, translation models, type conversion models,
# and statistics models as defined in dto/__init__.py
