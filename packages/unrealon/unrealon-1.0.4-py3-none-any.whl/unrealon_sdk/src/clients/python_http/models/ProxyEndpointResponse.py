from typing import *

from pydantic import BaseModel, Field


class ProxyEndpointResponse(BaseModel):
    """
    ProxyEndpointResponse model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    connection_string: Optional[str] = Field(validation_alias="connection_string", default=None)

    host: str = Field(validation_alias="host")

    port: int = Field(validation_alias="port")

    protocol: str = Field(validation_alias="protocol")
