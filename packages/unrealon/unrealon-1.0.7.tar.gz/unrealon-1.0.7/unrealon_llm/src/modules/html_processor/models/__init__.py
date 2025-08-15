"""
HTML Processor Models

Simplified universal model for HTML pattern extraction with markdown documentation.
"""

# Universal model
from .universal_model import UniversalExtractionSchema

# Processing models
from .processing_models import ProcessingInfo, ExtractionResult

__all__ = [
    # Universal model
    "UniversalExtractionSchema",
    
    # Processing models
    "ProcessingInfo", 
    "ExtractionResult",
]
