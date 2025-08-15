"""
UnrealOn LLM Utilities

Utility functions and helpers for UnrealOn LLM platform including
language detection, token counting, and model caching.
"""

# Language detection utilities
from .language_detector import (
    LanguageDetector,
    detect_language,
    detect_multiple_languages,
    is_language,
)

# Token counting utilities (legacy)
from .token_counter import (
    TokenCounter,
    count_tokens,
    count_message_tokens,
    optimize_for_tokens,
)

# Smart counting utilities (new approach)
from .smart_counter import (
    SmartTokenCounter,
    smart_count_tokens,
    smart_count_messages,
)

# Models cache utilities
from .models_cache import (
    ModelInfo,
    ModelsCache,
)

# HTML cleaning utilities
from .html_cleaner import (
    SmartHTMLCleaner,
    clean_html_for_llm,
    extract_js_data_only,
)

# Common utilities
from .common import (
    generate_correlation_id,
    generate_request_id,
)

# Data extraction utilities
from .data_extractor import (
    SmartDataExtractor,
    safe_extract_json,
    extract_llm_response_data,
    create_data_extractor,
)

# Exports
__all__ = [
    # Language Detection
    "LanguageDetector",
    "detect_language", 
    "detect_multiple_languages",
    "is_language",
    
    # Token Counting (Legacy)
    "TokenCounter",
    "count_tokens",
    "count_message_tokens", 
    "optimize_for_tokens",
    
    # Smart Counting (New)
    "SmartTokenCounter",
    "smart_count_tokens",
    "smart_count_messages",
    
    # Models Cache
    "ModelInfo",
    "ModelsCache",
    
    # HTML Cleaning
    "SmartHTMLCleaner",
    "clean_html_for_llm",
    "extract_js_data_only",
    
    # Common Utilities
    "generate_correlation_id",
    "generate_request_id",
    
    # Data Extraction
    "SmartDataExtractor",
    "safe_extract_json",
    "extract_llm_response_data",
    "create_data_extractor",
]
