from typing import *

from pydantic import BaseModel, Field


class BroadcastMessageRequest(BaseModel):
    """
    BroadcastMessageRequest model
        Request to broadcast message to users.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    admin_context: Optional[Union[Dict[str, Any]]] = Field(validation_alias="admin_context", default=None)

    expires_at: Optional[str] = Field(validation_alias="expires_at", default=None)

    message: str = Field(validation_alias="message")

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata", default=None)

    persistent: Optional[bool] = Field(validation_alias="persistent", default=None)

    priority: Optional[Any] = Field(validation_alias="priority", default=None)

    request_id: Optional[str] = Field(validation_alias="request_id", default=None)

    target: Optional[Any] = Field(validation_alias="target", default=None)

    target_room: Optional[str] = Field(validation_alias="target_room", default=None)

    target_users: Optional[Union[List[str]]] = Field(validation_alias="target_users", default=None)

    title: Optional[str] = Field(validation_alias="title", default=None)
