"""Strategy shutdown handler."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from strategy.v1 import handler_shutdown_pb2


class ShutdownRequest(BaseModel):
    """Strategy shutdown request."""

    reason: str = Field(default="Normal shutdown", description="Shutdown reason")
    force: bool = Field(default=False, description="Force immediate shutdown")

    def to_proto(self) -> handler_shutdown_pb2.ShutdownRequest:
        """Convert to protobuf message."""
        return handler_shutdown_pb2.ShutdownRequest(reason=self.reason, force=self.force)

    @classmethod
    def from_proto(cls, proto: handler_shutdown_pb2.ShutdownRequest) -> ShutdownRequest:
        """Create from protobuf message."""
        return cls(reason=proto.reason, force=proto.force)


class ShutdownResponse(BaseModel):
    """Response to shutdown request."""

    success: bool = Field(description="Whether shutdown succeeded")
    message: Optional[str] = Field(default=None, description="Response message")

    def to_proto(self) -> handler_shutdown_pb2.ShutdownResponse:
        """Convert to protobuf message."""
        proto = handler_shutdown_pb2.ShutdownResponse(success=self.success)
        if self.message:
            proto.message = self.message
        return proto

    @classmethod
    def from_proto(cls, proto: handler_shutdown_pb2.ShutdownResponse) -> ShutdownResponse:
        """Create from protobuf message."""
        return cls(success=proto.success, message=proto.message if proto.message else None)
