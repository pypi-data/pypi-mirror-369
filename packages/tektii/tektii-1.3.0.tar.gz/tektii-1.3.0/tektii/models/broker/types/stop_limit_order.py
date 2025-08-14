"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Union

from broker.v1 import broker_common_pb2
from pydantic import BaseModel, Field, field_validator

from ..conversions import decimal_to_precise_decimal, precise_decimal_to_decimal


class StopLimitOrder(BaseModel):
    """Configuration for stop limit orders."""

    stop_price: Decimal = Field(..., description="Stop trigger price")
    limit_price: Decimal = Field(..., description="Limit price after stop triggers")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("stop_price", "limit_price")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal]) -> Decimal:
        """Ensure prices are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    def to_proto(self) -> "broker_common_pb2.StopLimitOrder":
        """Convert to protobuf message."""
        from broker.v1 import broker_common_pb2

        proto = broker_common_pb2.StopLimitOrder()
        proto.stop_price.CopyFrom(decimal_to_precise_decimal(self.stop_price, "broker"))
        proto.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price, "broker"))
        return proto

    @classmethod
    def from_proto(cls, proto: "broker_common_pb2.StopLimitOrder") -> StopLimitOrder:
        """Create from protobuf message."""
        return cls(
            stop_price=precise_decimal_to_decimal(proto.stop_price),
            limit_price=precise_decimal_to_decimal(proto.limit_price),
        )
