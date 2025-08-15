"""
LLM DTOs - Core Models
Core data models for UnrealOn LLM platform
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import MessageRole


class TokenUsage(BaseModel):
    """Token usage statistics"""
    
    model_config = ConfigDict(
        title="Token Usage",
        description="Token usage statistics for LLM requests",
        validate_assignment=True,
        extra="forbid"
    )
    
    prompt_tokens: int = Field(
        ..., 
        ge=0, 
        description="Tokens used in prompt"
    )
    completion_tokens: int = Field(
        ..., 
        ge=0, 
        description="Tokens used in completion"
    )
    total_tokens: int = Field(
        ..., 
        ge=0, 
        description="Total tokens used"
    )
    
    @field_validator('total_tokens')
    @classmethod
    def validate_total_tokens(cls, v, info):
        values = info.data
        if 'prompt_tokens' in values and 'completion_tokens' in values:
            expected_total = values['prompt_tokens'] + values['completion_tokens']
            if v != expected_total:
                raise ValueError(
                    f"Total tokens {v} doesn't match sum of prompt and completion tokens"
                )
        return v


class ChatMessage(BaseModel):
    """Chat message with role and content"""
    
    model_config = ConfigDict(
        title="Chat Message",
        description="Individual chat message with role and content",
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "Analyze this HTML structure",
                "name": "user"
            }
        }
    )
    
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(
        ..., 
        min_length=1, 
        description="Message content"
    )
    name: Optional[str] = Field(None, description="Sender name")
    function_call: Optional[Dict[str, Any]] = Field(
        None, 
        description="Function call data"
    )


class LLMResponse(BaseModel):
    """Base LLM response model"""
    
    model_config = ConfigDict(
        title="LLM Response",
        description="Complete LLM response with metadata",
        validate_assignment=True,
        extra="forbid"
    )
    
    id: str = Field(..., description="Response ID")
    model: str = Field(..., description="Model used")
    content: str = Field(..., description="Response content")
    finish_reason: Optional[str] = Field(
        None, 
        description="Completion finish reason"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now, 
        description="Creation timestamp"
    )
    processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Processing time"
    )
    token_usage: Optional[TokenUsage] = Field(
        None, 
        description="Token usage details"
    )
    cost_usd: Optional[float] = Field(
        None, 
        ge=0, 
        description="Cost in USD"
    )
    
    # Enhanced data
    extracted_model: Optional[BaseModel] = Field(
        None, 
        description="Extracted and validated Pydantic model from response"
    )
    confidence_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Response confidence"
    )


class LanguageDetection(BaseModel):
    """Language detection result"""
    
    model_config = ConfigDict(
        title="Language Detection",
        description="Language detection result with confidence",
        validate_assignment=True,
        extra="forbid"
    )
    
    detected_language: str = Field(
        ..., 
        description="Detected language code"
    )
    confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Detection confidence"
    )
    alternative_languages: List[Dict[str, float]] = Field(
        default_factory=list, 
        description="Alternative language possibilities"
    )


class CostBreakdown(BaseModel):
    """Cost breakdown by operation and model"""
    
    model_config = ConfigDict(
        title="Cost Breakdown",
        description="Detailed cost analysis by module and model",
        validate_assignment=True,
        extra="forbid"
    )
    
    total_cost_usd: float = Field(
        ..., 
        ge=0, 
        description="Total cost across all operations"
    )
    by_module: Dict[str, float] = Field(
        default_factory=dict, 
        description="Cost breakdown by module"
    )
    by_model: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Cost breakdown by model with usage details"
    )
    by_operation: Dict[str, float] = Field(
        default_factory=dict, 
        description="Cost breakdown by operation type"
    )
    
    # Time period
    period_start: datetime = Field(
        ..., 
        description="Cost analysis period start"
    )
    period_end: datetime = Field(
        ..., 
        description="Cost analysis period end"
    )


class HealthStatus(BaseModel):
    """Health status for system components"""
    
    model_config = ConfigDict(
        title="Health Status",
        description="Health status of LLM platform components",
        validate_assignment=True,
        extra="forbid"
    )
    
    status: str = Field(
        ..., 
        pattern=r"^(healthy|degraded|unhealthy)$",
        description="Overall status"
    )
    checked_at: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp"
    )
    
    # Component statuses
    modules: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Status of individual modules"
    )
    
    # Performance metrics
    response_time_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Average response time"
    )
    error_rate: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Error rate (0-1)"
    )
    
    # Resource usage
    memory_usage_mb: Optional[float] = Field(
        None,
        ge=0,
        description="Memory usage in MB"
    )
    cache_hit_rate: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Cache hit rate (0-1)"
    )


class ProcessingMetrics(BaseModel):
    """Processing performance metrics"""
    
    model_config = ConfigDict(
        title="Processing Metrics",
        description="Performance metrics for LLM operations",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Processing statistics
    total_requests: int = Field(
        0,
        ge=0,
        description="Total number of requests processed"
    )
    successful_requests: int = Field(
        0,
        ge=0,
        description="Number of successful requests"
    )
    failed_requests: int = Field(
        0,
        ge=0,
        description="Number of failed requests"
    )
    
    # Performance metrics
    average_response_time_seconds: float = Field(
        0.0,
        ge=0,
        description="Average response time"
    )
    total_processing_time_seconds: float = Field(
        0.0,
        ge=0,
        description="Total processing time"
    )
    
    # Resource metrics
    total_tokens_used: int = Field(
        0,
        ge=0,
        description="Total tokens consumed"
    )
    total_cost_usd: float = Field(
        0.0,
        ge=0,
        description="Total cost incurred"
    )
    
    # Cache performance
    cache_hits: int = Field(
        0,
        ge=0,
        description="Number of cache hits"
    )
    cache_misses: int = Field(
        0,
        ge=0,
        description="Number of cache misses"
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_cache_operations = self.cache_hits + self.cache_misses
        if total_cache_operations == 0:
            return 0.0
        return self.cache_hits / total_cache_operations
