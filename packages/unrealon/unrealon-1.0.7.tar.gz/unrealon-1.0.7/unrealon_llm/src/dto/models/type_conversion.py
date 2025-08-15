"""
LLM DTOs - Type Conversion Models
Data models for schema generation and type conversion
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import DataType, SchemaFormat


class FieldAnalysis(BaseModel):
    """Analysis of individual JSON field"""
    
    model_config = ConfigDict(
        title="Field Analysis",
        description="Detailed analysis of individual data field",
        validate_assignment=True,
        extra="forbid"
    )
    
    field_name: str = Field(..., description="Field name")
    detected_type: DataType = Field(..., description="Detected data type")
    type_confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Type detection confidence"
    )
    
    # Statistics
    sample_values: List[Any] = Field(
        default_factory=list, 
        description="Sample values"
    )
    null_count: int = Field(0, ge=0, description="Number of null values")
    unique_values: int = Field(
        ..., 
        ge=0, 
        description="Number of unique values"
    )
    
    # Patterns
    value_patterns: List[str] = Field(
        default_factory=list, 
        description="Detected value patterns"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Validation constraints"
    )
    
    # Metadata
    is_required: bool = Field(
        True,
        description="Whether field is required"
    )
    default_value: Optional[Any] = Field(
        None,
        description="Default value if field is optional"
    )
    description: Optional[str] = Field(
        None,
        description="Field description"
    )


class StructureAnalysis(BaseModel):
    """JSON structure analysis result"""
    
    model_config = ConfigDict(
        title="Structure Analysis",
        description="Complete analysis of JSON data structure",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Structure metrics
    total_fields: int = Field(
        ..., 
        ge=0, 
        description="Total number of fields"
    )
    nested_levels: int = Field(
        ..., 
        ge=0, 
        description="Maximum nesting depth"
    )
    array_fields: int = Field(
        ..., 
        ge=0, 
        description="Number of array fields"
    )
    object_fields: int = Field(
        ..., 
        ge=0, 
        description="Number of object fields"
    )
    
    # Field analysis
    field_analyses: List[FieldAnalysis] = Field(
        ..., 
        description="Individual field analyses"
    )
    type_distribution: Dict[DataType, int] = Field(
        ..., 
        description="Distribution of data types"
    )
    
    # Schema generation
    inferred_schema: Dict[str, Any] = Field(
        ..., 
        description="Generated JSON schema"
    )
    validation_rules: List[str] = Field(
        default_factory=list, 
        description="Suggested validation rules"
    )
    
    # Recommendations
    optimization_suggestions: List[str] = Field(
        default_factory=list, 
        description="Structure optimization suggestions"
    )
    normalization_needed: bool = Field(
        False, 
        description="Whether normalization is recommended"
    )


class PydanticSchema(BaseModel):
    """Generated Pydantic schema"""
    
    model_config = ConfigDict(
        title="Pydantic Schema",
        description="Generated Pydantic model with complete code",
        validate_assignment=True,
        extra="forbid"
    )
    
    class_name: str = Field(
        ..., 
        min_length=1, 
        description="Generated class name"
    )
    python_code: str = Field(
        ..., 
        min_length=1, 
        description="Complete Python class code"
    )
    imports: List[str] = Field(
        default_factory=list, 
        description="Required imports"
    )
    
    # Validation
    validation_rules: List[str] = Field(
        default_factory=list, 
        description="Validation rules applied"
    )
    field_descriptions: Dict[str, str] = Field(
        default_factory=dict, 
        description="Field documentation"
    )
    
    # Metadata
    generated_at: datetime = Field(
        default_factory=datetime.now, 
        description="Generation timestamp"
    )
    schema_version: str = Field("2.0", description="Pydantic version used")
    
    # Quality metrics
    complexity_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Schema complexity score"
    )
    validation_coverage: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Validation rule coverage"
    )


class TypeScriptSchema(BaseModel):
    """Generated TypeScript schema"""
    
    model_config = ConfigDict(
        title="TypeScript Schema",
        description="Generated TypeScript interface with types",
        validate_assignment=True,
        extra="forbid"
    )
    
    interface_name: str = Field(
        ..., 
        min_length=1, 
        description="Interface name"
    )
    typescript_code: str = Field(
        ..., 
        min_length=1, 
        description="Complete TypeScript interface"
    )
    
    # Additional types
    enum_definitions: List[str] = Field(
        default_factory=list, 
        description="Generated enum definitions"
    )
    utility_types: List[str] = Field(
        default_factory=list, 
        description="Utility type definitions"
    )
    
    # Documentation
    field_comments: Dict[str, str] = Field(
        default_factory=dict, 
        description="Field documentation"
    )
    jsdoc_comments: List[str] = Field(
        default_factory=list, 
        description="JSDoc comments"
    )
    
    # Metadata
    generated_at: datetime = Field(
        default_factory=datetime.now, 
        description="Generation timestamp"
    )
    typescript_version: str = Field(
        "5.0", 
        description="TypeScript version compatibility"
    )


class SchemaGenerationRequest(BaseModel):
    """Request for schema generation"""
    
    model_config = ConfigDict(
        title="Schema Generation Request",
        description="Request for generating schemas from data",
        validate_assignment=True,
        extra="forbid"
    )
    
    data: Dict[str, Any] = Field(
        ..., 
        description="Source data for schema generation"
    )
    schema_format: SchemaFormat = Field(
        ..., 
        description="Target schema format"
    )
    
    # Generation options
    class_name: Optional[str] = Field(
        None,
        description="Custom class/interface name"
    )
    namespace: Optional[str] = Field(
        None,
        description="Namespace for generated code"
    )
    strict_validation: bool = Field(
        True,
        description="Generate strict validation rules"
    )
    
    # Documentation options
    generate_docs: bool = Field(
        True,
        description="Generate field documentation"
    )
    include_examples: bool = Field(
        False,
        description="Include example values in documentation"
    )
    
    # Additional context
    data_context: Optional[str] = Field(
        None,
        description="Context about the data structure"
    )
    field_contexts: Optional[Dict[str, str]] = Field(
        None,
        description="Context for specific fields"
    )


class SchemaGenerationResponse(BaseModel):
    """Response for schema generation"""
    
    model_config = ConfigDict(
        title="Schema Generation Response",
        description="Complete schema generation result",
        validate_assignment=True,
        extra="forbid"
    )
    
    # Generated schemas
    pydantic_schema: Optional[PydanticSchema] = Field(
        None,
        description="Generated Pydantic schema"
    )
    typescript_schema: Optional[TypeScriptSchema] = Field(
        None,
        description="Generated TypeScript schema"
    )
    json_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="Generated JSON schema"
    )
    
    # Analysis results
    structure_analysis: StructureAnalysis = Field(
        ...,
        description="Structure analysis results"
    )
    
    # Generation metadata
    schema_format: SchemaFormat = Field(
        ...,
        description="Generated schema format"
    )
    generation_time_seconds: float = Field(
        ...,
        ge=0,
        description="Time taken to generate schema"
    )
    
    # Quality metrics
    schema_quality_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Overall schema quality score"
    )
    validation_completeness: float = Field(
        ...,
        ge=0,
        le=1,
        description="Validation rule completeness"
    )
    
    # Cost and performance
    tokens_used: int = Field(
        ...,
        ge=0,
        description="Tokens consumed for generation"
    )
    cost_usd: float = Field(
        ...,
        ge=0,
        description="Generation cost"
    )
    
    # Recommendations
    optimization_recommendations: List[str] = Field(
        default_factory=list,
        description="Schema optimization recommendations"
    )
    usage_recommendations: List[str] = Field(
        default_factory=list,
        description="Usage recommendations"
    )


class ConversionRequest(BaseModel):
    """Request for type conversion between formats"""
    
    model_config = ConfigDict(
        title="Conversion Request",
        description="Request for converting between schema formats",
        validate_assignment=True,
        extra="forbid"
    )
    
    source_schema: str = Field(
        ...,
        description="Source schema code"
    )
    source_format: SchemaFormat = Field(
        ...,
        description="Source schema format"
    )
    target_format: SchemaFormat = Field(
        ...,
        description="Target schema format"
    )
    
    # Conversion options
    preserve_validation: bool = Field(
        True,
        description="Preserve validation rules during conversion"
    )
    preserve_documentation: bool = Field(
        True,
        description="Preserve field documentation"
    )
    strict_types: bool = Field(
        True,
        description="Use strict type definitions"
    )


class ConversionResponse(BaseModel):
    """Response for type conversion"""
    
    model_config = ConfigDict(
        title="Conversion Response",
        description="Result of schema format conversion",
        validate_assignment=True,
        extra="forbid"
    )
    
    converted_schema: str = Field(
        ...,
        description="Converted schema code"
    )
    target_format: SchemaFormat = Field(
        ...,
        description="Target format"
    )
    
    # Conversion metadata
    conversion_time_seconds: float = Field(
        ...,
        ge=0,
        description="Conversion processing time"
    )
    features_preserved: List[str] = Field(
        ...,
        description="Features preserved during conversion"
    )
    features_lost: List[str] = Field(
        default_factory=list,
        description="Features lost during conversion"
    )
    
    # Quality metrics
    conversion_accuracy: float = Field(
        ...,
        ge=0,
        le=1,
        description="Conversion accuracy score"
    )
    
    # Warnings and recommendations
    warnings: List[str] = Field(
        default_factory=list,
        description="Conversion warnings"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Usage recommendations for converted schema"
    )
