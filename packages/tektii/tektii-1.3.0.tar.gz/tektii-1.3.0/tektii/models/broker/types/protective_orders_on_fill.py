"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, Union

from broker.v1 import handler_place_order_pb2
from pydantic import BaseModel, Field, field_validator

from ..conversions import decimal_to_precise_decimal, precise_decimal_to_decimal
from .stop_limit_order import StopLimitOrder
from .stop_order import StopOrder


class ProtectiveOrdersOnFill(BaseModel):
    """Defines protective orders to create when an order fills.

    Used to automatically create stop loss and take profit orders.
    """

    stop_loss: Optional[Union[StopOrder, StopLimitOrder]] = Field(default=None, description="Stop loss configuration")
    take_profit_price: Optional[Decimal] = Field(default=None, description="Take profit limit price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("take_profit_price")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal, None]) -> Optional[Decimal]:
        """Ensure take profit price is Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    def to_proto(self) -> "handler_place_order_pb2.ProtectiveOrdersOnFill":
        """Convert to protobuf message."""
        from broker.v1 import handler_place_order_pb2

        proto = handler_place_order_pb2.ProtectiveOrdersOnFill()

        if self.stop_loss:
            if isinstance(self.stop_loss, StopOrder):
                proto.stop.CopyFrom(self.stop_loss.to_proto())
            elif isinstance(self.stop_loss, StopLimitOrder):
                proto.stop_limit.CopyFrom(self.stop_loss.to_proto())

        if self.take_profit_price:
            proto.take_profit_price.CopyFrom(decimal_to_precise_decimal(self.take_profit_price, "broker"))

        return proto

    @classmethod
    def from_proto(cls, proto: "handler_place_order_pb2.ProtectiveOrdersOnFill") -> ProtectiveOrdersOnFill:
        """Create from protobuf message."""
        stop_loss: Optional[Union[StopOrder, StopLimitOrder]] = None
        if proto.HasField("stop"):
            stop_loss = StopOrder.from_proto(proto.stop)
        elif proto.HasField("stop_limit"):
            stop_loss = StopLimitOrder.from_proto(proto.stop_limit)

        take_profit_price = None
        if proto.HasField("take_profit_price"):
            take_profit_price = precise_decimal_to_decimal(proto.take_profit_price)

        return cls(
            stop_loss=stop_loss,
            take_profit_price=take_profit_price,
        )
