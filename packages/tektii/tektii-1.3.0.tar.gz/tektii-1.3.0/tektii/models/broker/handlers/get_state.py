"""Get broker state request and response handlers."""

from __future__ import annotations

from typing import Optional

from broker.v1 import handler_get_state_pb2
from pydantic import BaseModel, Field

from ..types.account import Account
from ..types.order import Order
from ..types.position import Position


class StateRequest(BaseModel):
    """Request for current broker state.

    Used to query positions, orders, and account information.
    """

    include_positions: bool = Field(default=True, description="Include current positions in response")
    include_orders: bool = Field(default=True, description="Include orders in response")
    include_account: bool = Field(default=True, description="Include account state in response")

    def to_proto(self) -> handler_get_state_pb2.GetStateRequest:
        """Convert to protobuf message."""
        return handler_get_state_pb2.GetStateRequest(
            include_positions=self.include_positions,
            include_orders=self.include_orders,
            include_account=self.include_account,
        )


class StateResponse(BaseModel):
    """Response containing current broker state."""

    positions: dict[str, Position] = Field(default_factory=dict, description="Current positions by symbol")
    orders: dict[str, Order] = Field(default_factory=dict, description="Orders by order ID")
    account: Optional[Account] = Field(default=None, description="Account information")
    timestamp_us: int = Field(description="State snapshot timestamp in microseconds")

    @classmethod
    def from_proto(cls, proto: handler_get_state_pb2.GetStateResponse) -> StateResponse:
        """Create from protobuf message."""
        return cls(
            positions={symbol: Position.from_proto(p) for symbol, p in proto.positions.items()},
            orders={order_id: Order.from_proto(o) for order_id, o in proto.orders.items()},
            account=Account.from_proto(proto.account) if proto.HasField("account") else None,
            timestamp_us=proto.timestamp_us,
        )
