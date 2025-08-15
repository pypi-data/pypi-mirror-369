from typing import *

from pydantic import BaseModel, Field


class ParserMessageResponse(BaseModel):
    """
    ParserMessageResponse model
        Response model for parser message operations.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event: str = Field(validation_alias="event")

    message_sent: bool = Field(validation_alias="message_sent")

    parser_id: str = Field(validation_alias="parser_id")

    success: bool = Field(validation_alias="success")
