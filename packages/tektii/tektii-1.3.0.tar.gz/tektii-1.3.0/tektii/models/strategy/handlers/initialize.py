"""Module docstring."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from strategy.v1 import handler_init_pb2


class InitRequest(BaseModel):
    """Strategy initialization parameters."""

    strategy_id: str = Field(description="Unique strategy identifier")
    config: Dict[str, str] = Field(default_factory=dict, description="Strategy configuration parameters")
    symbols: List[str] = Field(default_factory=list, description="Symbols to trade")

    @classmethod
    def from_proto(cls, proto: handler_init_pb2.InitializeRequest) -> InitRequest:
        """Create from protobuf message."""
        return cls(strategy_id=proto.strategy_id, config=dict(proto.config), symbols=list(proto.symbols))


class InitResponse(BaseModel):
    """Response to initialization request."""

    success: bool = Field(description="Whether initialization succeeded")
    message: Optional[str] = Field(default=None, description="Response message")
    capabilities: Dict[str, str] = Field(default_factory=dict, description="Strategy capabilities")

    def to_proto(self) -> handler_init_pb2.InitializeResponse:
        """Convert to protobuf message."""
        proto = handler_init_pb2.InitializeResponse(success=self.success)

        if self.message:
            proto.message = self.message

        # Add capabilities as a map
        for key, value in self.capabilities.items():
            proto.capabilities[key] = value

        return proto
