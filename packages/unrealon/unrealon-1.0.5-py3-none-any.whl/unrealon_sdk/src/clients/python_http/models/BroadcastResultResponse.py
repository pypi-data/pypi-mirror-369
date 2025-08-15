from typing import *

from pydantic import BaseModel, Field

from .BroadcastDeliveryStats import BroadcastDeliveryStats


class BroadcastResultResponse(BaseModel):
    """
    BroadcastResultResponse model
        Response from broadcast operation.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    broadcast_id: str = Field(validation_alias="broadcast_id")

    data: Optional[Union[Dict[str, Any]]] = Field(validation_alias="data", default=None)

    delivery_stats: BroadcastDeliveryStats = Field(validation_alias="delivery_stats")

    estimated_delivery_time: Optional[str] = Field(validation_alias="estimated_delivery_time", default=None)

    message: str = Field(validation_alias="message")

    request_id: Optional[str] = Field(validation_alias="request_id", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    target_info: Dict[str, Any] = Field(validation_alias="target_info")

    timestamp: Optional[str] = Field(validation_alias="timestamp", default=None)
