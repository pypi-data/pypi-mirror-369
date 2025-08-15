from typing import *

from pydantic import BaseModel, Field

from .ParserType import ParserType
from .ServiceRegistrationDto import ServiceRegistrationDto


class ParserRegistrationRequest(BaseModel):
    """
    ParserRegistrationRequest model
        Request DTO for parser registration.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    api_key: str = Field(validation_alias="api_key")

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata", default=None)

    parser_id: str = Field(validation_alias="parser_id")

    parser_name: str = Field(validation_alias="parser_name")

    parser_type: ParserType = Field(validation_alias="parser_type")

    services: Optional[List[Optional[ServiceRegistrationDto]]] = Field(validation_alias="services", default=None)
