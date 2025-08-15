from typing import *

from pydantic import BaseModel, Field


class ParserRegistrationResponse(BaseModel):
    """
    ParserRegistrationResponse model
        Response DTO for parser registration.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    developer_id: Optional[str] = Field(validation_alias="developer_id", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    message: Optional[str] = Field(validation_alias="message", default=None)

    parser_id: Optional[str] = Field(validation_alias="parser_id", default=None)

    registered_services: Optional[List[str]] = Field(validation_alias="registered_services", default=None)

    success: bool = Field(validation_alias="success")
