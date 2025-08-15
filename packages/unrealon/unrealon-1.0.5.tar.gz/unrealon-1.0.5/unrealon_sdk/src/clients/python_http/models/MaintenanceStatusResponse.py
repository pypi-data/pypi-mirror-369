from typing import *

from pydantic import BaseModel, Field

from .MaintenanceMode import MaintenanceMode


class MaintenanceStatusResponse(BaseModel):
    """
    MaintenanceStatusResponse model
        Current maintenance status response.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    affected_services: Optional[List[str]] = Field(validation_alias="affected_services", default=None)

    data: Optional[Union[Dict[str, Any]]] = Field(validation_alias="data", default=None)

    estimated_end: Optional[str] = Field(validation_alias="estimated_end", default=None)

    grace_period_remaining: Optional[int] = Field(validation_alias="grace_period_remaining", default=None)

    maintenance_active: bool = Field(validation_alias="maintenance_active")

    message: str = Field(validation_alias="message")

    mode: Optional[Union[MaintenanceMode]] = Field(validation_alias="mode", default=None)

    reason: Optional[str] = Field(validation_alias="reason", default=None)

    request_id: Optional[str] = Field(validation_alias="request_id", default=None)

    started_at: Optional[str] = Field(validation_alias="started_at", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    timestamp: Optional[str] = Field(validation_alias="timestamp", default=None)
