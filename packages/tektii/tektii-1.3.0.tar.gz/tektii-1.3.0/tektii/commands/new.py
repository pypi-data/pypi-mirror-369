"""New command implementation for creating strategy templates."""

import os
from typing import Any


def cmd_new(args: Any) -> int:
    """Create a new strategy from template."""
    strategy_name = args.name
    force = args.force

    # Convert strategy name to PascalCase for class name
    class_name = "".join(word.capitalize() for word in strategy_name.replace("-", "_").split("_"))
    if not class_name.endswith("Strategy"):
        class_name += "Strategy"

    # Create file name
    strategy_file = f"{strategy_name}.py"

    # Check if file already exists
    if os.path.exists(strategy_file) and not force:
        print(f"Error: {strategy_file} already exists. Use --force to overwrite.")
        return 1

    # Create strategy content
    strategy_content = _get_template(class_name)

    # Write strategy file
    with open(strategy_file, "w") as f:
        f.write(strategy_content)

    print(f"✓ Created {strategy_file}")

    # Print next steps
    print("\nNext steps:")
    print(f"1. Edit {strategy_file} to implement your trading logic")
    print(f"2. Test locally: python {strategy_file}")
    print(f"3. Validate: tektii validate {strategy_file}")
    print(f"4. Deploy: tektii push {strategy_file} {class_name}")

    return 0


def _get_template(class_name: str) -> str:
    """Get the strategy template."""
    return f'''"""
{class_name} - A simple trading strategy.

This strategy demonstrates the basic structure of a Tektii strategy.
Modify this template to implement your trading logic.
"""

from typing import Dict, List

from tektii.strategy import TektiiStrategy
from tektii.models.strategy.events import (
    AccountUpdateEvent,
    CandleData,
    OptionGreeks,
    OrderUpdateEvent,
    PositionUpdateEvent,
    SystemUpdate,
    TickData,
    TradeUpdate,
)


class {class_name}(TektiiStrategy):
    """A simple trading strategy."""

    def __init__(self) -> None:
        """Initialize the strategy."""
        super().__init__()
        self.tick_count = 0
        self.candle_count = 0

    def on_tick_data(self, tick_data: TickData) -> None:
        """Handle incoming tick data."""
        self.tick_count += 1
        # Add your tick data logic here
        # Example: track the latest price
        # self.last_price = tick_data.last
        pass

    def on_candle_data(self, candle_data: CandleData) -> None:
        """Handle incoming candle data."""
        self.candle_count += 1
        # Add your candle data logic here
        # Example: track the close price
        # self.last_close = candle_data.close
        pass

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order update events."""
        # Add your order update logic here
        pass

    def on_initalize(self, config: Dict[str, str], symbols: List[str]) -> None:
        """Initialize the strategy with configuration."""
        # Log initialization
        pass

    def on_shutdown(self) -> None:
        """Clean up on strategy shutdown."""
        # Log shutdown stats
        pass


if __name__ == "__main__":
    # Test the strategy locally
    strategy = {class_name}()
    print(f"Created {{strategy.__class__.__name__}} successfully!")
'''
