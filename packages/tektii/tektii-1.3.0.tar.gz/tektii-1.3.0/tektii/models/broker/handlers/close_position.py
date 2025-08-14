"""Close position request and response handlers."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from broker.v1 import handler_close_position_pb2
from pydantic import BaseModel, Field

from ..conversions import decimal_to_precise_decimal
from ..types.order_type import OrderType


class ClosePositionRequest(BaseModel):
    """Request to close a position."""

    symbol: str = Field(description="Symbol of position to close")
    quantity: Optional[Decimal] = Field(default=None, description="Quantity to close (None = entire position)")
    order_type: OrderType = Field(description="Order type to use for closing")

    def to_proto(self) -> handler_close_position_pb2.ClosePositionRequest:
        """Convert to protobuf message."""
        proto = handler_close_position_pb2.ClosePositionRequest(symbol=self.symbol, order_type=self.order_type.to_proto())

        if self.quantity is not None:
            proto.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity, "broker"))

        return proto


class ClosePositionResponse(BaseModel):
    """Response from closing a position."""

    success: bool = Field(description="Whether position was closed successfully")
    order_ids: list[str] = Field(default_factory=list, description="IDs of closing orders if successful")
    message: Optional[str] = Field(default=None, description="Response message")

    @classmethod
    def from_proto(cls, proto: handler_close_position_pb2.ClosePositionResponse) -> ClosePositionResponse:
        """Create from protobuf message."""
        return cls(success=proto.accepted, order_ids=list(proto.order_ids), message=proto.reject_reason if proto.reject_reason else None)
