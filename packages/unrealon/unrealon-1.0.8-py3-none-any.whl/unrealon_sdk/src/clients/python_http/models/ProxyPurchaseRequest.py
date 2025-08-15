from typing import *

from pydantic import BaseModel, Field


class ProxyPurchaseRequest(BaseModel):
    """
    ProxyPurchaseRequest model
        Request to purchase proxies.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    count: int = Field(validation_alias="count")

    country: str = Field(validation_alias="country")

    description: Optional[str] = Field(validation_alias="description", default=None)

    duration_days: int = Field(validation_alias="duration_days")

    provider: str = Field(validation_alias="provider")

    shared: Optional[bool] = Field(validation_alias="shared", default=None)
