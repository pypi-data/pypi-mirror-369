from typing import *

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    ErrorResponse model
        Standard error response model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    details: Optional[Union[Dict[str, Any]]] = Field(validation_alias="details", default=None)

    error: str = Field(validation_alias="error")

    error_code: Optional[str] = Field(validation_alias="error_code", default=None)

    message: Optional[str] = Field(validation_alias="message", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    timestamp: Optional[str] = Field(validation_alias="timestamp", default=None)
