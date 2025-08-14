"""Get historical data request and response handlers."""

from __future__ import annotations

from typing import List

from broker.v1 import handler_get_historical_data_pb2
from pydantic import BaseModel, Field

from ..types.candle import Candle


class HistoricalDataRequest(BaseModel):
    """Request for historical market data."""

    symbol: str = Field(description="Symbol to retrieve data for")
    candle_size: str = Field(default="1m", description="Candle size (1m, 5m, 15m, 30m, 1h, 1d)")
    limit: int = Field(default=100, description="Maximum number of candles to return")

    def to_proto(self) -> handler_get_historical_data_pb2.GetHistoricalDataRequest:
        """Convert to protobuf message."""
        return handler_get_historical_data_pb2.GetHistoricalDataRequest(
            symbol=self.symbol,
            candle_size=self.candle_size,
            limit=self.limit,
        )


class HistoricalDataResponse(BaseModel):
    """Response containing historical market data."""

    symbol: str = Field(description="Symbol data is for")
    candles: List[Candle] = Field(default_factory=list, description="Historical candles")

    @classmethod
    def from_proto(cls, proto: handler_get_historical_data_pb2.GetHistoricalDataResponse) -> HistoricalDataResponse:
        """Create from protobuf message."""
        return cls(symbol=proto.symbol, candles=[Candle.from_proto(b) for b in proto.candles])
