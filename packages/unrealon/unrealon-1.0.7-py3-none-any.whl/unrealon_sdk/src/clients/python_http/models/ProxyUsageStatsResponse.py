from typing import *

from pydantic import BaseModel, Field


class ProxyUsageStatsResponse(BaseModel):
    """
    ProxyUsageStatsResponse model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    avg_response_time_ms: Optional[float] = Field(validation_alias="avg_response_time_ms", default=None)

    consecutive_failures: int = Field(validation_alias="consecutive_failures")

    failed_requests: int = Field(validation_alias="failed_requests")

    last_used_at: Optional[str] = Field(validation_alias="last_used_at", default=None)

    success_rate: float = Field(validation_alias="success_rate")

    successful_requests: int = Field(validation_alias="successful_requests")

    total_requests: int = Field(validation_alias="total_requests")
