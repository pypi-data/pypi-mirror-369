"""Strategy order type enumeration."""

from __future__ import annotations

from ...base import ProtoEnum


class OrderType(ProtoEnum):
    """Order type enumeration.

    Specifies how an order should be executed.
    Compatible with both broker and strategy services.
    """

    UNSPECIFIED = 0  # ORDER_TYPE_UNSPECIFIED
    MARKET = 1  # ORDER_TYPE_MARKET
    LIMIT = 2  # ORDER_TYPE_LIMIT
    STOP = 3  # ORDER_TYPE_STOP
    STOP_LIMIT = 4  # ORDER_TYPE_STOP_LIMIT

    def requires_limit_price(self) -> bool:
        """Check if this order type requires a limit price.

        Returns:
            True if limit price is required
        """
        return self in (OrderType.LIMIT, OrderType.STOP_LIMIT)

    def requires_stop_price(self) -> bool:
        """Check if this order type requires a stop price.

        Returns:
            True if stop price is required
        """
        return self in (OrderType.STOP, OrderType.STOP_LIMIT)
