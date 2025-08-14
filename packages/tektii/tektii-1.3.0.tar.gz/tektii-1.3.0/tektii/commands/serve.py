"""Serve command implementation for running strategy as gRPC server."""

import logging
import os
import signal
from concurrent import futures
from typing import Any, Optional, Type

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from strategy.v1.strategy_service_pb2_grpc import add_TektiiStrategyServiceServicer_to_server

from ..server import TektiiStrategyServer
from ..strategy import TektiiStrategy
from ..testing import MockBrokerStub
from ..utils.colors import Colors, print_colored, print_header
from ..utils.loader import load_strategy_class

logger = logging.getLogger(__name__)


def cmd_serve(args: Any) -> int:
    """Run strategy as gRPC server."""
    # Configure logging to show info messages
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")

    module_path = args.module
    class_name = args.class_name

    if not os.path.exists(module_path):
        print_colored(f"Error: {module_path} not found", Colors.FAIL)
        return 1

    print_header(f"Starting gRPC server for {class_name}")

    try:
        # Load strategy class
        strategy_class = load_strategy_class(module_path, class_name)

        # Start server
        print_colored(f"Starting server on port {args.port}...", Colors.OKCYAN)
        if args.broker:
            print_colored(f"Connecting to broker at {args.broker}", Colors.OKCYAN)
        else:
            print_colored("No broker specified - using mock broker for development", Colors.WARNING)
        serve(
            strategy_class=strategy_class,
            port=args.port,
            broker_address=args.broker,
        )
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully without showing traceback
        print_colored("\nShutdown complete", Colors.OKGREEN)
        return 0
    except Exception as e:
        print_colored(f"Error: {e}", Colors.FAIL)
        import traceback

        traceback.print_exc()
        return 1

    return 0


def serve(strategy_class: Type[TektiiStrategy], port: int = 50051, broker_address: Optional[str] = None) -> None:
    """Run the gRPC server for the strategy.

    This function starts a gRPC server that listens for events from the
    trading engine and routes them to the strategy.

    Args:
        strategy_class: The strategy class to instantiate
        port: The port to listen on (default: 50051)
        broker_address: Optional address of the broker service (e.g., "localhost:50052")
    """
    # Create strategy instance with broker address if provided
    # The strategy will handle connection retry with exponential backoff
    if broker_address is not None:
        logger.info(f"Creating strategy with broker address: {broker_address}")
        strategy = strategy_class(broker_address=broker_address)
    else:
        logger.info("No broker address provided - using mock broker for development")
        strategy = strategy_class()
        # Inject mock broker to allow strategy to make broker calls during development
        if strategy.stub is None:
            strategy.stub = MockBrokerStub()
            strategy.broker_address = "mock://development"
            logger.info("Mock broker injected for development mode")

    # Create server instance
    strategy_service = TektiiStrategyServer(strategy)

    # Create and start server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TektiiStrategyServiceServicer_to_server(strategy_service, server)  # type: ignore[no-untyped-call]

    # Add health check service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

    # Start server
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    logger.info(f"Strategy server started on port {port}")
    if broker_address:
        logger.info(f"Broker address configured: {broker_address}")
        logger.info("Waiting for Initialize call to establish broker connection...")
    else:
        logger.info("Running with mock broker - perfect for development and testing!")
        logger.info("To connect to a real broker, use: tektii serve <module> --broker <address>")

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig: int, frame: Any) -> None:
        print_colored("\nReceived interrupt signal, shutting down gracefully...", Colors.WARNING)
        logger.info("Shutting down server with 5 second grace period")
        server.stop(grace=5)  # 5 second grace period

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep the server running
    print_colored("Server is running. Press Ctrl+C to stop.", Colors.OKGREEN)
    logger.info("Server is running and waiting for connections")
    server.wait_for_termination()
    print_colored("Server stopped successfully", Colors.OKGREEN)
    logger.info("Server shutdown complete")
