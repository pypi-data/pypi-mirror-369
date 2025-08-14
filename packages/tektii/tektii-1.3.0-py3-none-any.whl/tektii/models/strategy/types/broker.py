"""Strategy broker type enumeration."""

from __future__ import annotations

from ...base import ProtoEnum


class Broker(ProtoEnum):
    """Broker enumeration.

    Indicates which broker or execution venue is being used.
    Available in both broker and strategy services.
    """

    UNSPECIFIED = 0  # BROKER_UNSPECIFIED
    BACKTESTING = 1  # BROKER_BACKTESTING
    ALPACA = 2  # BROKER_ALPACA
    INTERACTIVE_BROKERS = 3  # BROKER_INTERACTIVE_BROKERS
    BINANCE = 4  # BROKER_BINANCE
