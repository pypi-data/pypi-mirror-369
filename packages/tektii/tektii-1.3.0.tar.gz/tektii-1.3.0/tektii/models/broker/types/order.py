"""Order model and related types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from broker.v1 import broker_common_pb2
from pydantic import BaseModel, Field, field_validator, model_validator

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal, precise_decimal_to_decimal
from .broker import Broker
from .order_intent import OrderIntent
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
    created_at_us: int = Field(..., description="Creation timestamp (microseconds)")
    order_intent: Optional[OrderIntent] = Field(None, description="Order purpose (broker service only)")
    parent_trade_id: Optional[str] = Field(None, description="Parent trade ID for protective orders")
    broker: Optional[Broker] = Field(None, description="Broker/venue (strategy service only)")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "filled_quantity", "limit_price", "stop_price")
    @classmethod
    def validate_decimal(cls, v: Union[int, float, str, Decimal, None]) -> Optional[Decimal]:
        """Ensure all numeric fields are Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @field_validator("status", mode="before")
    @classmethod
    def convert_status(cls, v: Union[OrderStatus, int, str]) -> OrderStatus:
        """Convert status value to OrderStatus."""
        if isinstance(v, OrderStatus):
            return v
        elif isinstance(v, int):
            return OrderStatus.from_proto(v)
        elif isinstance(v, str):
            return OrderStatus.from_string(v)
        else:
            raise ValueError(f"Invalid order status: {v}")

    @field_validator("side", mode="before")
    @classmethod
    def convert_side(cls, v: Union[OrderSide, int, str]) -> OrderSide:
        """Convert side value to OrderSide."""
        if isinstance(v, OrderSide):
            return v
        elif isinstance(v, int):
            return OrderSide.from_proto(v)
        elif isinstance(v, str):
            return OrderSide.from_string(v)
        else:
            raise ValueError(f"Invalid order side: {v}")

    @field_validator("order_type", mode="before")
    @classmethod
    def convert_order_type(cls, v: Union[OrderType, int, str]) -> OrderType:
        """Convert order type value to OrderType."""
        if isinstance(v, OrderType):
            return v
        elif isinstance(v, int):
            return OrderType.from_proto(v)
        elif isinstance(v, str):
            return OrderType.from_string(v)
        else:
            raise ValueError(f"Invalid order type: {v}")

    @field_validator("order_intent", mode="before")
    @classmethod
    def convert_order_intent(cls, v: Union[OrderIntent, int, str, None]) -> Optional[OrderIntent]:
        """Convert order intent value to OrderIntent."""
        if v is None:
            return None
        if isinstance(v, OrderIntent):
            return v
        elif isinstance(v, int):
            return OrderIntent.from_proto(v)
        elif isinstance(v, str):
            return OrderIntent.from_string(v)
        else:
            raise ValueError(f"Invalid order intent: {v}")

    @model_validator(mode="after")
    def validate_prices(self) -> Order:
        """Validate price requirements based on order type."""
        if self.order_type.requires_limit_price() and self.limit_price is None:
            raise ValueError(f"{self.order_type} requires limit_price")
        if self.order_type.requires_stop_price() and self.stop_price is None:
            raise ValueError(f"{self.order_type} requires stop_price")
        return self

    @property
    def created_at(self) -> datetime:
        """Get creation time as datetime.

        Returns:
            Order creation timestamp
        """
        return datetime.fromtimestamp(self.created_at_us / 1_000_000)

    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining quantity to fill.

        Returns:
            Unfilled quantity
        """
        return self.quantity - self.filled_quantity

    @property
    def fill_percentage(self) -> Decimal:
        """Calculate fill percentage.

        Returns:
            Percentage of order filled
        """
        if self.quantity == 0:
            return Decimal(0)
        return (self.filled_quantity / self.quantity) * 100

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
            True if order can still be executed
        """
        return bool(self.status.is_active())

    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal state.

        Returns:
            True if order is done (filled, canceled, rejected, or expired)
        """
        return bool(self.status.is_terminal())

    def calculate_value(self) -> Optional[Decimal]:
        """Calculate the total order value.

        Returns:
            Order value based on quantity and price, or None for market orders
        """
        if self.order_type == OrderType.MARKET:
            return None
        elif self.order_type == OrderType.LIMIT and self.limit_price:
            return self.quantity * self.limit_price
        elif self.order_type == OrderType.STOP and self.stop_price:
            return self.quantity * self.stop_price
        elif self.order_type == OrderType.STOP_LIMIT and self.limit_price:
            return self.quantity * self.limit_price
        return None

    @classmethod
    def from_proto(cls, proto: "broker_common_pb2.Order") -> Order:
        """Create Order from broker service proto.

        Args:
            proto: Order proto from broker service

        Returns:
            Order model instance
        """
        return cls(
            order_id=proto.order_id,
            symbol=proto.symbol,
            status=OrderStatus.from_proto(proto.status),
            side=OrderSide.from_proto(proto.side),
            order_type=OrderType.from_proto(proto.order_type),
            quantity=precise_decimal_to_decimal(proto.quantity),
            filled_quantity=precise_decimal_to_decimal(proto.filled_quantity) if proto.filled_quantity else Decimal("0"),
            limit_price=optional_precise_decimal_to_decimal(proto.limit_price),
            stop_price=optional_precise_decimal_to_decimal(proto.stop_price),
            created_at_us=proto.created_at_us,
            order_intent=OrderIntent.from_proto(proto.order_intent) if proto.order_intent else None,
            parent_trade_id=proto.parent_trade_id if proto.parent_trade_id else None,
            broker=None,
        )

    def to_proto(self) -> "broker_common_pb2.Order":
        """Convert to broker service proto.

        Returns:
            Broker service Order proto
        """
        from broker.v1 import broker_common_pb2

        proto = broker_common_pb2.Order()
        proto.order_id = self.order_id
        proto.symbol = self.symbol
        proto.status = self.status.to_proto()
        proto.side = self.side.to_proto()
        proto.order_type = self.order_type.to_proto()
        proto.quantity.CopyFrom(decimal_to_precise_decimal(self.quantity, "broker"))
        if self.filled_quantity:
            proto.filled_quantity.CopyFrom(decimal_to_precise_decimal(self.filled_quantity, "broker"))
        if self.limit_price:
            proto.limit_price.CopyFrom(decimal_to_precise_decimal(self.limit_price, "broker"))
        if self.stop_price:
            proto.stop_price.CopyFrom(decimal_to_precise_decimal(self.stop_price, "broker"))
        proto.created_at_us = self.created_at_us
        if self.order_intent:
            proto.order_intent = self.order_intent.to_proto()
        if self.parent_trade_id:
            proto.parent_trade_id = self.parent_trade_id
        return proto

    def __str__(self) -> str:
        """Human-readable string representation."""
        price_info = ""
        if self.limit_price:
            price_info = f" @ {self.limit_price:.2f}"
        if self.stop_price:
            price_info += f" stop={self.stop_price:.2f}"

        fill_info = ""
        if self.is_partially_filled:
            fill_info = f" ({self.filled_quantity}/{self.quantity} filled)"

        return f"{self.status} {self.order_type} {self.side} " f"{self.quantity} {self.symbol}{price_info}{fill_info}"
