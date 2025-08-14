"""Time in force enumeration."""

from __future__ import annotations

from ...base import ProtoEnum


class TimeInForce(ProtoEnum):
    """Time in force enumeration.

    Specifies how long an order remains active.
    Only available in broker service PlaceOrder handler.
    """

    UNSPECIFIED = 0  # TIME_IN_FORCE_UNSPECIFIED
    DAY = 1  # TIME_IN_FORCE_DAY
    GTC = 2  # TIME_IN_FORCE_GTC
    IOC = 3  # TIME_IN_FORCE_IOC
    FOK = 4  # TIME_IN_FORCE_FOK

    def is_immediate(self) -> bool:
        """Check if this is an immediate-or-cancel type.

        Returns:
            True if order must execute immediately or cancel
        """
        return self in (TimeInForce.IOC, TimeInForce.FOK)
