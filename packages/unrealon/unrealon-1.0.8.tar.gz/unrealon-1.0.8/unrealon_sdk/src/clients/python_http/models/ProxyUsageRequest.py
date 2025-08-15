from typing import *

from pydantic import BaseModel, Field


class ProxyUsageRequest(BaseModel):
    """
    ProxyUsageRequest model
        Request to record proxy usage.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error_reason: Optional[str] = Field(validation_alias="error_reason", default=None)

    response_time_ms: Optional[float] = Field(validation_alias="response_time_ms", default=None)

    success: bool = Field(validation_alias="success")
