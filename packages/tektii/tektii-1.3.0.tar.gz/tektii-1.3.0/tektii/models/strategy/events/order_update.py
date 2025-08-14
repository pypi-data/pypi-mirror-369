"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel, Field
from strategy.v1 import event_order_update_pb2

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal, precise_decimal_to_decimal
from ..types.order_side import OrderSide
from ..types.order_status import OrderStatus
from ..types.order_type import OrderType


class OrderUpdateEvent(BaseModel):
    """Event triggered when an order status changes."""

    order_id: str = Field(description="Unique order identifier")
    symbol: str = Field(description="Trading symbol")
    status: OrderStatus = Field(description="Current order status")
    side: OrderSide = Field(description="Order side (buy/sell)")
    order_type: OrderType = Field(description="Order type")

    quantity: Decimal = Field(description="Order quantity")
    filled_quantity: Decimal = Field(default=Decimal("0"), description="Quantity filled so far")
    remaining_quantity: Decimal = Field(default=Decimal("0"), description="Quantity remaining")

    limit_price: Optional[Decimal] = Field(default=None, description="Limit price for limit orders")
    stop_price: Optional[Decimal] = Field(default=None, description="Stop price for stop orders")
    avg_fill_price: Optional[Decimal] = Field(default=None, description="Average price of fills")

    created_at_us: int = Field(description="Order creation timestamp (microseconds)")
    updated_at_us: int = Field(description="Order update timestamp (microseconds)")

    reject_reason: Optional[str] = Field(default=None, description="Rejection reason if rejected")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    def to_proto(self) -> event_order_update_pb2.OrderUpdateEvent:
        """Convert to protobuf message."""
        proto = event_order_update_pb2.OrderUpdateEvent(
            order_id=self.order_id,
            symbol=self.symbol,
            status=self.status.to_proto(),
            side=self.side.to_proto(),
            order_type=self.order_type.to_proto(),
            created_at_us=self.created_at_us,
            updated_at_us=self.updated_at_us,
        )

        proto.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity, "strategy"))
        proto.filled_quantity.CopyFrom(decimal_to_precise_decimal(self.filled_quantity, "strategy"))
        proto.remaining_quantity.CopyFrom(decimal_to_precise_decimal(self.remaining_quantity, "strategy"))

        if self.limit_price is not None:
            proto.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price, "strategy"))
        if self.stop_price is not None:
            proto.stop_price.CopyFrom(decimal_to_precise_decimal(self.stop_price, "strategy"))
        if self.avg_fill_price is not None:
            proto.avg_fill_price.CopyFrom(decimal_to_precise_decimal(self.avg_fill_price, "strategy"))
        if self.reject_reason:
            proto.reject_reason = self.reject_reason

        # Add metadata
        for key, value in self.metadata.items():
            proto.metadata[key] = value

        return proto

    @classmethod
    def from_proto(cls, proto: event_order_update_pb2.OrderUpdateEvent) -> OrderUpdateEvent:
        """Create from protobuf message."""
        return cls(
            order_id=proto.order_id,
            symbol=proto.symbol,
            status=OrderStatus.from_proto(proto.status),
            side=OrderSide.from_proto(proto.side),
            order_type=OrderType.from_proto(proto.order_type),
            quantity=precise_decimal_to_decimal(proto.quantity),
            filled_quantity=precise_decimal_to_decimal(proto.filled_quantity),
            remaining_quantity=precise_decimal_to_decimal(proto.remaining_quantity),
            limit_price=optional_precise_decimal_to_decimal(proto.limit_price) if proto.HasField("limit_price") else None,
            stop_price=optional_precise_decimal_to_decimal(proto.stop_price) if proto.HasField("stop_price") else None,
            avg_fill_price=optional_precise_decimal_to_decimal(proto.avg_fill_price) if proto.HasField("avg_fill_price") else None,
            created_at_us=proto.created_at_us,
            updated_at_us=proto.updated_at_us,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            metadata=dict(proto.metadata),
        )
