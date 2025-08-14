"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from broker.v1 import handler_place_order_pb2
from pydantic import BaseModel, Field

from ..conversions import decimal_to_precise_decimal
from ..types.broker import Broker
from ..types.order_intent import OrderIntent
from ..types.order_side import OrderSide
from ..types.order_type import OrderType
from ..types.protective_orders_on_fill import ProtectiveOrdersOnFill
from ..types.time_in_force import TimeInForce


class PlaceOrderRequest(BaseModel):
    """Request to place a new order."""

    symbol: str = Field(description="Trading symbol")
    side: OrderSide = Field(description="Order side (buy/sell)")
    order_type: OrderType = Field(description="Order type")
    quantity: Decimal = Field(description="Order quantity")
    limit_price: Optional[Decimal] = Field(default=None, description="Limit price for limit orders")
    stop_price: Optional[Decimal] = Field(default=None, description="Stop price for stop orders")
    time_in_force: Optional[TimeInForce] = Field(default=None, description="Time in force")
    client_order_id: Optional[str] = Field(default=None, description="Client order ID")
    order_intent: Optional[OrderIntent] = Field(default=None, description="Order intent")
    broker: Optional[Broker] = Field(default=None, description="Target broker")
    protective_orders_on_fill: Optional[ProtectiveOrdersOnFill] = Field(default=None, description="Protective orders to create on fill")
    parent_trade_id: Optional[str] = Field(default=None, description="Parent trade ID")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    validate_only: bool = Field(default=False, description="Only validate order without placing")
    request_id: Optional[str] = Field(default=None, description="Request ID for idempotency")

    def to_proto(self) -> handler_place_order_pb2.PlaceOrderRequest:
        """Convert to protobuf message."""
        proto = handler_place_order_pb2.PlaceOrderRequest(
            symbol=self.symbol,
            validate_only=self.validate_only,
        )

        proto.side = self.side.to_proto()
        proto.order_type = self.order_type.to_proto()
        proto.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity))

        if self.limit_price is not None:
            proto.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price))
        if self.stop_price is not None:
            proto.stop_price.CopyFrom(decimal_to_precise_decimal(self.stop_price))
        if self.time_in_force is not None:
            proto.time_in_force = self.time_in_force.to_proto()
        if self.client_order_id:
            proto.client_order_id = self.client_order_id
        if self.order_intent is not None:
            proto.order_intent = self.order_intent.to_proto()
        if self.broker is not None:
            proto.broker = self.broker.to_proto()
        if self.protective_orders_on_fill:
            proto.protective_orders_on_fill.CopyFrom(self.protective_orders_on_fill.to_proto())
        if self.parent_trade_id:
            proto.parent_trade_id = self.parent_trade_id
        if self.metadata:
            for key, value in self.metadata.items():
                proto.metadata[key] = value
        if self.request_id:
            proto.request_id = self.request_id

        return proto


class PlaceOrderResponse(BaseModel):
    """Response from placing an order."""

    accepted: bool = Field(description="Whether order was accepted")
    order_id: Optional[str] = Field(default=None, description="Order ID if accepted")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")
    reject_reason: Optional[str] = Field(default=None, description="Rejection reason if not accepted")
    error_code: Optional[int] = Field(default=None, description="Error code if rejected")
    timestamp_us: Optional[int] = Field(default=None, description="Response timestamp in microseconds")

    @classmethod
    def from_proto(cls, proto: handler_place_order_pb2.PlaceOrderResponse) -> PlaceOrderResponse:
        """Convert from protobuf message."""
        return cls(
            accepted=proto.accepted,
            order_id=proto.order_id if proto.order_id else None,
            request_id=proto.request_id if proto.request_id else None,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            error_code=proto.error_code if proto.error_code else None,
            timestamp_us=proto.timestamp_us if proto.timestamp_us else None,
        )
