"""Tektii SDK - Build trading strategies that run anywhere.

The Tektii SDK provides a comprehensive framework for building algorithmic
trading strategies with a dual-service architecture that cleanly separates
broker operations from strategy logic. Features protocol-based proto conversions,
enhanced type safety, and financial-grade decimal precision.

Example:
    ```python
    from decimal import Decimal
    from tektii import TektiiStrategy
    from tektii.models.strategy.events import TickData, CandleData
    from tektii.models.broker.handlers import PlaceOrderRequest
    from tektii.models.strategy.types import MarketOrder, OrderSide

    class MyStrategy(TektiiStrategy):
        def on_market_data(self, tick_data: TickData = None, candle_data: CandleData = None):
            if tick_data and tick_data.last > Decimal("100"):
                order = MarketOrder(
                    symbol=tick_data.symbol,
                    side=OrderSide.BUY,
                    quantity=Decimal("10")
                )
                request = PlaceOrderRequest(order=order)
                response = self.place_order(request)
    ```
"""

__author__ = "Tektii"
__email__ = "support@tektii.com"

# Re-export key model types for convenience
from tektii.models.base import ProtoConvertible, ProtoEnum
from tektii.strategy import TektiiStrategy

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__email__",
    # Core classes
    "TektiiStrategy",
    # Base protocols and types
    "ProtoConvertible",
    "ProtoEnum",
]
