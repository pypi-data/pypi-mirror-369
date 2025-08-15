from typing import *

from pydantic import BaseModel, Field


class ServiceRegistrationDto(BaseModel):
    """
    ServiceRegistrationDto model
        DTO for service registration.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    capabilities: Optional[Dict[str, Any]] = Field(validation_alias="capabilities", default=None)

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    service_id: str = Field(validation_alias="service_id")

    service_name: str = Field(validation_alias="service_name")

    service_type: str = Field(validation_alias="service_type")
