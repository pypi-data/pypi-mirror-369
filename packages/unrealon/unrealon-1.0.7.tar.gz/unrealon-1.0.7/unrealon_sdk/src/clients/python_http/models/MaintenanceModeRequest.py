from typing import *

from pydantic import BaseModel, Field


class MaintenanceModeRequest(BaseModel):
    """
    MaintenanceModeRequest model
        Request to manage maintenance mode.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    admin_context: Optional[Union[Dict[str, Any]]] = Field(validation_alias="admin_context", default=None)

    affected_services: Optional[Union[List[str]]] = Field(validation_alias="affected_services", default=None)

    enable: bool = Field(validation_alias="enable")

    estimated_duration_minutes: Optional[int] = Field(
        validation_alias="estimated_duration_minutes", default=None
    )

    grace_period_minutes: Optional[int] = Field(validation_alias="grace_period_minutes", default=None)

    mode: Optional[Any] = Field(validation_alias="mode", default=None)

    notify_users: Optional[bool] = Field(validation_alias="notify_users", default=None)

    reason: str = Field(validation_alias="reason")

    request_id: Optional[str] = Field(validation_alias="request_id", default=None)
