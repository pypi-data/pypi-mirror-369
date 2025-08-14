"""Strategy order side enumeration."""

from __future__ import annotations

from ...base import ProtoEnum


class OrderSide(ProtoEnum):
    """Order side enumeration.

    Indicates whether an order is to buy or sell.
    Compatible with both broker and strategy services.
    """

    UNSPECIFIED = 0  # ORDER_SIDE_UNSPECIFIED
    BUY = 1  # ORDER_SIDE_BUY
    SELL = 2  # ORDER_SIDE_SELL

    def opposite(self) -> OrderSide:
        """Get the opposite side.

        Returns:
            Opposite order side

        Raises:
            ValueError: If side is UNKNOWN
        """
        if self == OrderSide.BUY:
            return OrderSide.SELL
        elif self == OrderSide.SELL:
            return OrderSide.BUY
        else:
            raise ValueError("Cannot get opposite of UNSPECIFIED side")
