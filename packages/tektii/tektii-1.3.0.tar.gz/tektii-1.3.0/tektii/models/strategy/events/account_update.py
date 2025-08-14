"""Module docstring."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from strategy.v1 import event_account_update_pb2

from ..conversions import decimal_to_precise_decimal, optional_precise_decimal_to_decimal


class AccountUpdateEvent(BaseModel):
    """Event triggered when account state changes."""

    cash_balance: Optional[Decimal] = Field(default=None, description="Available cash balance")
    portfolio_value: Optional[Decimal] = Field(default=None, description="Total portfolio value")
    buying_power: Optional[Decimal] = Field(default=None, description="Available buying power")
    initial_margin: Optional[Decimal] = Field(default=None, description="Initial margin requirement")
    maintenance_margin: Optional[Decimal] = Field(default=None, description="Maintenance margin requirement")
    margin_used: Optional[Decimal] = Field(default=None, description="Margin currently in use")
    total_pnl: Optional[Decimal] = Field(default=None, description="Total P&L")
    leverage: Optional[Decimal] = Field(default=None, description="Current leverage")

    def to_proto(self) -> event_account_update_pb2.AccountUpdateEvent:
        """Convert to protobuf message."""
        proto = event_account_update_pb2.AccountUpdateEvent()

        if self.cash_balance is not None:
            proto.cash_balance.CopyFrom(decimal_to_precise_decimal(self.cash_balance, "strategy"))
        if self.portfolio_value is not None:
            proto.portfolio_value.CopyFrom(decimal_to_precise_decimal(self.portfolio_value, "strategy"))
        if self.buying_power is not None:
            proto.buying_power.CopyFrom(decimal_to_precise_decimal(self.buying_power, "strategy"))
        if self.initial_margin is not None:
            proto.initial_margin.CopyFrom(decimal_to_precise_decimal(self.initial_margin, "strategy"))
        if self.maintenance_margin is not None:
            proto.maintenance_margin.CopyFrom(decimal_to_precise_decimal(self.maintenance_margin, "strategy"))
        if self.margin_used is not None:
            proto.margin_used.CopyFrom(decimal_to_precise_decimal(self.margin_used, "strategy"))
        if self.total_pnl is not None:
            proto.total_pnl.CopyFrom(decimal_to_precise_decimal(self.total_pnl, "strategy"))
        if self.leverage is not None:
            proto.leverage.CopyFrom(decimal_to_precise_decimal(self.leverage, "strategy"))

        return proto

    @classmethod
    def from_proto(cls, proto: event_account_update_pb2.AccountUpdateEvent) -> AccountUpdateEvent:
        """Create from protobuf message."""
        return cls(
            cash_balance=optional_precise_decimal_to_decimal(proto.cash_balance) if proto.HasField("cash_balance") else None,
            portfolio_value=optional_precise_decimal_to_decimal(proto.portfolio_value) if proto.HasField("portfolio_value") else None,
            buying_power=optional_precise_decimal_to_decimal(proto.buying_power) if proto.HasField("buying_power") else None,
            initial_margin=optional_precise_decimal_to_decimal(proto.initial_margin) if proto.HasField("initial_margin") else None,
            maintenance_margin=optional_precise_decimal_to_decimal(proto.maintenance_margin) if proto.HasField("maintenance_margin") else None,
            margin_used=optional_precise_decimal_to_decimal(proto.margin_used) if proto.HasField("margin_used") else None,
            total_pnl=optional_precise_decimal_to_decimal(proto.total_pnl) if proto.HasField("total_pnl") else None,
            leverage=optional_precise_decimal_to_decimal(proto.leverage) if proto.HasField("leverage") else None,
        )
