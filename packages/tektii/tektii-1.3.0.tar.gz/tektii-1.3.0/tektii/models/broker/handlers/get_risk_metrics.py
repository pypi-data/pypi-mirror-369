"""Get risk metrics request and response handlers."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from broker.v1 import handler_get_risk_metrics_pb2
from pydantic import BaseModel, Field

from ..types.position_risk import PositionRisk


class RiskMetricsRequest(BaseModel):
    """Request for risk metrics calculation."""

    symbols: List[str] = Field(default_factory=list, description="Symbols to calculate metrics for (empty = all)")
    confidence_level: Optional[Decimal] = Field(default=None, description="Confidence level for VaR calculation")
    lookback_days: Optional[int] = Field(default=None, description="Number of days to look back for calculations")

    def to_proto(self) -> handler_get_risk_metrics_pb2.GetRiskMetricsRequest:
        """Convert to protobuf message."""
        from ..conversions import decimal_to_precise_decimal

        proto = handler_get_risk_metrics_pb2.GetRiskMetricsRequest(symbols=self.symbols)
        if self.confidence_level is not None:
            proto.confidence_level.CopyFrom(decimal_to_precise_decimal(self.confidence_level))
        if self.lookback_days is not None:
            proto.lookback_days = self.lookback_days
        return proto


class RiskMetricsResponse(BaseModel):
    """Response containing risk metrics."""

    position_risks: Dict[str, PositionRisk] = Field(default_factory=dict, description="Position-level risk metrics by symbol")
    portfolio_var: Optional[Decimal] = Field(default=None, description="Portfolio Value at Risk")
    portfolio_sharpe: Optional[Decimal] = Field(default=None, description="Portfolio Sharpe ratio")
    portfolio_beta: Optional[Decimal] = Field(default=None, description="Portfolio beta")
    max_drawdown: Optional[Decimal] = Field(default=None, description="Maximum drawdown")
    correlations: Dict[str, Optional[Decimal]] = Field(default_factory=dict, description="Correlation matrix")
    timestamp_us: int = Field(description="Metrics calculation timestamp in microseconds")

    @classmethod
    def from_proto(cls, proto: handler_get_risk_metrics_pb2.GetRiskMetricsResponse) -> RiskMetricsResponse:
        """Create from protobuf message."""
        from ..conversions import optional_precise_decimal_to_decimal, precise_decimal_to_decimal

        position_risks = {}
        for symbol, risk_proto in proto.position_risks.items():
            position_risks[symbol] = PositionRisk.from_proto(risk_proto)

        correlations = {}
        for key, value_proto in proto.correlations.items():
            correlations[key] = precise_decimal_to_decimal(value_proto) if value_proto else None

        return cls(
            position_risks=position_risks,
            portfolio_var=optional_precise_decimal_to_decimal(proto.portfolio_var) if proto.HasField("portfolio_var") else None,
            portfolio_sharpe=optional_precise_decimal_to_decimal(proto.portfolio_sharpe) if proto.HasField("portfolio_sharpe") else None,
            portfolio_beta=optional_precise_decimal_to_decimal(proto.portfolio_beta) if proto.HasField("portfolio_beta") else None,
            max_drawdown=optional_precise_decimal_to_decimal(proto.max_drawdown) if proto.HasField("max_drawdown") else None,
            correlations=correlations,
            timestamp_us=proto.timestamp_us,
        )
