from typing import *

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    HealthResponse model
        Health check response model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    components: Optional[Union[Dict[str, Any]]] = Field(validation_alias="components", default=None)

    service: str = Field(validation_alias="service")

    status: str = Field(validation_alias="status")

    timestamp: str = Field(validation_alias="timestamp")

    version: str = Field(validation_alias="version")
