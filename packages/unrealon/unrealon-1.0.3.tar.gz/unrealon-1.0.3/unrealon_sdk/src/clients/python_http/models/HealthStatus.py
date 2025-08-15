from typing import *

from pydantic import BaseModel, Field

from .WebSocketMetrics import WebSocketMetrics


class HealthStatus(BaseModel):
    """
    HealthStatus model
        Pydantic model for WebSocket service health status.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    active_connections: int = Field(validation_alias="active_connections")

    active_rooms: int = Field(validation_alias="active_rooms")

    connected_developers: int = Field(validation_alias="connected_developers")

    connected_parsers: int = Field(validation_alias="connected_parsers")

    error: Optional[str] = Field(validation_alias="error", default=None)

    max_connections: int = Field(validation_alias="max_connections")

    metrics: Optional[WebSocketMetrics] = Field(validation_alias="metrics", default=None)

    status: str = Field(validation_alias="status")

    websocket_server: Optional[str] = Field(validation_alias="websocket_server", default=None)
