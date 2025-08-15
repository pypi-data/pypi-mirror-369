from typing import *

from pydantic import BaseModel, Field


class ProxyRotationRequest(BaseModel):
    """
    ProxyRotationRequest model
        Request for proxy rotation via API.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    country: Optional[str] = Field(validation_alias="country", default=None)

    exclude_proxy_ids: Optional[List[str]] = Field(validation_alias="exclude_proxy_ids", default=None)

    force_rotation: Optional[bool] = Field(validation_alias="force_rotation", default=None)

    parser_id: str = Field(validation_alias="parser_id")

    strategy: Optional[str] = Field(validation_alias="strategy", default=None)
