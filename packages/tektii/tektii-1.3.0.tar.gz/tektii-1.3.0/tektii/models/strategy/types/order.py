"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from strategy.v1 import strategy_common_pb2

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal, precise_decimal_to_decimal
from .broker import Broker
from .order_side import OrderSide
from .order_status import OrderStatus
from .order_type import OrderType


class Order(BaseModel):
    """Represents a trading order.

    Comprehensive order information including status, fills, and metadata.
    """

    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Trading symbol")
    status: OrderStatus = Field(..., description="Current order status")
    side: OrderSide = Field(..., description="Buy or sell")
    order_type: OrderType = Field(..., description="Order execution type")
    quantity: Decimal = Field(..., description="Total order quantity")
    filled_quantity: Decimal = Field(Decimal("0"), description="Quantity filled so far")
    limit_price: Optional[Decimal] = Field(None, description="Limit price (if applicable)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price (if applicable)")
    # Timestamps - using microseconds
    created_at_us: Optional[int] = Field(None, description="Order creation time in microseconds")
    parent_trade_id: Optional[str] = Field(None, description="Parent trade ID for linked orders")

    # Additional metadata
    broker: Optional[Broker] = Field(None, description="Broker that executed order")

    @field_validator("quantity", "filled_quantity", "limit_price", "stop_price")
    @classmethod
    def validate_decimals(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate decimal fields are properly scaled."""
        if v is None:
            return v
        # Ensure proper decimal precision for financial values
        return v.quantize(Decimal("0.000001"))

    @field_validator("filled_quantity")
    @classmethod
    def validate_filled_quantity(cls, v: Decimal) -> Decimal:
        """Ensure filled quantity is non-negative."""
        if v < 0:
            raise ValueError("Filled quantity cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_order_consistency(self) -> Order:
        """Validate order field consistency."""
        # Filled quantity cannot exceed total quantity
        if self.filled_quantity > self.quantity:
            raise ValueError("Filled quantity cannot exceed total quantity")

        # Limit price required for limit orders
        if self.order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT) and self.limit_price is None:
            raise ValueError(f"{self.order_type.name} orders require a limit price")

        # Stop price required for stop orders
        if self.order_type in (OrderType.STOP, OrderType.STOP_LIMIT) and self.stop_price is None:
            raise ValueError(f"{self.order_type.name} orders require a stop price")

        return self

    def to_proto(self) -> strategy_common_pb2.Order:
        """Convert to protobuf Order message.

        Returns:
            Protobuf Order message
        """
        proto_order = strategy_common_pb2.Order()
        proto_order.order_id = self.order_id
        proto_order.symbol = self.symbol
        proto_order.status = self.status.value  # type: ignore[assignment]
        proto_order.side = self.side.value  # type: ignore[assignment]
        proto_order.order_type = self.order_type.value  # type: ignore[assignment]
        proto_order.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity))
        proto_order.filled_quantity.CopyFrom(decimal_to_precise_decimal(self.filled_quantity))

        # Optional fields
        if self.limit_price is not None:
            proto_order.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price))

        if self.stop_price is not None:
            proto_order.stop_price.CopyFrom(decimal_to_precise_decimal(self.stop_price))

        # Timestamps
        if self.created_at_us:
            proto_order.created_at_us = self.created_at_us

        # Parent trade ID
        if self.parent_trade_id:
            proto_order.parent_trade_id = self.parent_trade_id

        # Broker
        if self.broker:
            proto_order.broker = self.broker.value  # type: ignore[assignment]

        return proto_order

    @classmethod
    def from_proto(cls, proto_order: strategy_common_pb2.Order) -> Order:
        """Create Order from protobuf message.

        Args:
            proto_order: Protobuf Order message

        Returns:
            Order instance
        """
        return cls(
            order_id=proto_order.order_id,
            symbol=proto_order.symbol,
            status=OrderStatus(proto_order.status),
            side=OrderSide(proto_order.side),
            order_type=OrderType(proto_order.order_type),
            quantity=precise_decimal_to_decimal(proto_order.quantity),
            filled_quantity=precise_decimal_to_decimal(proto_order.filled_quantity),
            limit_price=optional_precise_decimal_to_decimal(proto_order.limit_price),
            stop_price=optional_precise_decimal_to_decimal(proto_order.stop_price),
            created_at_us=proto_order.created_at_us if proto_order.created_at_us else None,
            parent_trade_id=proto_order.parent_trade_id if proto_order.parent_trade_id else None,
            broker=Broker(proto_order.broker) if proto_order.broker else None,
        )

    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled.

        Returns:
            True if fully filled
        """
        return self.status == OrderStatus.FILLED

    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled.

        Returns:
            True if some quantity is filled but not all
        """
        return self.filled_quantity > 0 and self.filled_quantity < self.quantity

    @property
    def is_active(self) -> bool:
        """Check if order is still active.

        Returns:
            True if order can still be executed or modified
        """
        return self.status.is_active()

    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal state.

        Returns:
            True if order processing is complete
        """
        return self.status.is_terminal()

    @property
    def remaining_quantity(self) -> Decimal:
        """Get remaining unfilled quantity.

        Returns:
            Quantity not yet filled
        """
        return self.quantity - self.filled_quantity

    @property
    def fill_percentage(self) -> Decimal:
        """Get percentage of order filled.

        Returns:
            Percentage filled (0.0 to 1.0)
        """
        if self.quantity == 0:
            return Decimal("0")
        return self.filled_quantity / self.quantity

    def __str__(self) -> str:
        """Return string representation of order."""
        return f"Order({self.order_id}: {self.side.name} {self.quantity} " f"{self.symbol} @ {self.order_type.name}, {self.status.name})"
