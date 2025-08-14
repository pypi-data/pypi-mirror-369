"""Order status enumeration."""

from __future__ import annotations

from ...base import ProtoEnum


class OrderStatus(ProtoEnum):
    """Order status enumeration.

    Represents the current state of an order in its lifecycle.
    Compatible with both broker and strategy services.
    """

    UNSPECIFIED = 0  # Maps to ORDER_STATUS_UNSPECIFIED
    PENDING = 1  # ORDER_STATUS_PENDING
    SUBMITTED = 2  # ORDER_STATUS_SUBMITTED
    ACCEPTED = 3  # ORDER_STATUS_ACCEPTED
    PARTIAL = 4  # ORDER_STATUS_PARTIAL
    FILLED = 5  # ORDER_STATUS_FILLED
    CANCELED = 6  # ORDER_STATUS_CANCELED
    REJECTED = 7  # ORDER_STATUS_REJECTED
    EXPIRED = 8  # ORDER_STATUS_EXPIRED

    def is_terminal(self) -> bool:
        """Check if this is a terminal status (order is done).

        Returns:
            True if order is in terminal state
        """
        return self in (
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        )

    def is_active(self) -> bool:
        """Check if order is still active.

        Returns:
            True if order can still be executed
        """
        return self in (
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIAL,
        )
