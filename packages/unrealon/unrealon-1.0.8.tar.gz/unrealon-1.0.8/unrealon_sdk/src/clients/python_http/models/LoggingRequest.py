from typing import *

from pydantic import BaseModel, Field

from .LogLevel import LogLevel


class LoggingRequest(BaseModel):
    """
    LoggingRequest model
        Request for logging operation.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    context: Optional[Dict[str, Any]] = Field(validation_alias="context", default=None)

    level: LogLevel = Field(validation_alias="level")

    message: str = Field(validation_alias="message")

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    source: str = Field(validation_alias="source")

    tags: Optional[List[str]] = Field(validation_alias="tags", default=None)
