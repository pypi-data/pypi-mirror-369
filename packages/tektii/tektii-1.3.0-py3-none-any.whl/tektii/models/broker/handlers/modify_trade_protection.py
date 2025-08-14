"""Modify trade protection request and response handlers."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from broker.v1 import handler_modify_trade_protection_pb2
from pydantic import BaseModel, Field

from ..conversions import decimal_to_precise_decimal, precise_decimal_to_decimal
from ..errors import ErrorCode
from ..types.broker import Broker
from ..types.stop_limit_order import StopLimitOrder
from ..types.stop_order import StopOrder


class StopLossModification(BaseModel):
    """Modification for stop loss orders."""

    stop: Optional[StopOrder] = Field(default=None, description="New stop order configuration")
    stop_limit: Optional[StopLimitOrder] = Field(default=None, description="New stop limit order configuration")
    remove: bool = Field(default=False, description="Remove existing stop loss")

    def to_proto(self) -> handler_modify_trade_protection_pb2.ModifyTradeProtectionRequest.StopLossModification:
        """Convert to protobuf message."""
        proto = handler_modify_trade_protection_pb2.ModifyTradeProtectionRequest.StopLossModification()

        if self.stop:
            proto.stop.CopyFrom(self.stop.to_proto())
        elif self.stop_limit:
            proto.stop_limit.CopyFrom(self.stop_limit.to_proto())
        elif self.remove:
            proto.remove = True

        return proto


class TakeProfitModification(BaseModel):
    """Modification for take profit orders."""

    limit_price: Optional[Decimal] = Field(default=None, description="New take profit limit price")
    remove: bool = Field(default=False, description="Remove existing take profit")

    def to_proto(self) -> handler_modify_trade_protection_pb2.ModifyTradeProtectionRequest.TakeProfitModification:
        """Convert to protobuf message."""
        proto = handler_modify_trade_protection_pb2.ModifyTradeProtectionRequest.TakeProfitModification()

        if self.limit_price is not None:
            proto.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price, "broker"))
        elif self.remove:
            proto.remove = True

        return proto


class ModifyTradeProtectionRequest(BaseModel):
    """Request to modify protective orders on an existing trade.

    Allows modification of stop loss and take profit orders for open positions.
    """

    trade_id: str = Field(description="ID of the trade to modify")
    stop_loss_modification: Optional[StopLossModification] = Field(default=None, description="Stop loss modification")
    take_profit_modification: Optional[TakeProfitModification] = Field(default=None, description="Take profit modification")
    request_id: Optional[str] = Field(default=None, description="Client-provided request ID for tracking")
    broker: Optional[Broker] = Field(default=None, description="Target broker for the modification")

    def to_proto(self) -> handler_modify_trade_protection_pb2.ModifyTradeProtectionRequest:
        """Convert to protobuf message."""
        proto = handler_modify_trade_protection_pb2.ModifyTradeProtectionRequest()
        proto.trade_id = self.trade_id

        # Handle stop loss modification
        if self.stop_loss_modification:
            proto.stop_loss.CopyFrom(self.stop_loss_modification.to_proto())

        # Handle take profit modification
        if self.take_profit_modification:
            proto.take_profit.CopyFrom(self.take_profit_modification.to_proto())

        if self.request_id:
            proto.request_id = self.request_id

        if self.broker:
            proto.broker = self.broker.to_proto()

        return proto


class ModifyTradeProtectionResponse(BaseModel):
    """Response from modifying trade protection orders.

    Contains updated trade information and confirmation of modifications.
    """

    accepted: bool = Field(description="Whether the modification was accepted")
    trade_id: str = Field(description="ID of the modified trade")
    request_id: Optional[str] = Field(default=None, description="Client-provided request ID")
    stop_loss_order_id: Optional[str] = Field(default=None, description="ID of the stop loss order")
    take_profit_order_id: Optional[str] = Field(default=None, description="ID of the take profit order")
    trade_quantity: Optional[Decimal] = Field(default=None, description="Current trade quantity")
    trade_entry_price: Optional[Decimal] = Field(default=None, description="Average entry price of the trade")
    current_price: Optional[Decimal] = Field(default=None, description="Current market price")
    max_loss: Optional[Decimal] = Field(default=None, description="Maximum potential loss with current protection")
    max_profit: Optional[Decimal] = Field(default=None, description="Maximum potential profit with current protection")
    reject_reason: Optional[str] = Field(default=None, description="Reason for rejection if not accepted")
    error_code: Optional[ErrorCode] = Field(default=None, description="Error code if not accepted")
    timestamp_us: Optional[int] = Field(default=None, description="Response timestamp in microseconds")

    @classmethod
    def from_proto(cls, proto: handler_modify_trade_protection_pb2.ModifyTradeProtectionResponse) -> "ModifyTradeProtectionResponse":
        """Create from protobuf message."""
        return cls(
            accepted=proto.accepted,
            trade_id=proto.trade_id,
            request_id=proto.request_id if proto.request_id else None,
            stop_loss_order_id=proto.stop_loss_order_id if proto.stop_loss_order_id else None,
            take_profit_order_id=proto.take_profit_order_id if proto.take_profit_order_id else None,
            trade_quantity=precise_decimal_to_decimal(proto.trade_quantity) if proto.HasField("trade_quantity") else None,
            trade_entry_price=precise_decimal_to_decimal(proto.trade_entry_price) if proto.HasField("trade_entry_price") else None,
            current_price=precise_decimal_to_decimal(proto.current_price) if proto.HasField("current_price") else None,
            max_loss=precise_decimal_to_decimal(proto.max_loss) if proto.HasField("max_loss") else None,
            max_profit=precise_decimal_to_decimal(proto.max_profit) if proto.HasField("max_profit") else None,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            error_code=ErrorCode.from_proto(proto.error_code) if proto.HasField("error_code") else None,
            timestamp_us=proto.timestamp_us if proto.timestamp_us else None,
        )
