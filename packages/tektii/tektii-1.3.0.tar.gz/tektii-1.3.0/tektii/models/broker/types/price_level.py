"""Price level model for market depth."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ..conversions import decimal_to_precise_decimal, precise_decimal_to_decimal

if TYPE_CHECKING:
    from broker.v1 import handler_get_market_depth_pb2


class PriceLevel(BaseModel):
    """Represents a level in the order book.

    Used for market depth/Level 2 data.
    """

    price: Decimal = Field(..., description="Price level")
    size: Decimal = Field(..., description="Total size at this level")
    order_count: Optional[int] = Field(None, description="Number of orders at this level")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("price", "size")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal]) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def notional_value(self) -> Decimal:
        """Notional value at this price level.

        Returns:
            Price * size
        """
        return self.price * self.size

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"PriceLevel({self.price:.4f}: {self.size:.2f})"

    @classmethod
    def from_proto(cls, proto: "handler_get_market_depth_pb2.PriceLevel") -> PriceLevel:
        """Create from protobuf message.

        Args:
            proto: Protobuf PriceLevel message

        Returns:
            PriceLevel instance
        """
        return cls(
            price=precise_decimal_to_decimal(proto.price),
            size=precise_decimal_to_decimal(proto.size),
            order_count=proto.order_count if proto.order_count > 0 else None,
        )

    def to_proto(self) -> "handler_get_market_depth_pb2.PriceLevel":
        """Convert to protobuf message.

        Returns:
            Protobuf PriceLevel message
        """
        from broker.v1 import handler_get_market_depth_pb2

        proto = handler_get_market_depth_pb2.PriceLevel()
        proto.price.CopyFrom(decimal_to_precise_decimal(self.price))
        proto.size.CopyFrom(decimal_to_precise_decimal(self.size))
        if self.order_count is not None:
            proto.order_count = self.order_count
        return proto
