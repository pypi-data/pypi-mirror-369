from typing import *

from pydantic import BaseModel, Field


class SystemNotificationResponse(BaseModel):
    """
    SystemNotificationResponse model
        Response model for system notification broadcast.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    broadcasted: bool = Field(validation_alias="broadcasted")

    content: str = Field(validation_alias="content")

    priority: str = Field(validation_alias="priority")

    success: bool = Field(validation_alias="success")

    title: str = Field(validation_alias="title")
