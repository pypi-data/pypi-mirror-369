from typing import *

from pydantic import BaseModel, Field


class ValidationErrorResponse(BaseModel):
    """
    ValidationErrorResponse model
        Validation error response for request validation failures.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: Optional[str] = Field(validation_alias="error", default=None)

    error_code: Optional[str] = Field(validation_alias="error_code", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    validation_errors: List[Dict[str, Any]] = Field(validation_alias="validation_errors")
