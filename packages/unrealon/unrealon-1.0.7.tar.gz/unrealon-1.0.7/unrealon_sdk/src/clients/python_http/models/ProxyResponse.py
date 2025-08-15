from typing import *

from pydantic import BaseModel, Field

from .ProxyEndpointResponse import ProxyEndpointResponse
from .ProxyUsageStatsResponse import ProxyUsageStatsResponse


class ProxyResponse(BaseModel):
    """
    ProxyResponse model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    city: Optional[str] = Field(validation_alias="city", default=None)

    country: Optional[str] = Field(validation_alias="country", default=None)

    created_at: str = Field(validation_alias="created_at")

    display_name: Optional[str] = Field(validation_alias="display_name", default=None)

    endpoint: ProxyEndpointResponse = Field(validation_alias="endpoint")

    expires_at: Optional[str] = Field(validation_alias="expires_at", default=None)

    is_expired: Optional[bool] = Field(validation_alias="is_expired", default=None)

    is_healthy: Optional[bool] = Field(validation_alias="is_healthy", default=None)

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata", default=None)

    provider: str = Field(validation_alias="provider")

    provider_proxy_id: Optional[str] = Field(validation_alias="provider_proxy_id", default=None)

    proxy_id: str = Field(validation_alias="proxy_id")

    region: Optional[str] = Field(validation_alias="region", default=None)

    status: str = Field(validation_alias="status")

    tags: Optional[List[str]] = Field(validation_alias="tags", default=None)

    usage_stats: ProxyUsageStatsResponse = Field(validation_alias="usage_stats")
