"""Strategy server for handling gRPC requests."""

from __future__ import annotations

import logging
from typing import Dict, List

import grpc
from strategy.v1 import handler_init_pb2, handler_process_event_pb2, handler_shutdown_pb2, strategy_service_pb2_grpc

from tektii.models.strategy.events import AccountUpdateEvent, CandleData, OptionGreeks, OrderUpdateEvent, TradeUpdate
from tektii.strategy import TektiiStrategy

logger = logging.getLogger(__name__)


class TektiiStrategyServer(strategy_service_pb2_grpc.TektiiStrategyServiceServicer):
    """TektiiStrategyServer handles incoming gRPC requests for strategy events.

    It processes market data, order updates, and other events for strategies.
    """

    def __init__(self, strategy: TektiiStrategy) -> None:
        """Initialize the strategy server.

        Args:
            strategy: The trading strategy instance to handle events
        """
        self.strategy = strategy
        self.logger = logger

    def Initialize(
        self,
        request: handler_init_pb2.InitializeRequest,
        context: grpc.ServicerContext,
    ) -> handler_init_pb2.InitializeResponse:
        """Initialize the strategy with configuration and symbols.

        Args:
            request: Initialization request containing config and symbols
            context: gRPC context

        Returns:
            InitializeResponse confirming successful initialization
        """
        try:
            # Extract config and symbols from request
            config: Dict[str, str] = dict(request.config)
            symbols: List[str] = list(request.symbols)

            # Initialize the strategy
            self.strategy.on_initalize(config, symbols)

            self.logger.info(f"Strategy initialized with {len(symbols)} symbols")

            return handler_init_pb2.InitializeResponse(success=True, message="Strategy initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Strategy initialization failed: {str(e)}")
            return handler_init_pb2.InitializeResponse(success=False, message=f"Initialization failed: {str(e)}")

    def ProcessEvent(
        self,
        request: handler_process_event_pb2.ProcessEventRequest,
        context: grpc.ServicerContext,
    ) -> handler_process_event_pb2.ProcessEventResponse:
        """Process incoming events from the trading engine.

        Args:
            request: Event request containing market data or updates
            context: gRPC context

        Returns:
            ProcessEventResponse acknowledging event processing
        """
        try:
            # Process based on event type
            if request.HasField("candle_data"):
                candle = CandleData.from_proto(request.candle_data)
                self.strategy.on_candle_data(candle)

            elif request.HasField("option_greeks"):
                greeks = OptionGreeks.from_proto(request.option_greeks)
                self.strategy.on_option_greeks(greeks)

            elif request.HasField("order_update"):
                order = OrderUpdateEvent.from_proto(request.order_update)
                self.strategy.on_order_update(order)

            elif request.HasField("account_update"):
                account = AccountUpdateEvent.from_proto(request.account_update)
                self.strategy.on_account_update(account)

            elif request.HasField("trade_update"):
                trade = TradeUpdate.from_proto(request.trade_update)
                self.strategy.on_trade_update(trade)

            else:
                self.logger.warning(f"Received unknown event type for event_id: {request.event_id}")

            return handler_process_event_pb2.ProcessEventResponse(success=True)

        except Exception as e:
            self.logger.error(f"Failed to process event {request.event_id}: {e}")
            return handler_process_event_pb2.ProcessEventResponse(success=False, error=str(e))

    def Shutdown(
        self,
        request: handler_shutdown_pb2.ShutdownRequest,
        context: grpc.ServicerContext,
    ) -> handler_shutdown_pb2.ShutdownResponse:
        """Shutdown the strategy gracefully.

        Args:
            request: Shutdown request
            context: gRPC context

        Returns:
            ShutdownResponse confirming shutdown
        """
        try:
            # Call strategy shutdown
            self.strategy.on_shutdown()

            self.logger.info("Strategy shutdown successfully")

            return handler_shutdown_pb2.ShutdownResponse(success=True, message="Strategy shutdown complete")
        except Exception as e:
            self.logger.error(f"Failed to shutdown strategy: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Strategy shutdown failed: {str(e)}")
            return handler_shutdown_pb2.ShutdownResponse(success=False, message=f"Shutdown failed: {str(e)}")
