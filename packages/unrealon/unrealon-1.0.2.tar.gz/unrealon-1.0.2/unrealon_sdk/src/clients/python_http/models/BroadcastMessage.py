from typing import *

from pydantic import BaseModel, Field


class BroadcastMessage(BaseModel):
    """
    BroadcastMessage model
        Message to broadcast to a room.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    data: Dict[str, Any] = Field(validation_alias="data")

    event: Optional[str] = Field(validation_alias="event", default=None)
