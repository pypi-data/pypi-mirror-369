"""
UnrealOn LLM DTOs - Data Transfer Objects

Comprehensive data models for UnrealOn LLM platform with strict validation.
All models are built with Pydantic v2 for type safety and performance.
"""

# Enums
from .models.enums import (
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
    LLMTestingMode,
)

# Configuration models
from .models.config import (
    LLMConfig,
    AnalysisConfig,
    TranslationConfig,
    LLMTestConfiguration,
)

# Core models
from .models.core import (
    TokenUsage,
    ChatMessage,
    LLMResponse,
    LanguageDetection,
    CostBreakdown,
    HealthStatus,
    ProcessingMetrics,
)

# HTML Analysis models
from .models.html_analysis import (
    DetectedPattern,
    SelectorInfo,
    HTMLAnalysisRequest,
    HTMLAnalysisResult,
    SelectorValidationResult,
    CompleteAnalysisResult,
)

# Translation models
from .models.translation import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    JSONTranslationRequest,
    JSONTranslationResponse,
)

# Type Conversion models
from .models.type_conversion import (
    FieldAnalysis,
    StructureAnalysis,
    PydanticSchema,
    TypeScriptSchema,
    SchemaGenerationRequest,
    SchemaGenerationResponse,
    ConversionRequest,
    ConversionResponse,
)

# Statistics models
from .models.statistics import (
    ModuleUsage,
    UsageStats,
    StageResult,
    CompleteProcessingResult,
    PerformanceMetrics,
    BenchmarkResult,
)


# Exports organized by category
__all__ = [
    # ===== ENUMS =====
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
    "LLMTestingMode",
    # ===== CONFIGURATION =====
    "LLMConfig",
    "AnalysisConfig",
    "TranslationConfig",
    "LLMTestConfiguration",
    # ===== CORE MODELS =====
    "TokenUsage",
    "ChatMessage",
    "LLMResponse",
    "LanguageDetection",
    "CostBreakdown",
    "HealthStatus",
    "ProcessingMetrics",
    # ===== HTML ANALYSIS =====
    "DetectedPattern",
    "SelectorInfo",
    "HTMLAnalysisRequest",
    "HTMLAnalysisResult",
    "SelectorValidationResult",
    "CompleteAnalysisResult",
    # ===== TRANSLATION =====
    "TranslationRequest",
    "TranslationResponse",
    "BatchTranslationRequest",
    "BatchTranslationResponse",
    "JSONTranslationRequest",
    "JSONTranslationResponse",
    # ===== TYPE CONVERSION =====
    "FieldAnalysis",
    "StructureAnalysis",
    "PydanticSchema",
    "TypeScriptSchema",
    "SchemaGenerationRequest",
    "SchemaGenerationResponse",
    "ConversionRequest",
    "ConversionResponse",
    # ===== STATISTICS =====
    "ModuleUsage",
    "UsageStats",
    "StageResult",
    "CompleteProcessingResult",
    "PerformanceMetrics",
    "BenchmarkResult",
]


# Type aliases for convenience
LLMConfigType = LLMConfig
HTMLAnalysisResultType = HTMLAnalysisResult
TranslationResponseType = TranslationResponse
PydanticSchemaType = PydanticSchema
UsageStatsType = UsageStats

# Version info
__version__ = "2.0.0"
__author__ = "UnrealOn Team"
__description__ = "Data Transfer Objects for UnrealOn LLM Platform"
