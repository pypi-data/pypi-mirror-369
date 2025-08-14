"""Error types and codes for the Tektii SDK.

This module consolidates all error-related enumerations and classes
from the proto specification, providing a centralized location for
error handling types.
"""

from __future__ import annotations

from broker.v1 import broker_common_pb2

from ..base import ProtoEnum


class ErrorCode(ProtoEnum):
    """Error code enumeration.

    Indicates why an order was rejected or failed validation.
    Maps to the ErrorCode enum in the proto specification.
    """

    UNSPECIFIED = broker_common_pb2.ERROR_CODE_UNSPECIFIED  # 0
    INVALID_SYMBOL = broker_common_pb2.ERROR_CODE_INVALID_SYMBOL  # 1
    INVALID_QUANTITY = broker_common_pb2.ERROR_CODE_INVALID_QUANTITY  # 2
    INVALID_PRICE = broker_common_pb2.ERROR_CODE_INVALID_PRICE  # 3
    MISSING_REQUIRED_FIELD = broker_common_pb2.ERROR_CODE_MISSING_REQUIRED_FIELD  # 4
    CONFLICTING_FIELDS = broker_common_pb2.ERROR_CODE_CONFLICTING_FIELDS  # 5
    INSUFFICIENT_MARGIN = broker_common_pb2.ERROR_CODE_INSUFFICIENT_MARGIN  # 21
    POSITION_LIMIT = broker_common_pb2.ERROR_CODE_POSITION_LIMIT  # 22
    ACCOUNT_RESTRICTED = broker_common_pb2.ERROR_CODE_ACCOUNT_RESTRICTED  # 23
    MARKET_CLOSED = broker_common_pb2.ERROR_CODE_MARKET_CLOSED  # 41
    DUPLICATE_ORDER = broker_common_pb2.ERROR_CODE_DUPLICATE_ORDER  # 61
    ORDER_NOT_FOUND = broker_common_pb2.ERROR_CODE_ORDER_NOT_FOUND  # 62
    ORDER_NOT_MODIFIABLE = broker_common_pb2.ERROR_CODE_ORDER_NOT_MODIFIABLE  # 63
    RATE_LIMIT = broker_common_pb2.ERROR_CODE_RATE_LIMIT  # 81
    RISK_CHECK_FAILED = broker_common_pb2.ERROR_CODE_RISK_CHECK_FAILED  # 82


__all__ = [
    "ErrorCode",
]
