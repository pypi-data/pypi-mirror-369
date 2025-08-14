"""Conversion utilities for handling Decimal to/from protobuf conversions.

This module handles conversions between Python Decimal types and protobuf representations,
supporting both the legacy float-based format and the new PreciseDecimal format used by
the broker and strategy services.
"""

from decimal import Decimal
from typing import Optional

from strategy.v1 import strategy_common_pb2 as strategy_pb2


def proto_from_decimal(value: Optional[Decimal]) -> float:
    """Convert a Decimal to float for protobuf serialization.

    Args:
        value: Decimal value or None

    Returns:
        float representation, or 0.0 if None
    """
    if value is None:
        return 0.0
    return float(value)


def decimal_from_proto(value: float) -> Optional[Decimal]:
    """Convert a protobuf float to Decimal.

    Args:
        value: float value from protobuf

    Returns:
        Decimal representation, or None if value is 0.0
    """
    if value == 0.0:
        return None
    return Decimal(str(value))


def decimal_from_proto_required(value: float) -> Decimal:
    """Convert a protobuf float to Decimal (required field).

    Args:
        value: float value from protobuf

    Returns:
        Decimal representation
    """
    return Decimal(str(value))


def precise_decimal_to_decimal(precise: "strategy_pb2.PreciseDecimal") -> Decimal:
    """Convert a PreciseDecimal protobuf message to Python Decimal.

    Args:
        precise: PreciseDecimal protobuf message from either broker or strategy service

    Returns:
        Decimal representation with proper scaling
    """
    if precise.scale == 0:
        return Decimal(precise.value)

    # Create decimal with proper scaling
    scale_factor = Decimal(10) ** precise.scale
    result: Decimal = Decimal(precise.value) / scale_factor
    return result


def decimal_to_precise_decimal(value: Decimal, service: str = "strategy") -> "strategy_pb2.PreciseDecimal":
    """Convert a Python Decimal to PreciseDecimal protobuf message.

    Args:
        value: Decimal value to convert
        service: Which service's PreciseDecimal to create ('broker' or 'strategy')

    Returns:
        PreciseDecimal protobuf message
    """
    # Use 6 decimal places as standard precision
    scale = 6
    scale_factor = Decimal(10) ** scale
    scaled_value = int(value * scale_factor)

    return strategy_pb2.PreciseDecimal(value=scaled_value, scale=scale)


def optional_precise_decimal_to_decimal(precise: Optional["strategy_pb2.PreciseDecimal"]) -> Optional[Decimal]:
    """Convert an optional PreciseDecimal to optional Decimal.

    Args:
        precise: Optional PreciseDecimal protobuf message

    Returns:
        Optional Decimal representation
    """
    if precise is None:
        return None
    return precise_decimal_to_decimal(precise)
