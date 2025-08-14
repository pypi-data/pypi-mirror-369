"""Option greeks event model."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from strategy.v1 import event_option_greeks_pb2

from ..conversions import optional_precise_decimal_to_decimal


class OptionGreeks(BaseModel):
    """Option Greeks and related metrics."""

    symbol: str = Field(description="Option symbol")
    delta: Optional[Decimal] = Field(default=None, description="Delta - rate of change of option price with underlying price")
    gamma: Optional[Decimal] = Field(default=None, description="Gamma - rate of change of delta with underlying price")
    theta: Optional[Decimal] = Field(default=None, description="Theta - rate of change of option price with time")
    vega: Optional[Decimal] = Field(default=None, description="Vega - rate of change of option price with volatility")
    rho: Optional[Decimal] = Field(default=None, description="Rho - rate of change of option price with interest rate")
    implied_volatility: Optional[Decimal] = Field(default=None, description="Implied volatility")
    theoretical_value: Optional[Decimal] = Field(default=None, description="Theoretical option value")
    underlying_price: Optional[Decimal] = Field(default=None, description="Current underlying price")
    interest_rate: Optional[Decimal] = Field(default=None, description="Risk-free interest rate")
    days_to_expiry: Optional[int] = Field(default=None, description="Days until expiration")

    @classmethod
    def from_proto(cls, proto: event_option_greeks_pb2.OptionGreeks) -> OptionGreeks:
        """Create from protobuf message."""
        return cls(
            symbol=proto.symbol,
            delta=optional_precise_decimal_to_decimal(proto.delta) if proto.HasField("delta") else None,
            gamma=optional_precise_decimal_to_decimal(proto.gamma) if proto.HasField("gamma") else None,
            theta=optional_precise_decimal_to_decimal(proto.theta) if proto.HasField("theta") else None,
            vega=optional_precise_decimal_to_decimal(proto.vega) if proto.HasField("vega") else None,
            rho=optional_precise_decimal_to_decimal(proto.rho) if proto.HasField("rho") else None,
            implied_volatility=optional_precise_decimal_to_decimal(proto.implied_volatility) if proto.HasField("implied_volatility") else None,
            theoretical_value=optional_precise_decimal_to_decimal(proto.theoretical_value) if proto.HasField("theoretical_value") else None,
            underlying_price=optional_precise_decimal_to_decimal(proto.underlying_price) if proto.HasField("underlying_price") else None,
            interest_rate=optional_precise_decimal_to_decimal(proto.interest_rate) if proto.HasField("interest_rate") else None,
            days_to_expiry=proto.days_to_expiry if proto.days_to_expiry else None,
        )
