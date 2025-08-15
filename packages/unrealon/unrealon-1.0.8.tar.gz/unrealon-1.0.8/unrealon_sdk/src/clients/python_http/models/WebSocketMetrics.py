from typing import *

from pydantic import BaseModel, Field


class WebSocketMetrics(BaseModel):
    """
    WebSocketMetrics model
        Pydantic model for WebSocket performance metrics.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    connections_closed: Optional[int] = Field(validation_alias="connections_closed", default=None)

    connections_opened: Optional[int] = Field(validation_alias="connections_opened", default=None)

    messages_received: Optional[int] = Field(validation_alias="messages_received", default=None)

    messages_sent: Optional[int] = Field(validation_alias="messages_sent", default=None)
