"""Strategy candlestick data model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator
from strategy.v1 import strategy_common_pb2

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal, precise_decimal_to_decimal


class CandleType(IntEnum):
    """Candle type enumeration.

    Indicates how candles are aggregated.
    """

    UNKNOWN = 0
    TIME = 1
    TICK = 2
    VOLUME = 3
    DOLLAR = 4


class Candle(BaseModel):
    """Represents OHLCV data for a time period.

    Standard candlestick/candle data with open, high, low, close, volume.
    """

    timestamp_us: int = Field(..., description="Start of candle period (microseconds since epoch)")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    vwap: Optional[Decimal] = Field(None, description="Volume-weighted average price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("open", "high", "low", "close", "vwap")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal, None]) -> Optional[Decimal]:
        """Ensure all price fields are Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def timestamp(self) -> datetime:
        """Get timestamp as datetime.

        Returns:
            Candle timestamp as datetime
        """
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    @property
    def range(self) -> Decimal:
        """Price range from high to low.

        Returns:
            Price range
        """
        return self.high - self.low

    @property
    def body(self) -> Decimal:
        """Candle body size as absolute difference.

        Returns:
            Absolute body size
        """
        return abs(self.close - self.open)

    @property
    def is_bullish(self) -> bool:
        """Check if this is a bullish candle.

        Returns:
            True if close > open
        """
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Check if this is a bearish candle.

        Returns:
            True if close < open
        """
        return self.close < self.open

    @classmethod
    def from_proto(cls, proto: "strategy_common_pb2.Candle") -> Candle:
        """Create Candle from strategy service Candle proto.

        Args:
            proto: Candle proto from strategy service

        Returns:
            Candle model instance
        """
        return cls(
            timestamp_us=proto.timestamp_us,
            open=precise_decimal_to_decimal(proto.open),
            high=precise_decimal_to_decimal(proto.high),
            low=precise_decimal_to_decimal(proto.low),
            close=precise_decimal_to_decimal(proto.close),
            volume=proto.volume,
            vwap=optional_precise_decimal_to_decimal(proto.vwap),
        )

    def to_proto(self) -> "strategy_common_pb2.Candle":
        """Convert to strategy service Candle proto.

        Returns:
            sStrategy service Candle proto
        """
        proto = strategy_common_pb2.Candle()
        proto.timestamp_us = self.timestamp_us
        proto.open.CopyFrom(decimal_to_precise_decimal(self.open, "strategy"))
        proto.high.CopyFrom(decimal_to_precise_decimal(self.high, "strategy"))
        proto.low.CopyFrom(decimal_to_precise_decimal(self.low, "strategy"))
        proto.close.CopyFrom(decimal_to_precise_decimal(self.close, "strategy"))
        proto.volume = self.volume
        if self.vwap:
            proto.vwap.CopyFrom(decimal_to_precise_decimal(self.vwap, "strategy"))
        return proto

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Candle({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
            f"O={self.open:.2f} H={self.high:.2f} L={self.low:.2f} C={self.close:.2f} V={self.volume:,})"
        )
