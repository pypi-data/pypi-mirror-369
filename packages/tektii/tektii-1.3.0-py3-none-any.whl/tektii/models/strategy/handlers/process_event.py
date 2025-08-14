"""Module docstring."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from pydantic import BaseModel, Field
from strategy.v1 import handler_process_event_pb2

from ..types.broker import Broker

if TYPE_CHECKING:
    from ..events.account_update import AccountUpdateEvent
    from ..events.candle_data import CandleData
    from ..events.option_greeks import OptionGreeks
    from ..events.order_update import OrderUpdateEvent
    from ..events.trade_update import TradeUpdate


class ProcessEventRequest(BaseModel):
    """Request to process an event."""

    event_id: str = Field(description="Unique identifier for the event")
    timestamp_us: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000), description="Timestamp in microseconds")
    broker: Optional[Broker] = Field(default=None, description="Broker")
    candle_data: Optional[CandleData] = Field(default=None, description="Candle data if available")
    option_greeks: Optional[OptionGreeks] = Field(default=None, description="Option greeks if available")
    order_update: Optional[OrderUpdateEvent] = Field(default=None, description="Order update event if available")
    account_update: Optional[AccountUpdateEvent] = Field(default=None, description="Account update event if available")
    trade_update: Optional[TradeUpdate] = Field(default=None, description="Trade update event if available")

    @classmethod
    def from_proto(cls, proto: handler_process_event_pb2.ProcessEventRequest) -> ProcessEventRequest:
        """Create from protobuf message."""
        # Import event types here to avoid circular imports
        from ..events.account_update import AccountUpdateEvent
        from ..events.candle_data import CandleData
        from ..events.option_greeks import OptionGreeks
        from ..events.order_update import OrderUpdateEvent
        from ..events.trade_update import TradeUpdate

        # Build the object with proper types
        obj = cls(
            event_id=proto.event_id,
            timestamp_us=proto.timestamp_us,
        )

        if proto.HasField("broker"):
            obj.broker = Broker.from_proto(proto.broker)

        if proto.HasField("candle_data"):
            obj.candle_data = CandleData.from_proto(proto.candle_data)
        if proto.HasField("option_greeks"):
            obj.option_greeks = OptionGreeks.from_proto(proto.option_greeks)

        if proto.HasField("order_update"):
            obj.order_update = OrderUpdateEvent.from_proto(proto.order_update)
        if proto.HasField("account_update"):
            obj.account_update = AccountUpdateEvent.from_proto(proto.account_update)
        if proto.HasField("trade_update"):
            obj.trade_update = TradeUpdate.from_proto(proto.trade_update)

        return obj


class ProcessEventResponse(BaseModel):
    """Response to event processing."""

    success: bool = Field(description="Whether event was processed successfully")
    error: Optional[str] = Field(default=None, description="Error message if processing failed")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Response metadata")

    def to_proto(self) -> handler_process_event_pb2.ProcessEventResponse:
        """Convert to protobuf message."""
        proto = handler_process_event_pb2.ProcessEventResponse(success=self.success)

        if self.error:
            proto.error = self.error

        # Add metadata
        for key, value in self.metadata.items():
            proto.metadata[key] = value

        return proto
