"""Cancel order request and response handlers."""

from __future__ import annotations

from typing import Optional

from broker.v1 import handler_cancel_order_pb2
from pydantic import BaseModel, Field

from ..types.order_status import OrderStatus


class CancelOrderRequest(BaseModel):
    """Request to cancel an order."""

    order_id: str = Field(description="ID of order to cancel")

    def to_proto(self) -> handler_cancel_order_pb2.CancelOrderRequest:
        """Convert to protobuf message."""
        return handler_cancel_order_pb2.CancelOrderRequest(order_id=self.order_id)


class CancelOrderResponse(BaseModel):
    """Response from canceling an order."""

    success: bool = Field(description="Whether cancellation was successful")
    message: Optional[str] = Field(default=None, description="Response message")
    order_status: Optional[OrderStatus] = Field(default=None, description="Final order status")

    @classmethod
    def from_proto(cls, proto: handler_cancel_order_pb2.CancelOrderResponse) -> CancelOrderResponse:
        """Create from protobuf message."""
        return cls(
            success=proto.accepted,
            message=proto.reject_reason if proto.reject_reason else None,
            order_status=OrderStatus.from_proto(proto.previous_status) if proto.HasField("previous_status") else None,
        )
