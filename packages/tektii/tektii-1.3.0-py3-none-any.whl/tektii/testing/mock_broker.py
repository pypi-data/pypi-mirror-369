"""Mock broker stub for validation and testing."""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from broker.v1 import (
    handler_cancel_order_pb2,
    handler_close_position_pb2,
    handler_get_historical_data_pb2,
    handler_get_market_depth_pb2,
    handler_get_state_pb2,
    handler_modify_order_pb2,
    handler_modify_trade_protection_pb2,
    handler_place_order_pb2,
)

from ..models.broker.conversions import decimal_to_precise_decimal

logger = logging.getLogger(__name__)


class MockBrokerStub:
    """Mock implementation of TektiiBrokerServiceStub for validation and testing.

    This mock broker provides realistic responses without requiring a real broker connection.
    It maintains basic state to simulate broker behavior during validation.
    """

    def __init__(self) -> None:
        """Initialize the mock broker with default state."""
        self.orders: Dict[str, Any] = {}
        self.positions: Dict[str, Any] = {}
        self.order_counter = 0
        self.account = self._create_mock_account()
        self.call_history: List[tuple[str, Any]] = []

    def _create_mock_account(self) -> Dict[str, Any]:
        """Create a mock account with reasonable defaults."""
        return {
            "account_id": "MOCK-ACCOUNT-001",
            "cash_balance": Decimal("100000.00"),
            "buying_power": Decimal("100000.00"),
            "total_equity": Decimal("100000.00"),
            "margin_used": Decimal("0.00"),
            "currency": "USD",
        }

    def _next_order_id(self) -> str:
        """Generate the next order ID."""
        self.order_counter += 1
        return f"MOCK-ORDER-{self.order_counter:06d}"

    def _track_call(self, method: str, request: Any) -> None:
        """Track method calls for debugging."""
        self.call_history.append((method, request))
        logger.debug(f"Mock broker received {method} call")

    def GetState(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock GetState - returns current mock broker state."""
        self._track_call("GetState", request)

        # Create proto response directly
        response = handler_get_state_pb2.GetStateResponse()

        # Add account state
        account_state = handler_get_state_pb2.AccountState()
        account_state.cash_balance.CopyFrom(decimal_to_precise_decimal(Decimal("100000.00"), "broker"))
        account_state.buying_power.CopyFrom(decimal_to_precise_decimal(Decimal("100000.00"), "broker"))
        account_state.portfolio_value.CopyFrom(decimal_to_precise_decimal(Decimal("100000.00"), "broker"))
        account_state.margin_used.CopyFrom(decimal_to_precise_decimal(Decimal("0.00"), "broker"))
        response.account.CopyFrom(account_state)

        return response

    def PlaceOrder(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock PlaceOrder - always succeeds with a new order ID."""
        self._track_call("PlaceOrder", request)

        # Generate order ID
        order_id = self._next_order_id()

        # Create proto response directly
        response = handler_place_order_pb2.PlaceOrderResponse(
            accepted=True,
            order_id=order_id,
            request_id=f"REQ-{order_id}",
        )

        logger.debug(f"Mock broker placed order: {order_id}")
        return response

    def CancelOrder(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock CancelOrder - always succeeds."""
        self._track_call("CancelOrder", request)

        # Create proto response directly
        response = handler_cancel_order_pb2.CancelOrderResponse()
        response.accepted = True
        response.reject_reason = f"Order {request.order_id} cancelled successfully (mock)"

        logger.debug(f"Mock broker cancelled order: {request.order_id}")
        return response

    def ModifyOrder(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock ModifyOrder - always accepts modifications."""
        self._track_call("ModifyOrder", request)

        # Create proto response directly
        response = handler_modify_order_pb2.ModifyOrderResponse(accepted=True, order_id=request.order_id)

        logger.debug(f"Mock broker modified order: {request.order_id}")
        return response

    def ClosePosition(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock ClosePosition - always succeeds."""
        self._track_call("ClosePosition", request)

        # Create proto response directly
        response = handler_close_position_pb2.ClosePositionResponse()
        response.accepted = True
        response.reject_reason = f"Position for {request.symbol} closed successfully (mock)"

        logger.debug(f"Mock broker closed position: {request.symbol}")
        return response

    def ModifyTradeProtection(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock ModifyTradeProtection - always succeeds."""
        self._track_call("ModifyTradeProtection", request)

        # Create proto response directly
        response = handler_modify_trade_protection_pb2.ModifyTradeProtectionResponse()
        response.accepted = True
        response.trade_id = request.trade_id

        logger.debug(f"Mock broker modified trade protection: {request.trade_id}")
        return response

    def GetHistoricalData(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock GetHistoricalData - returns empty data."""
        self._track_call("GetHistoricalData", request)

        # Create proto response directly
        response = handler_get_historical_data_pb2.GetHistoricalDataResponse()
        # candles is a repeated field, leave empty for simplicity

        logger.debug(f"Mock broker returned historical data for {request.symbol}")
        return response

    def GetMarketDepth(self, request: Any, timeout: Optional[float] = None) -> Any:
        """Mock GetMarketDepth - returns empty depth."""
        self._track_call("GetMarketDepth", request)

        # Create proto response directly
        response = handler_get_market_depth_pb2.GetMarketDepthResponse()
        # bids and asks are repeated fields, leave empty for simplicity

        logger.debug(f"Mock broker returned market depth for {request.symbol}")
        return response
