"""Candle data event model."""

from __future__ import annotations

from decimal import Decimal
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field
from strategy.v1 import event_candle_data_pb2

from ..conversions import optional_precise_decimal_to_decimal, precise_decimal_to_decimal


class CandleType(IntEnum):
    """Type of candle data."""

    UNSPECIFIED = 0
    TIME = 1
    TICK = 2
    VOLUME = 3
    DOLLAR = 4

    @classmethod
    def from_proto(cls, value: int) -> CandleType:
        """Create from proto value."""
        return cls(value)


class CandleData(BaseModel):
    """Candlestick/bar data for a symbol."""

    symbol: str = Field(description="Trading symbol")
    open: Decimal = Field(description="Open price")
    high: Decimal = Field(description="High price")
    low: Decimal = Field(description="Low price")
    close: Decimal = Field(description="Close price")
    volume: int = Field(description="Volume")
    vwap: Optional[Decimal] = Field(default=None, description="Volume-weighted average price")
    trade_count: Optional[int] = Field(default=None, description="Number of trades")
    candle_type: Optional[CandleType] = Field(default=None, description="Type of candle")
    candle_size: Optional[int] = Field(default=None, description="Size of candle")
    candle_size_unit: Optional[str] = Field(default=None, description="Unit of candle size")

    @classmethod
    def from_proto(cls, proto: event_candle_data_pb2.CandleData) -> CandleData:
        """Create from protobuf message."""
        return cls(
            symbol=proto.symbol,
            open=precise_decimal_to_decimal(proto.open),
            high=precise_decimal_to_decimal(proto.high),
            low=precise_decimal_to_decimal(proto.low),
            close=precise_decimal_to_decimal(proto.close),
            volume=proto.volume,
            vwap=optional_precise_decimal_to_decimal(proto.vwap) if proto.HasField("vwap") else None,
            trade_count=proto.trade_count if proto.trade_count else None,
            candle_type=CandleType.from_proto(proto.candle_type) if proto.candle_type else None,
            candle_size=proto.candle_size if proto.candle_size else None,
            candle_size_unit=proto.candle_size_unit if proto.candle_size_unit else None,
        )
