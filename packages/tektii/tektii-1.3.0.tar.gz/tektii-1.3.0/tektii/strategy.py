"""Base strategy class for Tektii Strategy SDK.

This module provides the base class that all trading strategies should inherit from.
It handles event routing, state management, and communication with the trading system.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import grpc

if TYPE_CHECKING:
    from broker.v1.broker_service_pb2_grpc import TektiiBrokerServiceStub

from .models.broker.handlers import (
    CancelOrderRequest,
    CancelOrderResponse,
    ClosePositionRequest,
    ClosePositionResponse,
    HistoricalDataRequest,
    HistoricalDataResponse,
    MarketDepthRequest,
    MarketDepthResponse,
    PlaceOrderRequest,
    PlaceOrderResponse,
    StateRequest,
    StateResponse,
)
from .models.strategy.events import AccountUpdateEvent, CandleData, OptionGreeks, OrderUpdateEvent, TradeUpdate
from .testing import MockBrokerStub

# Setup logging
logger = logging.getLogger(__name__)


class TektiiStrategy:
    """Base class for all Tektii trading strategies."""

    def __init__(self, broker_address: str | None = None, max_retries: int = 5, initial_backoff: float = 1.0) -> None:
        """Initialize the strategy with optional broker connection.

        Args:
            broker_address: The broker gRPC server address (optional, None for testing without broker)
            max_retries: Maximum number of connection attempts (only used if broker_address is provided)
            initial_backoff: Initial backoff time in seconds for exponential backoff (only used if broker_address is provided)
        """
        self._config: Dict[str, str] = {}
        self.logger = logger
        self.broker_address = broker_address
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[Union[TektiiBrokerServiceStub, MockBrokerStub]] = None

        if broker_address is not None:
            # Create channel with keepalive settings
            self.channel = grpc.insecure_channel(
                broker_address,
                options=[
                    ("grpc.keepalive_time_ms", 30000),
                    ("grpc.keepalive_timeout_ms", 10000),
                    ("grpc.keepalive_permit_without_calls", True),
                ],
            )

    def _create_broker_stub(self) -> None:
        """Create the broker gRPC stub with retry logic."""
        if self.channel is None:
            self.logger.warning("Cannot create broker stub: no gRPC channel available")
            return

        # Import here to avoid circular imports
        from broker.v1.broker_service_pb2_grpc import TektiiBrokerServiceStub

        for attempt in range(self.max_retries):
            try:
                self.stub = TektiiBrokerServiceStub(self.channel)  # type: ignore[no-untyped-call]
                self.logger.info(f"Successfully created broker stub on attempt {attempt + 1}")
                return
            except Exception as e:
                backoff_time = self.initial_backoff * (2**attempt)
                self.logger.warning(f"Failed to create broker stub (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    self.logger.error("Max retries reached. Unable to create broker stub.")
                    raise

    def _ensure_broker_connection(self) -> None:
        """Ensure broker connection is established."""
        if self.stub is None and self.channel is not None:
            self.logger.info("Creating broker stub...")
            self._create_broker_stub()

        # Test the connection if we have a real stub
        if self.stub is not None and not isinstance(self.stub, MockBrokerStub) and not self._health_check():
            self.logger.warning("Broker health check failed, attempting to recreate stub...")
            self._create_broker_stub()

    def _health_check(self) -> bool:
        """Perform a health check on the broker connection."""
        if self.stub is None:
            return False

        # For mock stub, always return True
        if isinstance(self.stub, MockBrokerStub):
            return True

        # For real broker stub, try a simple state request
        try:
            state_request = StateRequest()
            self.stub.GetState(state_request.to_proto(), timeout=5.0)
            self.logger.debug("Broker health check successful")
            return True
        except grpc.RpcError as e:
            self.logger.debug(f"Health check failed with gRPC error: {e.code()}: {e.details()}")
            return False
        except Exception as e:
            self.logger.debug(f"Health check failed with exception: {e}")
            return False

    def on_candle_data(self, candle_data: CandleData) -> None:
        """Handle candle data events.

        Override this method to implement your strategy's response to candle (OHLCV) data.

        Args:
            candle_data: Candle data containing open, high, low, close, volume
        """
        pass

    def on_option_greeks(self, option_greeks: OptionGreeks) -> None:
        """Handle option greeks events.

        Override this method to implement your strategy's response to option greeks.

        Args:
            option_greeks: Option greeks data containing delta, gamma, theta, vega, rho
        """
        pass

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order update events.

        Override this method to react to order status changes.

        Args:
            order_update: Order update event
        """
        pass

    def on_account_update(self, account_update: AccountUpdateEvent) -> None:
        """Handle account update events.

        Override this method to react to account changes.

        Args:
            account_update: Account update event
        """
        pass

    def on_trade_update(self, trade_update: TradeUpdate) -> None:
        """Handle trade update events.

        Override this method to react to trade updates.

        Args:
            trade_update: Trade update event
        """
        pass

    def on_initalize(self, config: Dict[str, str], symbols: List[str]) -> None:
        """Initialize the strategy.

        Override this method to set up your strategy state.

        Args:
            config: Configuration parameters
            symbols: List of symbols the strategy will trade
        """
        pass

    def on_shutdown(self) -> None:
        """Shut down the strategy.

        Override this method to clean up resources.
        """
        pass

    def get_state(self, request: StateRequest, timeout: float = 10.0) -> StateResponse:
        """Query current state from the broker.

        Args:
            request: State request parameters
            timeout: Request timeout in seconds

        Returns:
            State response containing account and position information

        Raises:
            RuntimeError: If broker connection is not available
            grpc.RpcError: If the request fails
        """
        if self.stub is None:
            self._ensure_broker_connection()

        if self.stub is None:
            raise RuntimeError("Broker connection not available")

        try:
            response_proto = self.stub.GetState(request.to_proto(), timeout=timeout)
            return StateResponse.from_proto(response_proto)
        except grpc.RpcError as e:
            self.logger.error(f"GetState failed: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"GetState failed with unexpected error: {e}")
            raise

    def place_order(self, request: PlaceOrderRequest, timeout: float = 10.0) -> PlaceOrderResponse:
        """Place a trading order.

        Args:
            request: Order placement request
            timeout: Request timeout in seconds

        Returns:
            Order placement response

        Raises:
            RuntimeError: If broker connection is not available
            grpc.RpcError: If the request fails
        """
        if self.stub is None:
            self._ensure_broker_connection()

        if self.stub is None:
            raise RuntimeError("Broker connection not available")

        try:
            response_proto = self.stub.PlaceOrder(request.to_proto(), timeout=timeout)
            return PlaceOrderResponse.from_proto(response_proto)
        except grpc.RpcError as e:
            self.logger.error(f"PlaceOrder failed: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"PlaceOrder failed with unexpected error: {e}")
            raise

    def cancel_order(self, request: CancelOrderRequest, timeout: float = 10.0) -> CancelOrderResponse:
        """Cancel an existing order.

        Args:
            request: Order cancellation request
            timeout: Request timeout in seconds

        Returns:
            Order cancellation response

        Raises:
            RuntimeError: If broker connection is not available
            grpc.RpcError: If the request fails
        """
        if self.stub is None:
            self._ensure_broker_connection()

        if self.stub is None:
            raise RuntimeError("Broker connection not available")

        try:
            response_proto = self.stub.CancelOrder(request.to_proto(), timeout=timeout)
            return CancelOrderResponse.from_proto(response_proto)
        except grpc.RpcError as e:
            self.logger.error(f"CancelOrder failed: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"CancelOrder failed with unexpected error: {e}")
            raise

    def close_position(self, request: ClosePositionRequest, timeout: float = 10.0) -> ClosePositionResponse:
        """Close an existing position.

        Args:
            request: Position closure request
            timeout: Request timeout in seconds

        Returns:
            Position closure response

        Raises:
            RuntimeError: If broker connection is not available
            grpc.RpcError: If the request fails
        """
        if self.stub is None:
            self._ensure_broker_connection()

        if self.stub is None:
            raise RuntimeError("Broker connection not available")

        try:
            response_proto = self.stub.ClosePosition(request.to_proto(), timeout=timeout)
            return ClosePositionResponse.from_proto(response_proto)
        except grpc.RpcError as e:
            self.logger.error(f"ClosePosition failed: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"ClosePosition failed with unexpected error: {e}")
            raise

    def get_historical_data(self, request: HistoricalDataRequest, timeout: float = 30.0) -> HistoricalDataResponse:
        """Get historical market data.

        Args:
            request: Historical data request
            timeout: Request timeout in seconds

        Returns:
            Historical data response

        Raises:
            RuntimeError: If broker connection is not available
            grpc.RpcError: If the request fails
        """
        if self.stub is None:
            self._ensure_broker_connection()

        if self.stub is None:
            raise RuntimeError("Broker connection not available")

        try:
            response_proto = self.stub.GetHistoricalData(request.to_proto(), timeout=timeout)
            return HistoricalDataResponse.from_proto(response_proto)
        except grpc.RpcError as e:
            self.logger.error(f"GetHistoricalData failed: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"GetHistoricalData failed with unexpected error: {e}")
            raise

    def get_market_depth(self, request: MarketDepthRequest, timeout: float = 10.0) -> MarketDepthResponse:
        """Get market depth data.

        Args:
            request: Market depth request
            timeout: Request timeout in seconds

        Returns:
            Market depth response

        Raises:
            RuntimeError: If broker connection is not available
            grpc.RpcError: If the request fails
        """
        if self.stub is None:
            self._ensure_broker_connection()

        if self.stub is None:
            raise RuntimeError("Broker connection not available")

        try:
            response_proto = self.stub.GetMarketDepth(request.to_proto(), timeout=timeout)
            return MarketDepthResponse.from_proto(response_proto)
        except grpc.RpcError as e:
            self.logger.error(f"GetMarketDepth failed: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"GetMarketDepth failed with unexpected error: {e}")
            raise

    def __del__(self) -> None:
        """Clean up resources when the strategy is destroyed."""
        if self.channel is not None:
            try:
                self.channel.close()
            except Exception as e:
                self.logger.warning(f"Error closing gRPC channel: {e}")
