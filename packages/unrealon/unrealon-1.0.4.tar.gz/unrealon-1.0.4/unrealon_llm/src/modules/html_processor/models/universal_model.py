"""
Universal HTML Processing Model

Single simplified Pydantic model for any HTML page extraction with markdown documentation.
"""

from typing import Dict, List, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


class UniversalExtractionSchema(BaseModel):
    """Universal HTML page extraction schema with markdown documentation"""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",  # Allow extra fields for flexibility
        title="Universal Extraction Schema"
    )
    
    # LLM analysis results
    detected_item_type: str = Field(
        ...,
        description="Auto-detected type of page (product, listing, article, service, etc.)"
    )
    extraction_strategy: str = Field(
        ...,
        description="Brief description of extraction strategy"
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Overall extraction confidence"
    )
    
    # Simple CSS selectors organized by field
    selectors: Dict[str, List[str]] = Field(
        ...,
        description="CSS selectors organized by field name (title, price, description, items_container, etc.)"
    )
    
    # Comprehensive markdown documentation
    documentation: str = Field(
        ...,
        description="Markdown documentation with examples, explanations, and extraction guidance"
    )
    
    @field_validator('selectors', mode='before')
    @classmethod
    def convert_strings_to_lists(cls, v):
        """Convert string selectors to lists automatically"""
        if isinstance(v, dict):
            for key, value in v.items():
                if isinstance(value, str):
                    v[key] = [value]
        return v
