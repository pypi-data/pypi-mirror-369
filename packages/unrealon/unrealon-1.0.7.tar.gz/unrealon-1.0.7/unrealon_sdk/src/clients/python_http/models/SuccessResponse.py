from typing import *

from pydantic import BaseModel, Field

from .BaseModel import BaseModel


class SuccessResponse(BaseModel):
    """
    SuccessResponse model
        Standard success response model with automatic Pydantic object serialization.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    data: Optional[Union[Dict[str, Any], BaseModel, List[BaseModel], List[Dict[str, Any]]]] = Field(
        validation_alias="data", default=None
    )

    message: Optional[str] = Field(validation_alias="message", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    timestamp: Optional[str] = Field(validation_alias="timestamp", default=None)
