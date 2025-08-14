"""Order intent enumeration."""

from __future__ import annotations

from ...base import ProtoEnum


class OrderIntent(ProtoEnum):
    """Order intent enumeration.

    Indicates the purpose of an order for tracking and risk management.
    Only available in broker service.
    """

    UNSPECIFIED = 0  # ORDER_INTENT_UNSPECIFIED
    OPEN = 1  # ORDER_INTENT_OPEN
    CLOSE = 2  # ORDER_INTENT_CLOSE
    STOP_LOSS = 3  # ORDER_INTENT_STOP_LOSS
    TAKE_PROFIT = 4  # ORDER_INTENT_TAKE_PROFIT

    def is_protective(self) -> bool:
        """Check if this is a protective order intent.

        Returns:
            True if order is protective (stop loss or take profit)
        """
        return self in (OrderIntent.STOP_LOSS, OrderIntent.TAKE_PROFIT)
