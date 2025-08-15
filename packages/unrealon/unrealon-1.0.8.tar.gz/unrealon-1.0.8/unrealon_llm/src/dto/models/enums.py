"""
LLM DTOs - Enums
Enumeration types for UnrealOn LLM platform
"""

from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class OptimizationLevel(str, Enum):
    """Optimization levels for various operations"""
    SPEED = "speed"          # Fast but less accurate
    BALANCED = "balanced"    # Balance of speed and accuracy
    ROBUST = "robust"        # Slow but highly accurate


class CacheStrategy(str, Enum):
    """Caching strategies"""
    NONE = "none"
    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"


class MessageRole(str, Enum):
    """Chat message roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class PatternType(str, Enum):
    """Types of HTML patterns"""
    PRODUCT_TITLE = "product_title"
    PRICE = "price"
    DESCRIPTION = "description"
    IMAGE = "image"
    RATING = "rating"
    NAVIGATION = "navigation"
    BREADCRUMB = "breadcrumb"
    FORM = "form"
    BUTTON = "button"
    LINK = "link"
    LIST = "list"
    TABLE = "table"
    CUSTOM = "custom"


class SelectorType(str, Enum):
    """Types of CSS selectors"""
    CSS = "css"
    XPATH = "xpath"
    BOTH = "both"


class LanguageCode(str, Enum):
    """Supported language codes"""
    EN = "en"
    RU = "ru"
    KO = "ko"
    ZH = "zh"
    JA = "ja"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    AR = "ar"
    HI = "hi"
    TR = "tr"
    PL = "pl"
    UK = "uk"
    AUTO = "auto"  # Auto-detect


class DataType(str, Enum):
    """Detected data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    DATETIME = "datetime"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    CURRENCY = "currency"


class SchemaFormat(str, Enum):
    """Supported schema formats"""
    PYDANTIC = "pydantic"
    TYPESCRIPT = "typescript"
    JSON_SCHEMA = "json_schema"
    DATACLASS = "dataclass"
    SQLALCHEMY = "sqlalchemy"


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    HTML_ANALYSIS = "html_analysis"
    TRANSLATION = "translation"
    TYPE_GENERATION = "type_generation"
    VALIDATION = "validation"
    COMPLETE = "complete"


class LLMTestingMode(str, Enum):
    """LLM testing execution modes"""
    MOCK_ONLY = "mock_only"
    COST_CONTROLLED_REAL = "cost_controlled_real"
    DEVELOPMENT = "development"
    CI_CD = "ci_cd"
