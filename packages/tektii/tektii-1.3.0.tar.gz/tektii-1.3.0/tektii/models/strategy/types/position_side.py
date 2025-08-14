"""Strategy position side enumeration."""

from __future__ import annotations

from enum import Enum


class PositionSide(str, Enum):
    """Position side enumeration.

    Indicates the direction of a position.
    """

    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"

    @classmethod
    def from_quantity(cls, quantity: float) -> PositionSide:
        """Determine position side from quantity.

        Args:
            quantity: Position quantity

        Returns:
            Position side based on quantity sign
        """
        if quantity > 0:
            return cls.LONG
        elif quantity < 0:
            return cls.SHORT
        else:
            return cls.FLAT
