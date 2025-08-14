"""Get market depth request and response handlers."""

from __future__ import annotations

from datetime import datetime
from typing import List

from broker.v1 import handler_get_market_depth_pb2
from pydantic import BaseModel, Field

from ..types.price_level import PriceLevel


class MarketDepthRequest(BaseModel):
    """Request for current market depth."""

    symbol: str = Field(description="Symbol to get depth for")
    depth: int = Field(default=5, ge=1, le=20, description="Number of price levels")

    def to_proto(self) -> handler_get_market_depth_pb2.GetMarketDepthRequest:
        """Convert to protobuf message."""
        return handler_get_market_depth_pb2.GetMarketDepthRequest(symbol=self.symbol, depth=self.depth)


class MarketDepthResponse(BaseModel):
    """Response containing market depth data."""

    symbol: str = Field(description="Symbol depth is for")
    bids: List[PriceLevel] = Field(default_factory=list, description="Bid price levels")
    asks: List[PriceLevel] = Field(default_factory=list, description="Ask price levels")
    timestamp: datetime = Field(description="Depth snapshot timestamp")

    @classmethod
    def from_proto(cls, proto: handler_get_market_depth_pb2.GetMarketDepthResponse) -> MarketDepthResponse:
        """Create from protobuf message."""
        return cls(
            symbol=proto.symbol,
            bids=[PriceLevel.from_proto(b) for b in proto.bids],
            asks=[PriceLevel.from_proto(a) for a in proto.asks],
            timestamp=datetime.fromtimestamp(proto.timestamp_us / 1e9),
        )
