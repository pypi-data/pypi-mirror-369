from typing import *

from pydantic import BaseModel, Field

from .WebSocketMetrics import WebSocketMetrics


class ConnectionStats(BaseModel):
    """
    ConnectionStats model
        Pydantic model for WebSocket connection statistics.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    active_rooms: int = Field(validation_alias="active_rooms")

    client_connections: int = Field(validation_alias="client_connections")

    max_connections: int = Field(validation_alias="max_connections")

    metrics: Optional[WebSocketMetrics] = Field(validation_alias="metrics", default=None)

    parser_connections: int = Field(validation_alias="parser_connections")

    total_connections: int = Field(validation_alias="total_connections")
