"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from broker.v1 import handler_get_risk_metrics_pb2
from pydantic import BaseModel, Field

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal


class PositionRisk(BaseModel):
    """Risk metrics for a position."""

    symbol: str = Field(description="Position symbol")
    position_var: Optional[Decimal] = Field(default=None, description="Position Value at Risk")
    beta: Optional[Decimal] = Field(default=None, description="Beta relative to market")
    volatility: Optional[Decimal] = Field(default=None, description="Position volatility")
    exposure: Optional[Decimal] = Field(default=None, description="Position exposure")

    def to_proto(self) -> handler_get_risk_metrics_pb2.PositionRisk:
        """Convert to protobuf message."""
        proto = handler_get_risk_metrics_pb2.PositionRisk(symbol=self.symbol)

        if self.position_var is not None:
            proto.position_var.CopyFrom(decimal_to_precise_decimal(self.position_var, "broker"))
        if self.beta is not None:
            proto.beta.CopyFrom(decimal_to_precise_decimal(self.beta, "broker"))
        if self.volatility is not None:
            proto.volatility.CopyFrom(decimal_to_precise_decimal(self.volatility, "broker"))
        if self.exposure is not None:
            proto.exposure.CopyFrom(decimal_to_precise_decimal(self.exposure, "broker"))

        return proto

    @classmethod
    def from_proto(cls, proto: handler_get_risk_metrics_pb2.PositionRisk) -> PositionRisk:
        """Create from protobuf message."""
        return cls(
            symbol=proto.symbol,
            position_var=optional_precise_decimal_to_decimal(proto.position_var) if proto.HasField("position_var") else None,
            beta=optional_precise_decimal_to_decimal(proto.beta) if proto.HasField("beta") else None,
            volatility=optional_precise_decimal_to_decimal(proto.volatility) if proto.HasField("volatility") else None,
            exposure=optional_precise_decimal_to_decimal(proto.exposure) if proto.HasField("exposure") else None,
        )
