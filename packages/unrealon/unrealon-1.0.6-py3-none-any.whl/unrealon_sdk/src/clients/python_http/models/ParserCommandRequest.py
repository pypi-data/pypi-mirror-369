from typing import *

from pydantic import BaseModel, Field


class ParserCommandRequest(BaseModel):
    """
    ParserCommandRequest model
        Request model for sending commands to parsers.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    callback_url: Optional[str] = Field(validation_alias="callback_url", default=None)

    command: str = Field(validation_alias="command")

    metadata: Optional[Union[Dict[str, Any]]] = Field(validation_alias="metadata", default=None)

    parameters: Optional[Dict[str, Any]] = Field(validation_alias="parameters", default=None)

    priority: Optional[str] = Field(validation_alias="priority", default=None)

    timeout: Optional[int] = Field(validation_alias="timeout", default=None)
