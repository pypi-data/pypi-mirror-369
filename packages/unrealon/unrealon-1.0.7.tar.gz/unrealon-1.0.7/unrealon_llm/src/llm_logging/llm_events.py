"""
LLM-specific Event Types and Context

Extends the SDK logging system with AI/LLM specific event types and context models.
Focused on tracking LLM operations, costs, performance, and analysis results.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from unrealon_sdk.src.dto.logging import SDKContext, SDKEventType

# Use SDK event types directly instead of creating new ones
class LLMEventType(str, Enum):
    """LLM-specific event types mapped to SDK event types for compatibility."""
    
    # LLM Client Events (mapped to SDK events)
    LLM_CLIENT_INITIALIZED = SDKEventType.COMPONENT_CREATED.value
    LLM_REQUEST_STARTED = SDKEventType.API_CALL_STARTED.value 
    LLM_REQUEST_COMPLETED = SDKEventType.API_CALL_COMPLETED.value
    LLM_REQUEST_FAILED = SDKEventType.API_CALL_FAILED.value
    LLM_REQUEST_RETRIED = SDKEventType.CONNECTION_RETRY.value
    LLM_REQUEST_CACHED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    
    # Cost Tracking Events (mapped to SDK events)
    COST_CALCULATED = SDKEventType.PERFORMANCE_METRIC_COLLECTED.value
    COST_LIMIT_WARNING = SDKEventType.PERFORMANCE_THRESHOLD_EXCEEDED.value
    COST_LIMIT_EXCEEDED = SDKEventType.ERROR_DETECTED.value
    DAILY_BUDGET_RESET = SDKEventType.DEBUG_CHECKPOINT.value
    
    # Token Management Events (mapped to SDK events)
    TOKENS_COUNTED = SDKEventType.PERFORMANCE_METRIC_COLLECTED.value
    TOKEN_OPTIMIZATION_APPLIED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    TOKEN_LIMIT_EXCEEDED = SDKEventType.ERROR_DETECTED.value
    
    # HTML Analysis Events (mapped to SDK events)
    HTML_ANALYSIS_STARTED = SDKEventType.COMMAND_RECEIVED.value
    HTML_ANALYSIS_COMPLETED = SDKEventType.COMMAND_COMPLETED.value
    HTML_CLEANING_APPLIED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    SELECTOR_GENERATED = SDKEventType.COMMAND_COMPLETED.value
    SELECTOR_VALIDATED = SDKEventType.PYDANTIC_MODEL_VALIDATION.value
    PATTERN_EXTRACTED = SDKEventType.COMMAND_COMPLETED.value
    
    # Translation Events (mapped to SDK events)  
    TRANSLATION_STARTED = SDKEventType.COMMAND_RECEIVED.value
    TRANSLATION_COMPLETED = SDKEventType.COMMAND_COMPLETED.value
    LANGUAGE_DETECTED = SDKEventType.DEBUG_CHECKPOINT.value
    
    # Schema Generation Events (mapped to SDK events)
    SCHEMA_GENERATION_STARTED = SDKEventType.COMMAND_RECEIVED.value
    SCHEMA_GENERATION_COMPLETED = SDKEventType.COMMAND_COMPLETED.value
    TYPE_CONVERSION_APPLIED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    
    # Cache Events (mapped to SDK events)
    CACHE_HIT = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    CACHE_MISS = SDKEventType.DEBUG_CHECKPOINT.value
    RESPONSE_CACHED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    
    # Models Cache Events (mapped to SDK events)
    MODELS_CACHE_UPDATED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    
    # Performance Events (mapped to SDK events)
    HTML_SIZE_OPTIMIZED = SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED.value
    BATCH_PROCESSING_STARTED = SDKEventType.COMMAND_RECEIVED.value
    BATCH_PROCESSING_COMPLETED = SDKEventType.COMMAND_COMPLETED.value


class LLMContext(SDKContext):
    """Extended context for LLM operations."""
    
    # LLM Provider Information
    provider: Optional[str] = Field(None, description="LLM provider (openrouter, openai, etc.)")
    model: Optional[str] = Field(None, description="Model used for request")
    
    # Request Details
    request_id: Optional[str] = Field(None, description="Unique request identifier") 
    prompt_tokens: Optional[int] = Field(None, description="Number of input tokens")
    completion_tokens: Optional[int] = Field(None, description="Number of output tokens")
    total_tokens: Optional[int] = Field(None, description="Total tokens used")
    
    # Cost Information
    cost_usd: Optional[float] = Field(None, description="Request cost in USD")
    daily_cost_usd: Optional[float] = Field(None, description="Total daily cost in USD")
    
    # HTML Analysis Context
    html_size_bytes: Optional[int] = Field(None, description="Original HTML size in bytes")
    cleaned_html_size_bytes: Optional[int] = Field(None, description="Cleaned HTML size in bytes")
    target_elements: Optional[List[str]] = Field(None, description="Target elements for extraction")
    selectors_generated: Optional[int] = Field(None, description="Number of selectors generated")
    confidence_score: Optional[float] = Field(None, description="Analysis confidence score")
    
    # Translation Context
    source_language: Optional[str] = Field(None, description="Source language detected")
    target_language: Optional[str] = Field(None, description="Target language for translation")
    text_length: Optional[int] = Field(None, description="Length of text to translate")
    
    # Schema Context  
    schema_type: Optional[str] = Field(None, description="Type of schema generated (pydantic, typescript, etc.)")
    fields_count: Optional[int] = Field(None, description="Number of fields in schema")
    
    # Performance Metrics
    cache_hit_rate: Optional[float] = Field(None, description="Cache hit rate percentage")
    optimization_applied: Optional[str] = Field(None, description="Type of optimization applied")
    
    model_config = ConfigDict(
        extra="allow"  # Allow additional fields for flexibility
    )
