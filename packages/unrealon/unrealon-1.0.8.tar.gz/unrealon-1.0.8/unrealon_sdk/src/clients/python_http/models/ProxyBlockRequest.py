from typing import *

from pydantic import BaseModel, Field


class ProxyBlockRequest(BaseModel):
    """
    ProxyBlockRequest model
        Request to report blocked proxy.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    parser_id: str = Field(validation_alias="parser_id")

    proxy_id: str = Field(validation_alias="proxy_id")

    reason: Optional[str] = Field(validation_alias="reason", default=None)
