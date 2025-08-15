from typing import *

from pydantic import BaseModel, Field


class BroadcastDeliveryStats(BaseModel):
    """
    BroadcastDeliveryStats model
        Broadcast delivery statistics.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    data: Optional[Union[Dict[str, Any]]] = Field(validation_alias="data", default=None)

    delivered: int = Field(validation_alias="delivered")

    delivery_rate: float = Field(validation_alias="delivery_rate")

    failed: int = Field(validation_alias="failed")

    message: str = Field(validation_alias="message")

    pending: int = Field(validation_alias="pending")

    request_id: Optional[str] = Field(validation_alias="request_id", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    timestamp: Optional[str] = Field(validation_alias="timestamp", default=None)

    total_targeted: int = Field(validation_alias="total_targeted")
