"""
LLM DTOs - HTML Analysis Models
Data models for HTML analysis and selector generation
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import PatternType, SelectorType


class DetectedPattern(BaseModel):
    """HTML pattern detected by AI analysis"""
    
    model_config = ConfigDict(
        title="Detected Pattern",
        description="HTML pattern identified by AI analysis",
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "type": "product_title",
                "css_selector": ".product-title",
                "confidence": 0.95,
                "element_count": 1
            }
        }
    )
    
    type: PatternType = Field(..., description="Pattern type")
    css_selector: str = Field(
        ..., 
        min_length=1, 
        description="CSS selector"
    )
    xpath: Optional[str] = Field(None, description="XPath expression")
    confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Detection confidence"
    )
    
    # Pattern details
    element_count: int = Field(
        ..., 
        ge=0, 
        description="Number of matching elements"
    )
    attributes_used: List[str] = Field(
        default_factory=list, 
        description="HTML attributes used"
    )
    semantic_description: str = Field(
        ..., 
        description="Human-readable description"
    )
    
    # Fallback selectors
    fallback_selectors: List[str] = Field(
        default_factory=list, 
        description="Alternative selectors"
    )
    robustness_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Selector robustness"
    )


class SelectorInfo(BaseModel):
    """Information about generated selector"""
    
    model_config = ConfigDict(
        title="Selector Info",
        description="Detailed information about generated CSS selector",
        validate_assignment=True,
        extra="forbid"
    )
    
    css_selector: str = Field(
        ..., 
        min_length=1, 
        description="Primary CSS selector"
    )
    xpath: Optional[str] = Field(None, description="XPath equivalent")
    confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Selector confidence"
    )
    
    # Validation results
    is_unique: bool = Field(..., description="Selector matches unique element")
    match_count: int = Field(
        ..., 
        ge=0, 
        description="Number of elements matched"
    )
    
    # Performance metrics
    selection_speed_ms: Optional[float] = Field(
        None, 
        ge=0, 
        description="Selection speed"
    )
    robustness_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Robustness against changes"
    )
    
    # Alternatives
    fallback_selectors: List[str] = Field(
        default_factory=list, 
        description="Fallback options"
    )


class HTMLAnalysisRequest(BaseModel):
    """Request for HTML analysis"""
    
    model_config = ConfigDict(
        title="HTML Analysis Request",
        description="Request configuration for HTML analysis",
        validate_assignment=True,
        extra="forbid"
    )
    
    html_content: str = Field(
        ..., 
        min_length=10, 
        description="HTML content to analyze"
    )
    target_elements: List[str] = Field(
        ..., 
        min_length=1, 
        description="Target elements to find"
    )
    page_context: Optional[str] = Field(
        None, 
        description="Page context hint (e.g., 'e-commerce', 'news')"
    )
    
    # Analysis options
    optimization_level: str = Field(
        default="balanced",
        pattern=r"^(speed|balanced|robust)$",
        description="Analysis optimization level"
    )
    max_tokens: Optional[int] = Field(
        None,
        ge=100,
        le=8000,
        description="Maximum tokens for analysis"
    )
    enable_fallbacks: bool = Field(
        default=True,
        description="Generate fallback selectors"
    )


class HTMLAnalysisResult(BaseModel):
    """Result of HTML analysis operation"""
    
    model_config = ConfigDict(
        title="HTML Analysis Result",
        description="Complete result of HTML analysis with detected patterns",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Analysis metadata
    html_size_bytes: int = Field(
        ..., 
        ge=0, 
        description="Original HTML size"
    )
    processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Analysis processing time"
    )
    model_used: str = Field(..., description="LLM model used for analysis")
    
    # Detected patterns
    detected_patterns: List[DetectedPattern] = Field(
        ..., 
        description="All detected patterns"
    )
    target_elements_found: Dict[str, DetectedPattern] = Field(
        ..., 
        description="Requested target elements"
    )
    
    # Overall metrics
    overall_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Overall analysis confidence"
    )
    page_complexity_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Page complexity (0=simple, 1=complex)"
    )
    
    # Generated selectors
    generated_selectors: Dict[str, SelectorInfo] = Field(
        default_factory=dict, 
        description="Generated selectors"
    )
    
    # Cost and performance
    tokens_used: Optional[int] = Field(
        None, 
        ge=0, 
        description="Tokens consumed"
    )
    cost_usd: Optional[float] = Field(
        None, 
        ge=0, 
        description="Analysis cost"
    )
    
    # Extracted data
    extracted_js_data: Optional[Dict[str, Any]] = Field(
        None,
        description="JavaScript data extracted from HTML"
    )


class SelectorValidationResult(BaseModel):
    """Result of selector validation against HTML"""
    
    model_config = ConfigDict(
        title="Selector Validation Result",
        description="Result of testing selector against HTML content",
        validate_assignment=True,
        extra="forbid"
    )
    
    selector: str = Field(..., description="Validated selector")
    is_valid: bool = Field(..., description="Validation result")
    match_count: int = Field(
        ..., 
        ge=0, 
        description="Number of matched elements"
    )
    
    # Validation details
    matched_elements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of matched elements"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if validation failed"
    )
    
    # Performance metrics
    selection_time_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Time taken to select elements"
    )
    stability_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Stability score of the selector"
    )


class CompleteAnalysisResult(BaseModel):
    """Complete analysis result with selectors and validation"""
    
    model_config = ConfigDict(
        title="Complete Analysis Result",
        description="Complete HTML analysis with generated and validated selectors",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Analysis results
    analysis: HTMLAnalysisResult = Field(
        ..., 
        description="HTML analysis results"
    )
    
    # Generated selectors
    selectors: Dict[str, SelectorInfo] = Field(
        ..., 
        description="Generated selectors by element name"
    )
    
    # Validation results
    validation_results: Dict[str, SelectorValidationResult] = Field(
        default_factory=dict,
        description="Validation results for each selector"
    )
    
    # Overall metrics
    overall_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Overall confidence score"
    )
    success_rate: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Selector success rate"
    )
    
    # Performance and cost
    total_processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Total processing time"
    )
    total_cost_usd: Optional[float] = Field(
        None, 
        ge=0, 
        description="Total cost"
    )
    
    # Quality metrics
    average_robustness_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Average robustness of generated selectors"
    )
    recommendation: Optional[str] = Field(
        None,
        description="Recommendation for production use"
    )
