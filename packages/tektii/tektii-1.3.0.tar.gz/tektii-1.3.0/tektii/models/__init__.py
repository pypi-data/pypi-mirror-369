"""Type-safe models for the Tektii Strategy SDK.

This module provides Pydantic-based models that mirror the proto definitions
with enhanced type safety and developer experience.
"""

# Re-export base types
from .base import ProtoConvertible, ProtoEnum

# Re-export broker models
from .broker import PositionRisk

# Re-export strategy models
from .strategy import AccountUpdateEvent, CandleData, CandleType, OptionGreeks, OrderUpdateEvent, TradeUpdate, TradeUpdateReason

__all__ = [
    # Base types
    "ProtoConvertible",
    "ProtoEnum",
    # Broker models
    "PositionRisk",
    # Strategy events
    "AccountUpdateEvent",
    "CandleData",
    "CandleType",
    "OptionGreeks",
    "OrderUpdateEvent",
    "PositionUpdateEvent",
    "SystemUpdate",
    "SystemUpdateType",
    "TickData",
    "TickType",
    "TradeUpdate",
    "TradeUpdateReason",
]
