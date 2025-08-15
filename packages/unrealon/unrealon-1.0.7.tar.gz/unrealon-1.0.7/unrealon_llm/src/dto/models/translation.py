"""
LLM DTOs - Translation Models
Data models for translation operations
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import LanguageCode
from .core import LanguageDetection


class TranslationRequest(BaseModel):
    """Translation request model"""
    
    model_config = ConfigDict(
        title="Translation Request",
        description="Request for text translation with options",
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "text": "안녕하세요",
                "source_language": "ko",
                "target_language": "en",
                "context": "greeting"
            }
        }
    )
    
    text: str = Field(
        ..., 
        min_length=1, 
        description="Text to translate"
    )
    source_language: LanguageCode = Field(
        ..., 
        description="Source language"
    )
    target_language: LanguageCode = Field(
        ..., 
        description="Target language"
    )
    context: Optional[str] = Field(
        None, 
        description="Translation context"
    )
    
    # Processing options
    preserve_formatting: bool = Field(
        True, 
        description="Preserve original formatting"
    )
    handle_technical_terms: bool = Field(
        True, 
        description="Handle technical terms specially"
    )
    preserve_terms: Optional[List[str]] = Field(
        None,
        description="Terms to preserve without translation"
    )


class TranslationResponse(BaseModel):
    """Translation operation result"""
    
    model_config = ConfigDict(
        title="Translation Response",
        description="Complete translation result with metadata",
        validate_assignment=True,
        extra="forbid"
    )
    
    original_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    source_language: LanguageCode = Field(
        ..., 
        description="Source language used"
    )
    target_language: LanguageCode = Field(
        ..., 
        description="Target language used"
    )
    
    # Quality metrics
    translation_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Translation quality confidence"
    )
    detected_language: Optional[LanguageDetection] = Field(
        None, 
        description="Language detection result"
    )
    
    # Processing metadata
    processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Translation time"
    )
    tokens_used: Optional[int] = Field(
        None, 
        ge=0, 
        description="Tokens consumed"
    )
    cost_usd: Optional[float] = Field(
        None, 
        ge=0, 
        description="Translation cost"
    )
    cached: bool = Field(False, description="Result from cache")
    
    # Enhanced features
    alternative_translations: List[str] = Field(
        default_factory=list, 
        description="Alternative translations"
    )
    terminology_used: Dict[str, str] = Field(
        default_factory=dict, 
        description="Special terminology mappings"
    )
    
    # Quality indicators
    fluency_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Translation fluency score"
    )
    accuracy_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Translation accuracy score"
    )


class BatchTranslationRequest(BaseModel):
    """Batch translation request"""
    
    model_config = ConfigDict(
        title="Batch Translation Request",
        description="Request for batch translation of multiple texts",
        validate_assignment=True,
        extra="forbid"
    )
    
    texts: List[str] = Field(
        ..., 
        min_length=1, 
        description="Texts to translate"
    )
    source_language: LanguageCode = Field(
        ..., 
        description="Source language"
    )
    target_language: LanguageCode = Field(
        ..., 
        description="Target language"
    )
    context: Optional[str] = Field(
        None, 
        description="Translation context"
    )
    
    # Batch options
    preserve_order: bool = Field(
        True, 
        description="Preserve order of translations"
    )
    fail_on_error: bool = Field(
        False, 
        description="Fail entire batch on single error"
    )
    max_batch_size: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Maximum batch size"
    )


class BatchTranslationResponse(BaseModel):
    """Batch translation result"""
    
    model_config = ConfigDict(
        title="Batch Translation Response",
        description="Result of batch translation operation",
        validate_assignment=True,
        extra="forbid"
    )
    
    translations: List[TranslationResponse] = Field(
        ..., 
        description="Individual translation results"
    )
    
    # Batch metrics
    total_texts: int = Field(
        ..., 
        ge=1, 
        description="Total number of texts processed"
    )
    successful_translations: int = Field(
        ..., 
        ge=0, 
        description="Number of successful translations"
    )
    failed_translations: int = Field(
        ..., 
        ge=0, 
        description="Number of failed translations"
    )
    
    # Performance metrics
    total_processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Total processing time"
    )
    average_time_per_translation: float = Field(
        ..., 
        ge=0, 
        description="Average time per translation"
    )
    
    # Cost metrics
    total_tokens_used: int = Field(
        ..., 
        ge=0, 
        description="Total tokens consumed"
    )
    total_cost_usd: float = Field(
        ..., 
        ge=0, 
        description="Total cost"
    )
    
    # Quality metrics
    average_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Average translation confidence"
    )
    cache_hit_rate: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Cache hit rate"
    )
    
    # Error information
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of any errors that occurred"
    )


class JSONTranslationRequest(BaseModel):
    """Request for JSON structure translation"""
    
    model_config = ConfigDict(
        title="JSON Translation Request",
        description="Request for translating JSON data while preserving structure",
        validate_assignment=True,
        extra="forbid"
    )
    
    json_data: Dict[str, Any] = Field(
        ..., 
        description="JSON data to translate"
    )
    source_language: LanguageCode = Field(
        ..., 
        description="Source language"
    )
    target_language: LanguageCode = Field(
        ..., 
        description="Target language"
    )
    
    # Translation options
    preserve_keys: List[str] = Field(
        default_factory=list,
        description="Keys to preserve without translation"
    )
    translate_keys: bool = Field(
        False,
        description="Whether to translate object keys"
    )
    preserve_types: bool = Field(
        True,
        description="Preserve data types (numbers, booleans, etc.)"
    )
    
    # Context options
    data_context: Optional[str] = Field(
        None,
        description="Context about the data (e.g., 'product_data', 'user_profile')"
    )
    field_contexts: Optional[Dict[str, str]] = Field(
        None,
        description="Specific context for individual fields"
    )


class JSONTranslationResponse(BaseModel):
    """JSON translation result"""
    
    model_config = ConfigDict(
        title="JSON Translation Response",
        description="Result of JSON structure translation",
        validate_assignment=True,
        extra="forbid"
    )
    
    original_data: Dict[str, Any] = Field(
        ..., 
        description="Original JSON data"
    )
    translated_data: Dict[str, Any] = Field(
        ..., 
        description="Translated JSON data"
    )
    
    # Translation metadata
    fields_translated: List[str] = Field(
        ..., 
        description="List of fields that were translated"
    )
    fields_preserved: List[str] = Field(
        ..., 
        description="List of fields that were preserved"
    )
    
    # Quality metrics
    translation_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Overall translation confidence"
    )
    structure_preserved: bool = Field(
        ..., 
        description="Whether structure was preserved"
    )
    
    # Performance metrics
    processing_time_seconds: float = Field(
        ..., 
        ge=0, 
        description="Processing time"
    )
    total_tokens_used: int = Field(
        ..., 
        ge=0, 
        description="Total tokens used"
    )
    cost_usd: float = Field(
        ..., 
        ge=0, 
        description="Translation cost"
    )
    
    # Detailed results
    field_results: Dict[str, TranslationResponse] = Field(
        default_factory=dict,
        description="Individual translation results for each field"
    )
    
    # Error tracking
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Any errors encountered during translation"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Translation warnings"
    )
