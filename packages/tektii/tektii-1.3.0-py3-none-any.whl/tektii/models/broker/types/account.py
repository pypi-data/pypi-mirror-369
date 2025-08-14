"""Account state model for broker operations."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from broker.v1 import handler_get_state_pb2
from pydantic import BaseModel, Field

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal


class Account(BaseModel):
    """Account state information including balances and margin details."""

    cash_balance: Optional[Decimal] = Field(default=None, description="Available cash balance")
    portfolio_value: Optional[Decimal] = Field(default=None, description="Total portfolio value")
    buying_power: Optional[Decimal] = Field(default=None, description="Available buying power")
    margin_used: Optional[Decimal] = Field(default=None, description="Currently used margin")
    initial_margin: Optional[Decimal] = Field(default=None, description="Initial margin requirement")
    maintenance_margin: Optional[Decimal] = Field(default=None, description="Maintenance margin requirement")
    total_pnl: Optional[Decimal] = Field(default=None, description="Total profit and loss")

    @classmethod
    def from_proto(cls, proto: handler_get_state_pb2.AccountState) -> Account:
        """Create from protobuf message."""
        return cls(
            cash_balance=optional_precise_decimal_to_decimal(proto.cash_balance) if proto.HasField("cash_balance") else None,
            portfolio_value=optional_precise_decimal_to_decimal(proto.portfolio_value) if proto.HasField("portfolio_value") else None,
            buying_power=optional_precise_decimal_to_decimal(proto.buying_power) if proto.HasField("buying_power") else None,
            margin_used=optional_precise_decimal_to_decimal(proto.margin_used) if proto.HasField("margin_used") else None,
            initial_margin=optional_precise_decimal_to_decimal(proto.initial_margin) if proto.HasField("initial_margin") else None,
            maintenance_margin=optional_precise_decimal_to_decimal(proto.maintenance_margin) if proto.HasField("maintenance_margin") else None,
            total_pnl=optional_precise_decimal_to_decimal(proto.total_pnl) if proto.HasField("total_pnl") else None,
        )

    def to_proto(self) -> handler_get_state_pb2.AccountState:
        """Convert to protobuf message."""
        proto = handler_get_state_pb2.AccountState()

        if self.cash_balance is not None:
            proto.cash_balance.CopyFrom(decimal_to_precise_decimal(self.cash_balance))
        if self.portfolio_value is not None:
            proto.portfolio_value.CopyFrom(decimal_to_precise_decimal(self.portfolio_value))
        if self.buying_power is not None:
            proto.buying_power.CopyFrom(decimal_to_precise_decimal(self.buying_power))
        if self.margin_used is not None:
            proto.margin_used.CopyFrom(decimal_to_precise_decimal(self.margin_used))
        if self.initial_margin is not None:
            proto.initial_margin.CopyFrom(decimal_to_precise_decimal(self.initial_margin))
        if self.maintenance_margin is not None:
            proto.maintenance_margin.CopyFrom(decimal_to_precise_decimal(self.maintenance_margin))
        if self.total_pnl is not None:
            proto.total_pnl.CopyFrom(decimal_to_precise_decimal(self.total_pnl))

        return proto
