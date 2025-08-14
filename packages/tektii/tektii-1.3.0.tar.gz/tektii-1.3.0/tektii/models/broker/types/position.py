"""Position model and related types."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, Union

from broker.v1 import broker_common_pb2
from pydantic import BaseModel, Field, field_validator

from ..conversions import decimal_to_precise_decimal, precise_decimal_to_decimal
from .broker import Broker


class Position(BaseModel):
    """Represents a current position in a trading account.

    A position tracks the quantity and value of securities held,
    along with profit/loss information.
    """

    symbol: str = Field(..., description="Trading symbol")
    quantity: Decimal = Field(..., description="Position size (positive=long, negative=short)")
    avg_price: Decimal = Field(..., description="Average entry price")
    market_value: Decimal = Field(..., description="Current market value of position")
    unrealized_pnl: Decimal = Field(..., description="Unrealized profit/loss")
    realized_pnl: Decimal = Field(..., description="Realized profit/loss")
    current_price: Decimal = Field(..., description="Current market price")
    broker: Optional[Broker] = Field(None, description="Broker/venue for this position")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "avg_price", "market_value", "unrealized_pnl", "realized_pnl", "current_price")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal]) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def is_long(self) -> bool:
        """Check if this is a long position.

        Returns:
            True if position quantity is positive
        """
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if this is a short position.

        Returns:
            True if position quantity is negative
        """
        return self.quantity < 0

    @property
    def total_pnl(self) -> Decimal:
        """Total profit and loss for this position.

        Returns:
            Total profit/loss
        """
        return self.realized_pnl + self.unrealized_pnl

    @property
    def return_percentage(self) -> Decimal:
        """Return percentage based on the cost basis.

        Returns:
            Return as percentage of investment
        """
        if self.avg_price == 0:
            return Decimal(0)

        cost_basis = abs(self.quantity) * self.avg_price
        if cost_basis == 0:
            return Decimal(0)

        return (self.total_pnl / cost_basis) * 100

    @classmethod
    def from_proto(cls, proto: "broker_common_pb2.Position") -> Position:
        """Create Position from broker service proto.

        Args:
            proto: Position proto from broker service

        Returns:
            Position model instance
        """
        return cls(
            symbol=proto.symbol,
            quantity=precise_decimal_to_decimal(proto.quantity),
            avg_price=precise_decimal_to_decimal(proto.avg_price),
            market_value=precise_decimal_to_decimal(proto.market_value),
            unrealized_pnl=precise_decimal_to_decimal(proto.unrealized_pnl),
            realized_pnl=precise_decimal_to_decimal(proto.realized_pnl),
            current_price=precise_decimal_to_decimal(proto.current_price),
            broker=None,
        )

    def to_proto(self) -> "broker_common_pb2.Position":
        """Convert to broker service proto.

        Returns:
            Broker service Position proto
        """
        proto = broker_common_pb2.Position()
        proto.symbol = self.symbol
        proto.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity, "broker"))
        proto.avg_price.CopyFrom(decimal_to_precise_decimal(self.avg_price, "broker"))
        proto.market_value.CopyFrom(decimal_to_precise_decimal(self.market_value, "broker"))
        proto.unrealized_pnl.CopyFrom(decimal_to_precise_decimal(self.unrealized_pnl, "broker"))
        proto.realized_pnl.CopyFrom(decimal_to_precise_decimal(self.realized_pnl, "broker"))
        proto.current_price.CopyFrom(decimal_to_precise_decimal(self.current_price, "broker"))
        return proto

    def __str__(self) -> str:
        """Human-readable string representation."""
        side = "Long" if self.is_long else "Short"
        return f"{side} {abs(self.quantity)} {self.symbol} @ {self.avg_price:.2f} " f"(P&L: {self.total_pnl:+.2f}, {self.return_percentage:+.2f}%)"
