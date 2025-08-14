"""Strategy stop order model."""

from __future__ import annotations

from decimal import Decimal
from typing import Union

from broker.v1 import broker_common_pb2
from pydantic import BaseModel, Field, field_validator

from ...broker.conversions import decimal_to_precise_decimal as broker_decimal_to_precise
from ...broker.conversions import precise_decimal_to_decimal as broker_precise_to_decimal


class StopOrder(BaseModel):
    """Configuration for stop market orders."""

    stop_price: Decimal = Field(..., description="Stop trigger price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("stop_price")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal]) -> Decimal:
        """Ensure stop price is Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    def to_broker_proto(self) -> "broker_common_pb2.StopOrder":
        """Convert to broker service proto."""
        from broker.v1 import broker_common_pb2

        proto = broker_common_pb2.StopOrder()
        proto.stop_price.CopyFrom(broker_decimal_to_precise(self.stop_price))
        return proto

    @classmethod
    def from_broker_proto(cls, proto: "broker_common_pb2.StopOrder") -> StopOrder:
        """Create from broker service proto."""
        return cls(stop_price=broker_precise_to_decimal(proto.stop_price))
