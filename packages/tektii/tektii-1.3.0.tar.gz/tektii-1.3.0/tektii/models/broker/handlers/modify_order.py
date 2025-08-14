"""Modify order request and response handlers."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from broker.v1 import handler_modify_order_pb2
from pydantic import BaseModel, Field

from ..errors import ErrorCode
from ..types.broker import Broker


class ModifyOrderRequest(BaseModel):
    """Request to modify an existing order."""

    order_id: str = Field(description="ID of order to modify")
    quantity: Optional[Decimal] = Field(default=None, description="New quantity (None = no change)")
    limit_price: Optional[Decimal] = Field(default=None, description="New limit price (None = no change)")
    stop_price: Optional[Decimal] = Field(default=None, description="New stop price (None = no change)")
    request_id: Optional[str] = Field(default=None, description="Client request ID for tracking")
    broker: Optional[Broker] = Field(default=None, description="Target broker for the modification")

    def to_proto(self) -> handler_modify_order_pb2.ModifyOrderRequest:
        """Convert to protobuf message."""
        from ..conversions import decimal_to_precise_decimal

        proto_msg = handler_modify_order_pb2.ModifyOrderRequest(order_id=self.order_id)

        if self.quantity is not None:
            proto_msg.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity))
        if self.limit_price is not None:
            proto_msg.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price))
        if self.stop_price is not None:
            proto_msg.stop_price.CopyFrom(decimal_to_precise_decimal(self.stop_price))
        if self.request_id:
            proto_msg.request_id = self.request_id
        if self.broker is not None:
            proto_msg.broker = self.broker.to_proto()

        return proto_msg

    @classmethod
    def from_proto(cls, proto: handler_modify_order_pb2.ModifyOrderRequest) -> ModifyOrderRequest:
        """Create from protobuf message."""
        from ..conversions import precise_decimal_to_decimal
        from ..types.broker import Broker

        return cls(
            order_id=proto.order_id,
            quantity=precise_decimal_to_decimal(proto.quantity) if proto.HasField("quantity") else None,
            limit_price=precise_decimal_to_decimal(proto.limit_price) if proto.HasField("limit_price") else None,
            stop_price=precise_decimal_to_decimal(proto.stop_price) if proto.HasField("stop_price") else None,
            request_id=proto.request_id if proto.request_id else None,
            broker=Broker.from_proto(proto.broker) if proto.HasField("broker") else None,
        )


class ModifyOrderResponse(BaseModel):
    """Response from modifying an order."""

    accepted: bool = Field(description="Whether modification was accepted")
    order_id: Optional[str] = Field(default=None, description="ID of modified order")
    request_id: Optional[str] = Field(default=None, description="Client request ID")
    reject_reason: Optional[str] = Field(default=None, description="Rejection reason if not accepted")
    error_code: Optional[ErrorCode] = Field(default=None, description="Error code if not accepted")
    timestamp_us: Optional[int] = Field(default=None, description="Response timestamp in microseconds")

    @classmethod
    def from_proto(cls, proto: handler_modify_order_pb2.ModifyOrderResponse) -> ModifyOrderResponse:
        """Create from protobuf message."""
        return cls(
            accepted=proto.accepted,
            order_id=proto.order_id if proto.order_id else None,
            request_id=proto.request_id if proto.request_id else None,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            error_code=ErrorCode.from_proto(proto.error_code) if proto.HasField("error_code") else None,
            timestamp_us=proto.timestamp_us if proto.timestamp_us > 0 else None,
        )
