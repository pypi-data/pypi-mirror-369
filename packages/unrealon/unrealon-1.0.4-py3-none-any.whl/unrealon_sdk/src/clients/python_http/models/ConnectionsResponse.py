from typing import *

from pydantic import BaseModel, Field


class ConnectionsResponse(BaseModel):
    """
    ConnectionsResponse model
        Response model for connections information.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    connected_developers: List[str] = Field(validation_alias="connected_developers")

    connected_parsers: List[str] = Field(validation_alias="connected_parsers")

    total_developers: int = Field(validation_alias="total_developers")

    total_parsers: int = Field(validation_alias="total_parsers")
