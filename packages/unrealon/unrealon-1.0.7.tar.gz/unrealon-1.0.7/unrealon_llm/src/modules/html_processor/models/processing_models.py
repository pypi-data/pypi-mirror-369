"""
Processing Models for HTML Processing

Pydantic models for processing metadata and results.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProcessingInfo(BaseModel):
    """Processing metadata and statistics"""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        title="Processing Information"
    )
    
    original_html_size: int = Field(..., description="Original HTML size in bytes")
    cleaned_html_size: int = Field(..., description="Cleaned HTML size in bytes")
    cleaning_stats: Dict[str, Any] = Field(..., description="HTML cleaning statistics")
    extracted_js_data: Dict[str, Any] = Field(..., description="Extracted JavaScript data")
    processor_type: str = Field(..., description="Type of processor used")
    llm_model: str = Field(..., description="LLM model used for extraction")
    tokens_used: int = Field(..., description="Total tokens used in LLM request")
    cost_usd: float = Field(..., description="Cost of LLM request in USD")


class ExtractionResult(BaseModel):
    """Complete extraction result with metadata"""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        title="Extraction Result"
    )
    
    extraction_result: Dict[str, Any] = Field(..., description="Raw extraction patterns")
    processing_info: ProcessingInfo = Field(..., description="Processing metadata")
