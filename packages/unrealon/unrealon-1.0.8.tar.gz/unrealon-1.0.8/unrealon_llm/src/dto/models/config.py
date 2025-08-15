"""
LLM DTOs - Configuration Models
Configuration data models for UnrealOn LLM platform
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import CacheStrategy, LLMProvider, LLMTestingMode, OptimizationLevel


class LLMConfig(BaseModel):
    """Main configuration for UnrealOn LLM platform"""
    
    model_config = ConfigDict(
        title="LLM Configuration",
        description="Complete configuration for UnrealOn LLM platform",
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "openrouter_api_key": "sk-or-v1-...",
                "default_model": "anthropic/claude-3.5-sonnet",
                "daily_cost_limit_usd": 10.0,
                "enable_global_cache": True
            }
        }
    )
    
    # API Configuration
    openrouter_api_key: Optional[str] = Field(
        None, 
        description="OpenRouter API key",
        min_length=10
    )
    openai_api_key: Optional[str] = Field(
        None, 
        description="OpenAI API key",
        min_length=10
    )
    anthropic_api_key: Optional[str] = Field(
        None, 
        description="Anthropic API key",
        min_length=10
    )
    
    # Default Provider & Model
    default_provider: LLMProvider = Field(
        LLMProvider.OPENROUTER, 
        description="Default LLM provider"
    )
    default_model: str = Field(
        "anthropic/claude-3.5-sonnet", 
        description="Default model to use",
        min_length=1
    )
    fallback_models: List[str] = Field(
        default_factory=lambda: ["openai/gpt-3.5-turbo", "meta-llama/llama-2-70b-chat"],
        description="Fallback models if primary fails"
    )
    
    # Performance Settings
    max_concurrent_requests: int = Field(
        5, 
        ge=1, 
        le=50, 
        description="Max concurrent API requests"
    )
    request_timeout_seconds: int = Field(
        30, 
        ge=5, 
        le=300, 
        description="Request timeout"
    )
    max_retries: int = Field(
        3, 
        ge=0, 
        le=10, 
        description="Maximum retry attempts"
    )
    
    # Caching Configuration
    enable_global_cache: bool = Field(
        True, 
        description="Enable global caching"
    )
    cache_strategy: CacheStrategy = Field(
        CacheStrategy.MEMORY, 
        description="Caching strategy"
    )
    cache_ttl_hours: int = Field(
        24, 
        ge=1, 
        le=168, 
        description="Cache TTL in hours"
    )
    max_cache_size_mb: int = Field(
        100, 
        ge=10, 
        le=1000, 
        description="Max cache size in MB"
    )
    
    # Cost Management
    daily_cost_limit_usd: float = Field(
        10.0, 
        ge=0, 
        description="Daily cost limit in USD"
    )
    cost_alert_threshold: float = Field(
        0.8, 
        ge=0, 
        le=1, 
        description="Cost alert threshold (0-1)"
    )
    
    # Module-specific settings
    enable_html_analysis: bool = Field(
        True, 
        description="Enable HTML analysis module"
    )
    enable_translation: bool = Field(
        True, 
        description="Enable translation module"
    )
    enable_json_processing: bool = Field(
        True, 
        description="Enable JSON processing module"
    )
    enable_type_conversion: bool = Field(
        True, 
        description="Enable type conversion module"
    )


class AnalysisConfig(BaseModel):
    """Configuration for HTML analysis operations"""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Analysis settings
    optimization_level: OptimizationLevel = Field(
        OptimizationLevel.BALANCED,
        description="Analysis optimization level"
    )
    max_html_size_kb: int = Field(
        500, 
        ge=10, 
        le=2000, 
        description="Maximum HTML size in KB"
    )
    max_tokens_per_analysis: int = Field(
        2000, 
        ge=100, 
        le=8000, 
        description="Maximum tokens per analysis"
    )
    
    # Quality settings
    min_confidence_threshold: float = Field(
        0.8, 
        ge=0.5, 
        le=1.0, 
        description="Minimum confidence threshold"
    )
    enable_selector_validation: bool = Field(
        True, 
        description="Enable selector validation"
    )
    generate_fallback_selectors: bool = Field(
        True, 
        description="Generate fallback selectors"
    )
    
    # Preprocessing options
    remove_scripts: bool = Field(True, description="Remove script tags")
    remove_styles: bool = Field(True, description="Remove style tags")
    preserve_attributes: List[str] = Field(
        default_factory=lambda: ["class", "id", "data-*"],
        description="HTML attributes to preserve"
    )


class TranslationConfig(BaseModel):
    """Configuration for translation operations"""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Translation settings
    auto_detect_language: bool = Field(
        True, 
        description="Auto-detect source language"
    )
    preserve_formatting: bool = Field(
        True, 
        description="Preserve original formatting"
    )
    handle_technical_terms: bool = Field(
        True, 
        description="Handle technical terms specially"
    )
    
    # Quality settings
    min_translation_confidence: float = Field(
        0.9, 
        ge=0.5, 
        le=1.0, 
        description="Minimum translation confidence"
    )
    enable_consistency_checks: bool = Field(
        True, 
        description="Enable translation consistency checks"
    )
    
    # Performance settings
    batch_size: int = Field(
        10, 
        ge=1, 
        le=100, 
        description="Batch translation size"
    )
    max_text_length: int = Field(
        5000, 
        ge=100, 
        le=20000, 
        description="Maximum text length for single translation"
    )


class LLMTestConfiguration(BaseModel):
    """Complete LLM testing configuration"""
    
    model_config = ConfigDict(
        title="LLM Testing Configuration",
        description="Complete configuration for LLM testing with cost controls",
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "testing_mode": "mock_only",
                "cost_limit_usd": "0.25",
                "ai_accuracy_threshold": 0.85,
                "enable_real_api_tests": False
            }
        }
    )
    
    # Testing mode configuration
    testing_mode: LLMTestingMode = Field(default=LLMTestingMode.MOCK_ONLY)
    enable_real_api_tests: bool = Field(
        default=False, 
        description="Enable real API testing"
    )
    
    # Cost control settings
    cost_limit_usd: Decimal = Field(
        default=Decimal('0.25'), 
        ge=0, 
        le=Decimal('1.00'),
        description="Maximum cost limit for testing"
    )
    single_test_limit_usd: Decimal = Field(
        default=Decimal('0.05'), 
        ge=0, 
        le=Decimal('0.25'),
        description="Maximum cost per single test"
    )
    cost_alert_threshold: Decimal = Field(
        default=Decimal('0.20'), 
        ge=0, 
        le=Decimal('1.00'),
        description="Cost alert threshold"
    )
    
    # API configuration
    openrouter_api_key: Optional[str] = Field(
        None, 
        description="Real API key for controlled testing"
    )
    default_test_model: str = Field(
        default="anthropic/claude-3.5-sonnet", 
        description="Cheapest model for testing"
    )
    max_tokens_per_test: int = Field(
        default=500, 
        ge=10, 
        le=2000, 
        description="Token limit per test"
    )
    
    # Mock configuration
    mock_response_delay_ms: int = Field(
        default=100, 
        ge=0, 
        le=2000, 
        description="Simulated API delay"
    )
    mock_token_simulation: bool = Field(
        default=True, 
        description="Simulate realistic token usage"
    )
    mock_cost_simulation: bool = Field(
        default=True, 
        description="Simulate API costs"
    )
    
    # Quality validation settings
    ai_accuracy_threshold: float = Field(
        default=0.85, 
        ge=0.5, 
        le=1.0, 
        description="Minimum AI accuracy"
    )
    consistency_threshold: float = Field(
        default=0.85, 
        ge=0.5, 
        le=1.0, 
        description="Response consistency requirement"
    )
    validate_ai_outputs: bool = Field(
        default=True, 
        description="Enable AI output validation"
    )
    
    # Performance settings
    test_timeout_seconds: int = Field(
        default=30, 
        ge=5, 
        le=300, 
        description="Maximum test execution time"
    )
    parallel_test_workers: int = Field(
        default=1, 
        ge=1, 
        le=4, 
        description="Parallel test execution"
    )
    enable_performance_benchmarks: bool = Field(
        default=True, 
        description="Enable performance testing"
    )
