from typing import *

from pydantic import BaseModel, Field

from .ProxyResponse import ProxyResponse


class ProxyListResponse(BaseModel):
    """
    ProxyListResponse model
        Response model for proxy list endpoint.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    items: List[ProxyResponse] = Field(validation_alias="items")

    total: int = Field(validation_alias="total")
