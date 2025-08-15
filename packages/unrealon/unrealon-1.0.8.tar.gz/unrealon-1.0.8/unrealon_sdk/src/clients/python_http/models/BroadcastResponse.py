from typing import *

from pydantic import BaseModel, Field


class BroadcastResponse(BaseModel):
    """
    BroadcastResponse model
        Response model for broadcast operations.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event: str = Field(validation_alias="event")

    message_sent: bool = Field(validation_alias="message_sent")

    room: str = Field(validation_alias="room")

    success: bool = Field(validation_alias="success")
