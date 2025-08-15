from typing import *

from pydantic import BaseModel, Field


class LoggingResponse(BaseModel):
    """
    LoggingResponse model
        Response from logging operation.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    entry_id: Optional[str] = Field(validation_alias="entry_id", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    message: str = Field(validation_alias="message")

    session_id: str = Field(validation_alias="session_id")

    success: bool = Field(validation_alias="success")
