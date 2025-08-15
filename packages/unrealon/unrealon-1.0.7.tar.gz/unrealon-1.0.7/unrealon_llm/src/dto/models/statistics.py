"""
LLM DTOs - Statistics Models
Data models for usage statistics and analytics
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import ProcessingStage


class ModuleUsage(BaseModel):
    """Usage statistics for individual module"""
    
    model_config = ConfigDict(
        title="Module Usage",
        description="Usage statistics for individual LLM module",
        validate_assignment=True,
        extra="forbid"
    )
    
    module_name: str = Field(..., description="Module name")
    total_requests: int = Field(
        0, 
        ge=0, 
        description="Total requests processed"
    )
    successful_requests: int = Field(
        0, 
        ge=0, 
        description="Successful requests"
    )
    failed_requests: int = Field(
        0, 
        ge=0, 
        description="Failed requests"
    )
    
    # Performance metrics
    average_response_time: float = Field(
        0.0, 
        ge=0, 
        description="Average response time"
    )
    total_processing_time: float = Field(
        0.0, 
        ge=0, 
        description="Total processing time"
    )
    
    # Cost tracking
    total_cost_usd: float = Field(
        0.0, 
        ge=0, 
        description="Total cost incurred"
    )
    tokens_consumed: int = Field(
        0, 
        ge=0, 
        description="Total tokens used"
    )
    
    # Cache performance
    cache_hits: int = Field(0, ge=0, description="Cache hits")
    cache_misses: int = Field(0, ge=0, description="Cache misses")
    
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


class UsageStats(BaseModel):
    """Comprehensive usage statistics"""
    
    model_config = ConfigDict(
        title="Usage Statistics",
        description="Comprehensive usage statistics across all modules",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Time period
    period_start: datetime = Field(..., description="Statistics period start")
    period_end: datetime = Field(..., description="Statistics period end")
    
    # Overall metrics
    total_requests: int = Field(
        0, 
        ge=0, 
        description="Total requests across all modules"
    )
    total_cost_usd: float = Field(
        0.0, 
        ge=0, 
        description="Total cost incurred"
    )
    total_tokens_used: int = Field(
        0, 
        ge=0, 
        description="Total tokens consumed"
    )
    
    # Module breakdown
    module_usage: List[ModuleUsage] = Field(
        ..., 
        description="Usage by module"
    )
    
    # Performance metrics
    average_response_time: float = Field(
        0.0, 
        ge=0, 
        description="Overall average response time"
    )
    cache_hit_rate: float = Field(
        0.0, 
        ge=0, 
        le=1, 
        description="Overall cache hit rate"
    )
    success_rate: float = Field(
        0.0, 
        ge=0, 
        le=1, 
        description="Overall success rate"
    )
    
    # Cost analysis
    cost_by_model: Dict[str, float] = Field(
        default_factory=dict, 
        description="Cost breakdown by model"
    )
    cost_by_operation: Dict[str, float] = Field(
        default_factory=dict, 
        description="Cost breakdown by operation"
    )
    
    # Recommendations
    optimization_recommendations: List[str] = Field(
        default_factory=list, 
        description="Usage optimization suggestions"
    )
    cost_saving_opportunities: List[str] = Field(
        default_factory=list, 
        description="Cost reduction suggestions"
    )


class StageResult(BaseModel):
    """Result of individual processing stage"""
    
    model_config = ConfigDict(
        title="Stage Result",
        description="Result of individual processing pipeline stage",
        validate_assignment=True,
        extra="forbid"
    )
    
    stage: ProcessingStage = Field(..., description="Processing stage")
    success: bool = Field(..., description="Stage completion status")
    processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Stage processing time"
    )
    
    # Stage-specific data
    stage_data: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Stage-specific results"
    )
    error_message: Optional[str] = Field(
        None, 
        description="Error message if failed"
    )
    
    # Quality metrics
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Stage confidence"
    )
    quality_metrics: Dict[str, float] = Field(
        default_factory=dict, 
        description="Quality measurements"
    )
    
    # Performance metrics
    tokens_used: Optional[int] = Field(
        None,
        ge=0,
        description="Tokens consumed in this stage"
    )
    cost_usd: Optional[float] = Field(
        None,
        ge=0,
        description="Cost for this stage"
    )
    cache_utilized: bool = Field(
        False,
        description="Whether cache was used"
    )


class CompleteProcessingResult(BaseModel):
    """Result of complete processing pipeline"""
    
    model_config = ConfigDict(
        title="Complete Processing Result",
        description="Complete result of processing pipeline with all stages",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Input metadata
    input_html_size: int = Field(
        ..., 
        ge=0, 
        description="Input HTML size"
    )
    target_language: str = Field(..., description="Target language used")
    processing_config: Dict[str, Any] = Field(
        ..., 
        description="Processing configuration"
    )
    
    # Processing results
    stage_results: List[StageResult] = Field(
        ..., 
        description="Results from each stage"
    )
    overall_success: bool = Field(
        ..., 
        description="Overall processing success"
    )
    total_processing_time: float = Field(
        ..., 
        ge=0, 
        description="Total processing time"
    )
    
    # Generated outputs (references to actual result objects)
    html_analysis_result_id: Optional[str] = Field(
        None,
        description="ID of HTML analysis result"
    )
    translated_data_id: Optional[str] = Field(
        None,
        description="ID of translated data result"
    )
    pydantic_schema_id: Optional[str] = Field(
        None,
        description="ID of generated Pydantic schema"
    )
    typescript_schema_id: Optional[str] = Field(
        None,
        description="ID of generated TypeScript schema"
    )
    
    # Quality and performance
    overall_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Overall confidence score"
    )
    cost_breakdown: Dict[str, float] = Field(
        default_factory=dict, 
        description="Cost by operation"
    )
    total_cost_usd: float = Field(
        ..., 
        ge=0, 
        description="Total processing cost"
    )
    
    # Performance indicators
    cache_efficiency: float = Field(
        ...,
        ge=0,
        le=1,
        description="Cache utilization efficiency"
    )
    token_efficiency: float = Field(
        ...,
        ge=0,
        description="Token usage efficiency ratio"
    )
    
    # Recommendations
    quality_assessment: str = Field(
        ...,
        description="Overall quality assessment"
    )
    production_readiness: bool = Field(
        ...,
        description="Whether result is production ready"
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )


class PerformanceMetrics(BaseModel):
    """Performance metrics collection"""
    
    model_config = ConfigDict(
        title="Performance Metrics",
        description="Comprehensive performance metrics for LLM operations",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Time metrics
    operation_name: str = Field(..., description="Operation being measured")
    start_time: datetime = Field(..., description="Operation start time")
    end_time: datetime = Field(..., description="Operation end time")
    duration_seconds: float = Field(
        ..., 
        ge=0, 
        description="Operation duration"
    )
    
    # Resource metrics
    memory_usage_mb: Optional[float] = Field(
        None,
        ge=0,
        description="Memory usage during operation"
    )
    cpu_usage_percent: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="CPU usage percentage"
    )
    
    # LLM-specific metrics
    tokens_per_second: Optional[float] = Field(
        None,
        ge=0,
        description="Token processing rate"
    )
    api_latency_ms: Optional[float] = Field(
        None,
        ge=0,
        description="API response latency"
    )
    
    # Quality metrics
    accuracy_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Operation accuracy score"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Operation confidence score"
    )
    
    # Context information
    model_used: Optional[str] = Field(
        None,
        description="LLM model used"
    )
    input_size_bytes: Optional[int] = Field(
        None,
        ge=0,
        description="Input data size"
    )
    output_size_bytes: Optional[int] = Field(
        None,
        ge=0,
        description="Output data size"
    )
    
    # Error information
    errors_encountered: List[str] = Field(
        default_factory=list,
        description="Errors that occurred during operation"
    )
    warnings_generated: List[str] = Field(
        default_factory=list,
        description="Warnings generated during operation"
    )


class BenchmarkResult(BaseModel):
    """Benchmark test result"""
    
    model_config = ConfigDict(
        title="Benchmark Result",
        description="Result of performance benchmark test",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Test identification
    test_name: str = Field(..., description="Benchmark test name")
    test_category: str = Field(..., description="Test category")
    test_version: str = Field(..., description="Test version")
    
    # Performance results
    execution_time_seconds: float = Field(
        ...,
        ge=0,
        description="Test execution time"
    )
    throughput_ops_per_second: Optional[float] = Field(
        None,
        ge=0,
        description="Operations per second"
    )
    
    # Resource usage
    peak_memory_mb: float = Field(
        ...,
        ge=0,
        description="Peak memory usage"
    )
    average_cpu_percent: float = Field(
        ...,
        ge=0,
        le=100,
        description="Average CPU usage"
    )
    
    # Quality metrics
    accuracy_achieved: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Accuracy achieved in test"
    )
    baseline_comparison: Optional[float] = Field(
        None,
        description="Performance vs baseline (1.0 = same, >1.0 = better)"
    )
    
    # Test environment
    test_environment: Dict[str, Any] = Field(
        default_factory=dict,
        description="Test environment details"
    )
    
    # Results analysis
    passed: bool = Field(..., description="Whether test passed criteria")
    performance_grade: str = Field(
        ...,
        pattern=r"^[A-F]$",
        description="Performance grade A-F"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Performance improvement recommendations"
    )
