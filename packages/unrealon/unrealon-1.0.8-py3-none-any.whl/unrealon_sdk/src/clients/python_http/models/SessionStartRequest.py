from typing import *

from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    """
    SessionStartRequest model
        Request to start a new logging session.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    auto_expire: Optional[bool] = Field(validation_alias="auto_expire", default=None)

    max_entries: Optional[int] = Field(validation_alias="max_entries", default=None)

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata", default=None)

    retention_hours: Optional[int] = Field(validation_alias="retention_hours", default=None)

    tags: Optional[List[str]] = Field(validation_alias="tags", default=None)
