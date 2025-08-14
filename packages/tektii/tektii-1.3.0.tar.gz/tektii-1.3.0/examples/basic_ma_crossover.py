#!/usr/bin/env python3
"""Basic Moving Average Crossover Strategy.

This example demonstrates a simple trading strategy using the Tektii SDK.
The strategy:
1. Calculates short and long moving averages
2. Generates buy signals when short MA crosses above long MA
3. Generates sell signals when short MA crosses below long MA
4. Manages positions with proper risk management
"""

from collections import deque
from decimal import Decimal
from typing import Optional

from tektii import TektiiStrategy
from tektii.models.broker.handlers import PlaceOrderRequest
from tektii.models.broker.types.order_side import OrderSide
from tektii.models.broker.types.order_type import OrderType
from tektii.models.broker.types.time_in_force import TimeInForce
from tektii.models.strategy.events import AccountUpdateEvent, CandleData, OrderUpdateEvent


class MovingAverageCrossoverStrategy(TektiiStrategy):
    """Simple moving average crossover strategy."""

    def __init__(self) -> None:
        """Initialize the moving average crossover strategy."""
        super().__init__()

        # Strategy parameters
        self.short_period = 20
        self.long_period = 50
        self.position_size = Decimal("100")  # Number of shares per trade

        # Price history for moving average calculation
        self.price_history: deque[Decimal] = deque(maxlen=self.long_period)

        # Track current position
        self.has_position = False
        self.position_side: Optional[OrderSide] = None

        # Track moving averages
        self.short_ma: Optional[Decimal] = None
        self.long_ma: Optional[Decimal] = None
        self.prev_short_ma: Optional[Decimal] = None
        self.prev_long_ma: Optional[Decimal] = None

    def on_initalize(self, config: dict[str, str], symbols: list[str]) -> None:
        """Initialize strategy when connected to broker."""
        self.logger.info("Moving Average Crossover Strategy initialized")
        self.logger.info(f"Parameters: short_period={self.short_period}, long_period={self.long_period}")
        if symbols:
            self.logger.info(f"Trading symbols: {', '.join(symbols)}")

    def on_candle_data(self, candle_data: CandleData) -> None:
        """Process incoming candle data."""
        # Extract close price from the candle data
        if candle_data:
            price = candle_data.close
            self.price_history.append(price)

            # Only start trading when we have enough data
            if len(self.price_history) < self.long_period:
                return

            # Calculate moving averages
            self._calculate_moving_averages()

            # Check for trading signals
            self._check_signals(candle_data.symbol, price)

    def _calculate_moving_averages(self) -> None:
        """Calculate short and long moving averages."""
        # Store previous values
        self.prev_short_ma = self.short_ma
        self.prev_long_ma = self.long_ma

        # Calculate new moving averages
        prices_list = list(self.price_history)

        # Short MA (last N prices)
        short_prices = prices_list[-self.short_period :]
        self.short_ma = sum(short_prices) / Decimal(str(self.short_period))

        # Long MA (all prices in history)
        self.long_ma = sum(prices_list) / Decimal(str(self.long_period))

    def _check_signals(self, symbol: str, current_price: Decimal) -> None:
        """Check for crossover signals and execute trades."""
        # Check all MAs are available
        if self.short_ma is None or self.long_ma is None or self.prev_short_ma is None or self.prev_long_ma is None:
            return

        # Detect golden cross (short MA crosses above long MA)
        golden_cross = self.prev_short_ma <= self.prev_long_ma and self.short_ma > self.long_ma

        # Detect death cross (short MA crosses below long MA)
        death_cross = self.prev_short_ma >= self.prev_long_ma and self.short_ma < self.long_ma

        # Execute trades based on signals
        if golden_cross and not self.has_position:
            self._enter_long_position(symbol, current_price)
        elif death_cross and self.has_position and self.position_side == OrderSide.BUY:
            self._exit_position(symbol, current_price)
        elif death_cross and not self.has_position:
            self._enter_short_position(symbol, current_price)
        elif golden_cross and self.has_position and self.position_side == OrderSide.SELL:
            self._exit_position(symbol, current_price)

    def _enter_long_position(self, symbol: str, price: Decimal) -> None:
        """Enter a long position."""
        self.logger.info(f"Golden Cross detected! Entering long position at {price}")

        # Create a market buy order request
        order_request = PlaceOrderRequest(
            symbol=symbol, side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=self.position_size, time_in_force=TimeInForce.DAY
        )

        # Place the order
        try:
            response = self.place_order(order_request)
            if response and hasattr(response, "order_id"):
                self.has_position = True
                self.position_side = OrderSide.BUY
                self.logger.info(f"Buy order placed: {response.order_id}")
            else:
                self.logger.error("Failed to place buy order: No order ID returned")
        except Exception as e:
            self.logger.error(f"Failed to place buy order: {str(e)}")

    def _enter_short_position(self, symbol: str, price: Decimal) -> None:
        """Enter a short position."""
        self.logger.info(f"Death Cross detected! Entering short position at {price}")

        # Create a market sell order request
        order_request = PlaceOrderRequest(
            symbol=symbol, side=OrderSide.SELL, order_type=OrderType.MARKET, quantity=self.position_size, time_in_force=TimeInForce.DAY
        )

        # Place the order
        try:
            response = self.place_order(order_request)
            if response and hasattr(response, "order_id"):
                self.has_position = True
                self.position_side = OrderSide.SELL
                self.logger.info(f"Sell order placed: {response.order_id}")
            else:
                self.logger.error("Failed to place sell order: No order ID returned")
        except Exception as e:
            self.logger.error(f"Failed to place sell order: {str(e)}")

    def _exit_position(self, symbol: str, price: Decimal) -> None:
        """Exit current position."""
        if self.position_side is None:
            self.logger.warning("Cannot exit position: no position side tracked")
            return

        exit_side = OrderSide.SELL if self.position_side == OrderSide.BUY else OrderSide.BUY
        self.logger.info(f"Exiting {self.position_side.name} position at {price}")

        # Create a market order request to close position
        order_request = PlaceOrderRequest(
            symbol=symbol, side=exit_side, order_type=OrderType.MARKET, quantity=self.position_size, time_in_force=TimeInForce.DAY
        )

        # Place the order
        try:
            response = self.place_order(order_request)
            if response and hasattr(response, "order_id"):
                self.has_position = False
                self.position_side = None
                self.logger.info(f"Exit order placed: {response.order_id}")
            else:
                self.logger.error("Failed to place exit order: No order ID returned")
        except Exception as e:
            self.logger.error(f"Failed to place exit order: {str(e)}")

    def on_order_update(self, event: OrderUpdateEvent) -> None:
        """Handle order status updates."""
        self.logger.info(f"Order {event.order_id} status: {event.status.name}")

        # Log fills
        if event.filled_quantity and event.filled_quantity > 0:
            self.logger.info(f"Order {event.order_id} filled: " f"{event.filled_quantity} @ {event.avg_fill_price}")

    def on_account_update(self, event: AccountUpdateEvent) -> None:
        """Handle account updates."""
        self.logger.info(f"Account Update - " f"Balance: {event.cash_balance}, " f"Buying Power: {event.buying_power}")

    def on_shutdown(self) -> None:
        """Clean up when strategy is shutting down."""
        self.logger.info("Strategy shutting down")

        # Close any open positions
        if self.has_position:
            self.logger.warning("Closing open position on shutdown")
            # In a real scenario, you'd close the position here


if __name__ == "__main__":
    # This allows the strategy to be run directly
    # To run this strategy, use the tektii CLI:
    # tektii serve examples.basic_ma_crossover:MovingAverageCrossoverStrategy
    pass
