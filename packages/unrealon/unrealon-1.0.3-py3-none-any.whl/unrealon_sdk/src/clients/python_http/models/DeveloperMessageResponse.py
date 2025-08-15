from typing import *

from pydantic import BaseModel, Field


class DeveloperMessageResponse(BaseModel):
    """
    DeveloperMessageResponse model
        Response model for developer message operations.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    developer_id: str = Field(validation_alias="developer_id")

    event: str = Field(validation_alias="event")

    message_sent: bool = Field(validation_alias="message_sent")

    sessions_reached: int = Field(validation_alias="sessions_reached")

    success: bool = Field(validation_alias="success")
