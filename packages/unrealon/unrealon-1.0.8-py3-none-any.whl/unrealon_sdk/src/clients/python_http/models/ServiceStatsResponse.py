from typing import *

from pydantic import BaseModel, Field


class ServiceStatsResponse(BaseModel):
    """
    ServiceStatsResponse model
        Base model for service statistics responses.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    additional_metrics: Optional[Dict[str, Any]] = Field(validation_alias="additional_metrics", default=None)

    error_rate: Optional[float] = Field(validation_alias="error_rate", default=None)

    errors_encountered: Optional[int] = Field(validation_alias="errors_encountered", default=None)

    initialized: bool = Field(validation_alias="initialized")

    last_operation: Optional[str] = Field(validation_alias="last_operation", default=None)

    operations_performed: Optional[int] = Field(validation_alias="operations_performed", default=None)

    service_name: str = Field(validation_alias="service_name")

    status: Optional[str] = Field(validation_alias="status", default=None)

    uptime_seconds: Optional[float] = Field(validation_alias="uptime_seconds", default=None)
