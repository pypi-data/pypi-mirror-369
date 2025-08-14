"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from enum import IntEnum
from typing import Dict, Optional

from pydantic import BaseModel, Field
from strategy.v1 import event_trade_update_pb2

from ..conversions import optional_precise_decimal_to_decimal, precise_decimal_to_decimal
from ..types.order_side import OrderSide


class TradeUpdateReason(IntEnum):
    """Reason for trade update."""

    UNSPECIFIED = 0
    PARTIAL_CLOSE = 1
    PROTECTION_MODIFIED = 2
    CLOSED = 3
    OPENED = 4

    @classmethod
    def from_proto(cls, value: int) -> TradeUpdateReason:
        """Create from proto value."""
        return cls(value)


class TradeUpdate(BaseModel):
    """Event triggered when a trade updates."""

    trade_id: str = Field(description="Unique trade identifier")
    symbol: str = Field(description="Trading symbol")
    side: OrderSide = Field(description="Trade side")
    quantity: Decimal = Field(description="Original trade quantity")
    remaining_quantity: Decimal = Field(description="Remaining trade quantity")
    entry_price: Decimal = Field(description="Entry price")
    entry_timestamp_us: int = Field(description="Entry timestamp in microseconds")
    unrealized_pnl: Decimal = Field(description="Unrealized P&L")
    realized_pnl: Decimal = Field(description="Realized P&L")
    current_price: Optional[Decimal] = Field(default=None, description="Current market price")
    stop_loss_order_id: Optional[str] = Field(default=None, description="Stop loss order ID")
    take_profit_order_id: Optional[str] = Field(default=None, description="Take profit order ID")
    update_reason: Optional[TradeUpdateReason] = Field(default=None, description="Reason for update")
    timestamp_us: int = Field(description="Update timestamp in microseconds")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    @classmethod
    def from_proto(cls, proto: event_trade_update_pb2.TradeUpdateEvent) -> TradeUpdate:
        """Create from protobuf message."""
        return cls(
            trade_id=proto.trade_id,
            symbol=proto.symbol,
            side=OrderSide.from_proto(proto.side),
            quantity=precise_decimal_to_decimal(proto.quantity),
            remaining_quantity=precise_decimal_to_decimal(proto.remaining_quantity),
            entry_price=precise_decimal_to_decimal(proto.entry_price),
            entry_timestamp_us=proto.entry_timestamp_us,
            unrealized_pnl=precise_decimal_to_decimal(proto.unrealized_pnl),
            realized_pnl=precise_decimal_to_decimal(proto.realized_pnl),
            current_price=optional_precise_decimal_to_decimal(proto.current_price) if proto.HasField("current_price") else None,
            stop_loss_order_id=proto.stop_loss_order_id if proto.stop_loss_order_id else None,
            take_profit_order_id=proto.take_profit_order_id if proto.take_profit_order_id else None,
            update_reason=TradeUpdateReason.from_proto(proto.update_reason) if proto.update_reason else None,
            timestamp_us=proto.timestamp_us,
            metadata=dict(proto.metadata),
        )
