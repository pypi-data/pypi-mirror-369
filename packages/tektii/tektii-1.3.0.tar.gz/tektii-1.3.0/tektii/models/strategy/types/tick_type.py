"""Tick type enumeration."""

from __future__ import annotations

from enum import IntEnum


class TickType(IntEnum):
    """Tick type enumeration.

    Indicates the type of data in a tick.
    """

    UNKNOWN = 0
    QUOTE = 1
    TRADE = 2
    QUOTE_AND_TRADE = 3
