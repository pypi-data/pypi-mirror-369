"""Strategy validation module for pre-upload checks."""

import importlib.util
import inspect
import logging
import os
import statistics
import sys
import time
import traceback
import tracemalloc
from collections.abc import Generator
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from types import ModuleType
from typing import Any, Callable, Final, Optional, Type

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from tektii.models.broker.handlers import PlaceOrderRequest
from tektii.models.broker.types.order_side import OrderSide as BrokerOrderSide
from tektii.models.broker.types.order_type import OrderType as BrokerOrderType
from tektii.models.broker.types.time_in_force import TimeInForce as BrokerTimeInForce
from tektii.models.strategy.events import CandleData, CandleType
from tektii.strategy import TektiiStrategy
from tektii.testing import MockBrokerStub

from ..utils.loader import load_strategy_class

logger = logging.getLogger(__name__)
console = Console()

# Constants for better readability and maintenance
DEFAULT_TEST_SYMBOL: Final[str] = "AAPL"
DEFAULT_TEST_PRICE: Final[Decimal] = Decimal("150.0")
DEFAULT_TEST_QUANTITY: Final[Decimal] = Decimal("100")


@contextmanager
def suppress_strategy_logs(strategy: TektiiStrategy) -> Generator[None, None, None]:
    """Temporarily suppress error logs from strategy during validation."""
    # Get the strategy's logger
    strategy_logger = logging.getLogger(strategy.__class__.__module__)
    original_level = strategy_logger.level

    # Also suppress the base strategy logger
    base_logger = logging.getLogger("tektii.strategy")
    base_original_level = base_logger.level

    try:
        # Set to CRITICAL to only show critical errors
        strategy_logger.setLevel(logging.CRITICAL)
        base_logger.setLevel(logging.CRITICAL)
        yield
    finally:
        # Restore original levels
        strategy_logger.setLevel(original_level)
        base_logger.setLevel(base_original_level)


@dataclass
class ValidationConfig:
    """Configuration for validation thresholds with type safety."""

    # Performance thresholds (tiered for different strategy types)
    min_throughput_eps: int = 50  # Retail strategies
    recommended_throughput_eps: int = 500  # Professional strategies
    hft_throughput_eps: int = 10000  # High-frequency strategies
    max_p99_latency_us: int = 5000
    max_latency_spike_us: int = 50000

    # Memory thresholds
    max_memory_growth_mb: float = 50.0
    warning_memory_growth_mb: float = 20.0
    max_peak_memory_mb: float = 200.0

    # Risk management thresholds
    max_position_size_pct: float = 5.0  # Max position as % of daily volume
    max_portfolio_exposure_pct: float = 200.0  # Max leverage
    max_single_asset_concentration_pct: float = 20.0  # Max concentration in one asset
    max_price_deviation_pct: float = 10.0  # Max price deviation from market
    max_orders_per_minute: int = 100  # Fat finger protection
    max_daily_trades: int = 1000  # Pattern day trader threshold

    # Data quality thresholds
    min_data_completeness_pct: float = 95.0  # Minimum data completeness
    max_stale_data_seconds: int = 300  # 5 minutes

    # Test parameters
    num_warmup_events: int = 100
    num_perf_test_events: int = 1000
    num_memory_test_events: int = 5000


class ValidationStatus(Enum):
    """Status of a validation check."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationCheck:
    """Individual validation check result with comprehensive details."""

    name: str
    status: ValidationStatus
    message: str
    details: Optional[str] = None
    duration_ms: Optional[float] = None
    educational_tip: Optional[str] = None  # Educational guidance

    @property
    def icon(self) -> str:
        """Get status icon."""
        return {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.SKIPPED: "⏭️",
        }[self.status]

    @property
    def color(self) -> str:
        """Get status color for rich."""
        return {
            ValidationStatus.PASSED: "green",
            ValidationStatus.FAILED: "red",
            ValidationStatus.WARNING: "yellow",
            ValidationStatus.SKIPPED: "dim",
        }[self.status]


@dataclass
class ValidationCategory:
    """Category of validation checks with computed properties."""

    name: str
    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return sum(1 for c in self.checks if c.status == ValidationStatus.PASSED)

    @property
    def failed_count(self) -> int:
        """Count of failed checks."""
        return sum(1 for c in self.checks if c.status == ValidationStatus.FAILED)

    @property
    def warning_count(self) -> int:
        """Count of warning checks."""
        return sum(1 for c in self.checks if c.status == ValidationStatus.WARNING)

    @property
    def overall_status(self) -> ValidationStatus:
        """Determine overall status based on check results."""
        if self.failed_count > 0:
            return ValidationStatus.FAILED
        elif self.warning_count > 0:
            return ValidationStatus.WARNING
        elif self.passed_count > 0:
            return ValidationStatus.PASSED
        return ValidationStatus.SKIPPED


@dataclass
class ValidationResult:
    """Result of strategy validation with enhanced metrics."""

    is_valid: bool
    categories: list[ValidationCategory] = field(default_factory=list)
    performance_metrics: Optional[dict[str, Any]] = None
    memory_metrics: Optional[dict[str, Any]] = None
    strategy_info: dict[str, Any] = field(default_factory=dict)
    risk_score: Optional[str] = None  # Overall risk assessment
    readiness_score: Optional[int] = None  # Production readiness (0-100)

    def get_category(self, name: str) -> ValidationCategory:
        """Get or create a validation category."""
        for cat in self.categories:
            if cat.name == name:
                return cat
        cat = ValidationCategory(name=name)
        self.categories.append(cat)
        return cat

    def add_check(self, category: str, check: ValidationCheck) -> None:
        """Add a check to a category."""
        cat = self.get_category(category)
        cat.checks.append(check)
        if check.status == ValidationStatus.FAILED:
            self.is_valid = False

    @property
    def total_checks(self) -> int:
        """Total number of checks across all categories."""
        return sum(len(cat.checks) for cat in self.categories)

    @property
    def passed_checks(self) -> int:
        """Total number of passed checks."""
        return sum(cat.passed_count for cat in self.categories)

    @property
    def failed_checks(self) -> int:
        """Total number of failed checks."""
        return sum(cat.failed_count for cat in self.categories)

    @property
    def warning_checks(self) -> int:
        """Total number of warning checks."""
        return sum(cat.warning_count for cat in self.categories)

    def display(self) -> None:
        """Display validation results with rich formatting."""
        self._display_summary()
        self._display_categories()
        self._display_metrics()

    def _display_summary(self) -> None:
        """Display overall summary with metrics."""
        if self.is_valid:
            summary_text = "[bold green]✅ Strategy Validation PASSED[/bold green]\n"
            summary_text += f"[dim]{self.passed_checks}/{self.total_checks} checks passed[/dim]"
            if self.readiness_score:
                summary_text += f"\n[cyan]Production Readiness: {self.readiness_score}/100[/cyan]"
            if self.risk_score:
                summary_text += f"\n[yellow]Risk Level: {self.risk_score}[/yellow]"

            console.print(Panel.fit(summary_text, border_style="green"))
        else:
            summary_text = "[bold red]❌ Strategy Validation FAILED[/bold red]\n"
            summary_text += f"[dim]{self.failed_checks} failed, {self.warning_checks} warnings, {self.passed_checks} passed[/dim]"

            console.print(Panel.fit(summary_text, border_style="red"))

    def _display_categories(self) -> None:
        """Display all validation categories."""
        for cat in self.categories:
            self._display_category(cat)

    def _display_metrics(self) -> None:
        """Display performance and memory metrics."""
        if self.performance_metrics:
            self._display_performance_metrics()
        if self.memory_metrics:
            self._display_memory_metrics()
        if self.strategy_info:
            self._display_strategy_info()

    def _display_category(self, cat: ValidationCategory) -> None:
        """Display a category of checks."""
        # Map status to colors
        status_color = {"failed": "red", "warning": "yellow", "passed": "green"}.get(cat.overall_status.name.lower(), "dim")

        tree = Tree(f"[bold {status_color}]{cat.name}[/bold {status_color}]")

        for check in cat.checks:
            node_text = f"{check.icon} {check.message}"
            if check.duration_ms:
                node_text += f" [dim]({check.duration_ms:.1f}ms)[/dim]"

            if check.details or check.educational_tip:
                check_node = tree.add(f"[{check.color}]{node_text}[/{check.color}]")

                if check.details:
                    for line in check.details.split("\n"):
                        if line.strip():
                            check_node.add(f"[dim]{line}[/dim]")

                # Add educational tips
                if check.educational_tip:
                    check_node.add(f"[cyan]💡 Tip: {check.educational_tip}[/cyan]")
            else:
                tree.add(f"[{check.color}]{node_text}[/{check.color}]")

        console.print(tree)
        console.print()

    def _display_performance_metrics(self) -> None:
        """Display performance metrics table."""
        table = Table(title="Event Processor Performance Metrics", box=box.ROUNDED)
        table.add_column("Event Processor", style="cyan", width=20)
        table.add_column("Status/Metrics", style="white")

        if self.performance_metrics:
            for metric, value in self.performance_metrics.items():
                if metric == "_header":
                    continue  # Skip the header

                # Style based on whether it's implemented or not
                if "Not implemented" in str(value):
                    table.add_row(metric, f"[dim]{value}[/dim]")
                elif "(throughput)" in metric:
                    # Throughput rows in green
                    table.add_row(metric, f"[green]{value}[/green]")
                else:
                    # Regular metrics
                    table.add_row(metric, str(value))

        console.print(table)
        console.print()

    def _display_memory_metrics(self) -> None:
        """Display memory metrics table."""
        table = Table(title="Memory Metrics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        if self.memory_metrics:
            for metric, value in self.memory_metrics.items():
                table.add_row(metric.replace("_", " ").title(), str(value))

        console.print(table)
        console.print()

    def _display_strategy_info(self) -> None:
        """Display strategy information."""
        table = Table(title="Strategy Information", box=box.ROUNDED, show_header=False)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        for key, value in self.strategy_info.items():
            if key not in ["performance_metrics", "memory_metrics"]:
                display_key = key.replace("_", " ").title()
                table.add_row(display_key, str(value))

        console.print(table)
        console.print()


class MockBrokerValidator:
    """Mock broker that validates order formats during validation."""

    def __init__(self) -> None:
        """Initialize mock broker validator."""
        self.orders_validated = 0
        self.validated_orders: list[dict[str, Any]] = []

    def validate_order(self, request: PlaceOrderRequest) -> dict[str, Any]:
        """Validate order format and track results."""
        self.orders_validated += 1
        errors: list[str] = []
        warnings: list[str] = []

        # Validate required fields
        if not request.symbol:
            errors.append("Order missing symbol")

        if not request.quantity or request.quantity <= Decimal(0):
            errors.append(f"Invalid order quantity: {request.quantity}")

        # Fat finger protection - check for extremely large quantities
        if request.quantity and request.quantity > Decimal("100000"):
            warnings.append(f"Very large order quantity: {request.quantity} - potential fat finger trade")

        # Check order type is valid
        if not request.order_type:
            errors.append("Order missing type")

        # Check order side is valid
        if not request.side:
            errors.append("Order missing side")

        # For limit orders, validate price
        if request.order_type == BrokerOrderType.LIMIT:
            if not request.limit_price or request.limit_price <= Decimal(0):
                errors.append("LIMIT order requires positive limit price")

            # Fat finger protection - check for unrealistic prices
            if request.limit_price and request.limit_price > Decimal("10000"):
                warnings.append(f"Very high limit price: {request.limit_price} - verify this is intentional")

        # For stop orders, validate stop price
        if request.order_type in [BrokerOrderType.STOP, BrokerOrderType.STOP_LIMIT] and (not request.stop_price or request.stop_price <= Decimal(0)):
            errors.append(f"{request.order_type.name} order requires positive stop price")

        # For stop-limit, need both prices
        if request.order_type == BrokerOrderType.STOP_LIMIT and (not request.limit_price or request.limit_price <= Decimal(0)):
            errors.append("STOP_LIMIT order requires positive limit price")

        if not errors:
            # Track successful validation
            self.validated_orders.append(
                {
                    "symbol": request.symbol,
                    "side": request.side.name,
                    "quantity": float(request.quantity),
                    "type": request.order_type.name,
                    "limit_price": float(request.limit_price) if request.limit_price else None,
                    "stop_price": float(request.stop_price) if request.stop_price else None,
                }
            )
            # For mock validation, just return a simple response
            return {"valid": True, "errors": [], "warnings": warnings}
        else:
            # Return validation errors
            return {"valid": False, "errors": errors, "warnings": warnings}


class StrategyValidator:
    """Comprehensive validator for trading strategies with enhanced type safety."""

    def __init__(self, strategy_class: Type[TektiiStrategy], config: Optional[ValidationConfig] = None) -> None:
        """Initialize validator.

        Args:
            strategy_class: Strategy class to validate
            config: Optional validation configuration
        """
        if not issubclass(strategy_class, TektiiStrategy):
            raise TypeError(f"Expected TektiiStrategy subclass, got {strategy_class}")

        self.strategy_class = strategy_class
        self.result = ValidationResult(is_valid=True)
        self.mock_broker = MockBrokerValidator()
        self.config = config or ValidationConfig()

    def validate(self, comprehensive: bool = True) -> ValidationResult:
        """Run all validation checks.

        Args:
            comprehensive: Whether to run comprehensive tests (performance, edge cases)

        Returns:
            Validation result
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True,
        ) as progress:
            self._run_core_validation(progress)

            strategy_instance = self._get_strategy_instance()
            if strategy_instance:
                self._run_functional_validation(progress, strategy_instance)
                if comprehensive:
                    self._run_comprehensive_validation(progress, strategy_instance)

        # Calculate overall scores
        self._calculate_scores()
        return self.result

    def _run_core_validation(self, progress: Progress) -> None:
        """Run core validation checks."""
        core_task = progress.add_task("[cyan]Running core validation...", total=6)

        self._check_inheritance()
        progress.update(core_task, advance=1)

        self._check_required_methods()
        progress.update(core_task, advance=1)

        strategy_instance = self._check_instantiation()
        progress.update(core_task, advance=1)

        if strategy_instance:
            self._collect_strategy_info(strategy_instance)
            progress.update(core_task, advance=1)

            self._check_initialization(strategy_instance)
            progress.update(core_task, advance=1)

            self._check_risk_management(strategy_instance)
            progress.update(core_task, advance=1)

    def _run_functional_validation(self, progress: Progress, strategy: TektiiStrategy) -> None:
        """Run functional validation checks."""
        func_task = progress.add_task("[cyan]Testing functionality...", total=4)

        self._check_market_data_handling(strategy)
        progress.update(func_task, advance=1)

        self._check_order_capabilities(strategy)
        progress.update(func_task, advance=1)

        self._check_error_handling(strategy)
        progress.update(func_task, advance=1)

        self._check_data_quality_handling(strategy)
        progress.update(func_task, advance=1)

    def _run_comprehensive_validation(self, progress: Progress, strategy: TektiiStrategy) -> None:
        """Run comprehensive validation checks."""
        perf_task = progress.add_task("[cyan]Running comprehensive tests...", total=4)

        self._check_edge_cases(strategy)
        progress.update(perf_task, advance=1)

        self._check_performance(strategy)
        progress.update(perf_task, advance=1)

        self._check_memory_leaks(strategy)
        progress.update(perf_task, advance=1)

        self._check_trading_patterns(strategy)
        progress.update(perf_task, advance=1)

    def _get_strategy_instance(self) -> Optional[TektiiStrategy]:
        """Get a validated strategy instance."""
        try:
            strategy = self.strategy_class()
            if strategy.stub is None:
                strategy.stub = MockBrokerStub()
                strategy.broker_address = "mock://validation"
            return strategy
        except Exception:
            return None

    def _check_risk_management(self, strategy: TektiiStrategy) -> None:
        """Check risk management capabilities and practices."""
        start_time = time.perf_counter()

        # Define risk indicators to look for
        risk_indicators = {
            "position_sizing": ["position_size", "max_position", "position_limit"],
            "stop_losses": ["stop_loss", "max_loss", "risk_per_trade"],
            "portfolio_limits": ["max_exposure", "concentration_limit", "leverage_limit"],
            "risk_metrics": ["var", "drawdown", "sharpe", "volatility"],
        }

        found_indicators: dict[str, list[str]] = {}
        missing_areas: list[str] = []

        for category, indicators in risk_indicators.items():
            found: list[str] = []
            for indicator in indicators:
                # Check attributes
                if hasattr(strategy, indicator):
                    found.append(f"attribute: {indicator}")

                # Check in source code
                try:
                    source = inspect.getsource(strategy.__class__)
                    if indicator in source.lower():
                        found.append(f"code: {indicator}")
                except Exception:
                    pass

            if found:
                found_indicators[category] = found
            else:
                missing_areas.append(category)

        # Assess risk management quality
        if len(found_indicators) >= 3:
            status = ValidationStatus.PASSED
            message = f"Good risk management: {len(found_indicators)}/4 areas covered"
            tip = "Consider documenting your risk management approach in strategy docstring"
        elif len(found_indicators) >= 1:
            status = ValidationStatus.WARNING
            message = f"Basic risk management: {len(found_indicators)}/4 areas covered"
            tip = f"Consider adding: {', '.join(missing_areas[:2])}"
        else:
            status = ValidationStatus.WARNING
            message = "No explicit risk management detected"
            tip = "Add position sizing, stop losses, and portfolio limits for safer trading"

        details = None
        if found_indicators:
            details = "\n".join([f"{cat}: {', '.join(items)}" for cat, items in found_indicators.items()])

        self.result.add_check(
            "Risk Management",
            ValidationCheck(
                name="Risk Controls",
                status=status,
                message=message,
                details=details,
                educational_tip=tip,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _check_data_quality_handling(self, strategy: TektiiStrategy) -> None:
        """Check how strategy handles data quality issues."""
        start_time = time.perf_counter()

        data_quality_tests = [
            ("Stale Data", self._test_stale_data_handling),
            ("Missing Fields", self._test_missing_fields),
            ("Market Gaps", self._test_market_gaps),
            ("Invalid Timestamps", self._test_invalid_timestamps),
        ]

        passed_tests = 0
        failed_details: list[str] = []

        for test_name, test_func in data_quality_tests:
            try:
                test_func(strategy)
                passed_tests += 1
            except Exception as e:
                failed_details.append(f"{test_name}: {str(e)[:50]}")

        if passed_tests == len(data_quality_tests):
            status = ValidationStatus.PASSED
            message = "Handles all data quality scenarios"
            tip = "Excellent data validation - your strategy should be robust in production"
        elif passed_tests >= len(data_quality_tests) // 2:
            status = ValidationStatus.WARNING
            message = f"Handles {passed_tests}/{len(data_quality_tests)} data quality scenarios"
            tip = "Consider adding validation for missing or stale market data"
        else:
            status = ValidationStatus.WARNING
            message = "Limited data quality handling"
            tip = "Add input validation to handle market data gaps and anomalies"

        self.result.add_check(
            "Data Quality",
            ValidationCheck(
                name="Data Validation",
                status=status,
                message=message,
                details="\n".join(failed_details) if failed_details else None,
                educational_tip=tip,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _check_trading_patterns(self, strategy: TektiiStrategy) -> None:
        """Analyze trading patterns for potential issues."""
        start_time = time.perf_counter()

        pattern_issues: list[str] = []

        # Simulate rapid trading to check for excessive frequency
        if hasattr(strategy, "on_candle_data"):
            order_count = self._analyze_trading_frequency(strategy)

            # Check for excessive trading
            if order_count > 50:  # More than 50% of ticks generate orders
                pattern_issues.append(f"Very high trading frequency: {order_count} orders per 100 ticks")
            elif order_count > 20:
                pattern_issues.append(f"High trading frequency: {order_count} orders per 100 ticks (consider PDT rules)")

        # Check for potential wash trading patterns
        self._check_wash_trading_patterns(pattern_issues)

        # Determine status based on issues found
        status, message, tip = self._assess_trading_patterns(pattern_issues)

        self.result.add_check(
            "Trading Patterns",
            ValidationCheck(
                name="Pattern Analysis",
                status=status,
                message=message,
                details="\n".join(pattern_issues) if pattern_issues else None,
                educational_tip=tip,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _analyze_trading_frequency(self, strategy: TektiiStrategy) -> int:
        """Analyze trading frequency during rapid market updates."""
        order_count = 0

        # Suppress logs during pattern testing
        with suppress_strategy_logs(strategy):
            for i in range(200):  # Simulate 200 candles in quick succession
                candle_data = self._create_test_candle(i)

                initial_orders = self.mock_broker.orders_validated
                with suppress(Exception):
                    strategy.on_candle_data(candle_data)

                new_orders = self.mock_broker.orders_validated - initial_orders
                order_count += new_orders

        return order_count

    def _create_test_candle(self, index: int) -> CandleData:
        """Create a test candle with varying prices."""
        price_adjustment = Decimal("0.01") * (index % 10)
        base_price = DEFAULT_TEST_PRICE + price_adjustment
        return CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=base_price,
            high=base_price + Decimal("0.2"),
            low=base_price - Decimal("0.1"),
            close=base_price + Decimal("0.05"),
            volume=1000,
            candle_type=CandleType.TIME,
        )

    def _check_wash_trading_patterns(self, pattern_issues: list[str]) -> None:
        """Check for potential wash trading patterns."""
        validated_orders = self.mock_broker.validated_orders
        if len(validated_orders) >= 2:
            buy_orders = [o for o in validated_orders if o["side"] == "BUY"]
            sell_orders = [o for o in validated_orders if o["side"] == "SELL"]

            # Simple wash trading check - immediate offsetting orders
            if len(buy_orders) > 0 and len(sell_orders) > 0:
                for buy in buy_orders:
                    for sell in sell_orders:
                        if buy["symbol"] == sell["symbol"] and buy["quantity"] == sell["quantity"]:
                            pattern_issues.append("Potential wash trading: identical offsetting orders detected")
                            return

    def _assess_trading_patterns(self, pattern_issues: list[str]) -> tuple[ValidationStatus, str, str]:
        """Assess trading patterns and return status, message, and tip."""
        if not pattern_issues:
            return (
                ValidationStatus.PASSED,
                "No concerning trading patterns detected",
                "Trading patterns appear reasonable for regulatory compliance",
            )
        elif len(pattern_issues) == 1 and "High trading frequency" in pattern_issues[0]:
            return (ValidationStatus.WARNING, "Moderate trading frequency detected", "Monitor pattern day trader rules if trading frequently")
        else:
            return (
                ValidationStatus.WARNING,
                f"Found {len(pattern_issues)} potential pattern issue(s)",
                "Review trading patterns for regulatory compliance",
            )

    def _test_stale_data_handling(self, strategy: TektiiStrategy) -> None:
        """Test handling of stale market data."""
        if not hasattr(strategy, "on_candle_data"):
            return

        old_candle = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=DEFAULT_TEST_PRICE,
            high=DEFAULT_TEST_PRICE + Decimal("0.1"),
            low=DEFAULT_TEST_PRICE - Decimal("0.1"),
            close=DEFAULT_TEST_PRICE + Decimal("0.05"),
            volume=1000,
            candle_type=CandleType.TIME,
        )

        # Send same candle multiple times to simulate stale data
        for _ in range(10):
            strategy.on_candle_data(old_candle)

    def _test_missing_fields(self, strategy: TektiiStrategy) -> None:
        """Test with market data missing optional fields."""
        if not hasattr(strategy, "on_candle_data"):
            return

        minimal_candle = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=DEFAULT_TEST_PRICE,
            high=DEFAULT_TEST_PRICE,
            low=DEFAULT_TEST_PRICE,
            close=DEFAULT_TEST_PRICE,
            volume=0,
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(minimal_candle)

    def _test_market_gaps(self, strategy: TektiiStrategy) -> None:
        """Test handling of price gaps."""
        if not hasattr(strategy, "on_candle_data"):
            return

        # Normal price
        candle1 = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=Decimal("100.0"),
            high=Decimal("100.2"),
            low=Decimal("99.8"),
            close=Decimal("100.05"),
            volume=1000,
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(candle1)

        # Large gap up (20% jump)
        candle2 = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=Decimal("120.0"),
            high=Decimal("120.5"),
            low=Decimal("119.5"),
            close=Decimal("120.05"),
            volume=2000,
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(candle2)

    def _test_invalid_timestamps(self, strategy: TektiiStrategy) -> None:
        """Test with invalid or out-of-order timestamps."""
        if not hasattr(strategy, "on_candle_data"):
            return

        candle = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=DEFAULT_TEST_PRICE,
            high=DEFAULT_TEST_PRICE + Decimal("1.0"),
            low=DEFAULT_TEST_PRICE - Decimal("0.5"),
            close=DEFAULT_TEST_PRICE + Decimal("0.75"),
            volume=1000000,
            candle_size=1,
            candle_size_unit="min",
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(candle)

    def _calculate_scores(self) -> None:
        """Calculate overall readiness and risk scores."""
        total_checks = self.result.total_checks
        if total_checks == 0:
            return

        # Calculate readiness score (0-100)
        passed_weight = 3
        warning_weight = 1

        score = ((self.result.passed_checks * passed_weight + self.result.warning_checks * warning_weight) * 100) // (total_checks * passed_weight)

        self.result.readiness_score = min(100, max(0, int(score)))

        # Calculate risk assessment
        risk_category = self.result.get_category("Risk Management")
        pattern_category = self.result.get_category("Trading Patterns")

        risk_issues = risk_category.failed_count + risk_category.warning_count + pattern_category.failed_count + pattern_category.warning_count

        if risk_issues == 0:
            self.result.risk_score = "Conservative"
        elif risk_issues <= 2:
            self.result.risk_score = "Moderate"
        else:
            self.result.risk_score = "Aggressive"

    def _check_inheritance(self) -> None:
        """Check that the class properly inherits from TektiiStrategy."""
        start_time = time.perf_counter()

        # Check if it directly inherits or through intermediate classes
        mro = self.strategy_class.__mro__
        if TektiiStrategy not in mro:
            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="Inheritance",
                    status=ValidationStatus.FAILED,
                    message="TektiiStrategy not in method resolution order",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )
            return

        details = None
        status = ValidationStatus.PASSED
        tip = None

        # Check for common inheritance issues
        if len(mro) > 4:  # strategy_class -> ... -> TektiiStrategy -> ABC -> object
            status = ValidationStatus.WARNING
            details = f"Deep inheritance hierarchy ({len(mro)} levels) may impact performance"
            tip = "Consider flattening inheritance hierarchy for better performance"

        self.result.add_check(
            "Structure",
            ValidationCheck(
                name="Inheritance",
                status=status,
                message="Correctly inherits from TektiiStrategy",
                details=details,
                educational_tip=tip,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _check_required_methods(self) -> None:
        """Check that required methods are implemented."""
        start_time = time.perf_counter()

        # Check for required data handlers - at least one should be implemented
        data_handlers = ["on_candle_data"]
        implemented_handlers = self._get_implemented_methods(data_handlers)

        self._validate_data_handlers(implemented_handlers, start_time)

        # Check optional event handlers
        event_handlers = [
            "on_initalize",
            "on_shutdown",
            "on_order_update",
            "on_position_update",
            "on_account_update",
            "on_trade_update",
            "on_system_update",
        ]
        implemented_events = self._get_implemented_methods(event_handlers)
        self._validate_event_handlers(implemented_events, start_time)

        # Check method signatures
        self._check_method_signatures()

    def _get_implemented_methods(self, method_names: list[str]) -> list[str]:
        """Get list of implemented methods from the strategy class."""
        implemented = []
        for method_name in method_names:
            if hasattr(self.strategy_class, method_name):
                method = getattr(self.strategy_class, method_name)
                if callable(method) and method.__qualname__ != f"TektiiStrategy.{method_name}":
                    implemented.append(method_name)
        return implemented

    def _validate_data_handlers(self, implemented_handlers: list[str], start_time: float) -> None:
        """Validate data handler implementation."""
        if not implemented_handlers:
            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="Data Handlers",
                    status=ValidationStatus.WARNING,
                    message="No market data handlers implemented",
                    details="Consider implementing on_candle_data",
                    educational_tip="Market data handlers are essential for receiving price updates",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )
        else:
            tip = None
            if len(implemented_handlers) == 1:
                tip = "Consider implementing both tick and candle handlers for more flexibility"

            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="Data Handlers",
                    status=ValidationStatus.PASSED,
                    message=f"Implements: {', '.join(implemented_handlers)}",
                    educational_tip=tip,
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )

    def _validate_event_handlers(self, implemented_events: list[str], start_time: float) -> None:
        """Validate event handler implementation."""
        if implemented_events:
            tip = None
            if "on_order_update" not in implemented_events:
                tip = "Consider implementing on_order_update to track order execution"

            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="Event Handlers",
                    status=ValidationStatus.PASSED,
                    message=f"Implements {len(implemented_events)} event handlers",
                    details=", ".join(implemented_events),
                    educational_tip=tip,
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )
        else:
            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="Event Handlers",
                    status=ValidationStatus.PASSED,
                    message="Uses default event handlers",
                    educational_tip="Consider implementing on_order_update and on_account_update for better monitoring",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )

    def _check_method_signatures(self) -> None:
        """Check method signatures for common issues."""
        start_time = time.perf_counter()
        issues: list[str] = []

        # Note: on_tick_data has been removed from the SDK

        # Check on_candle_data signature
        if hasattr(self.strategy_class, "on_candle_data"):
            try:
                sig = inspect.signature(self.strategy_class.on_candle_data)
                params = list(sig.parameters.keys())
                if len(params) < 2 or "candle_data" not in params:
                    issues.append("on_candle_data should accept 'candle_data' parameter")
            except Exception as e:
                issues.append(f"Could not inspect on_candle_data: {str(e)}")

        status = ValidationStatus.WARNING if issues else ValidationStatus.PASSED
        message = f"Found {len(issues)} signature issue(s)" if issues else "All method signatures are correct"

        self.result.add_check(
            "Structure",
            ValidationCheck(
                name="Method Signatures",
                status=status,
                message=message,
                details="\n".join(issues) if issues else None,
                educational_tip="Method signatures must match the base class interface" if issues else None,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _check_instantiation(self) -> Optional[TektiiStrategy]:
        """Check that the strategy can be instantiated."""
        start_time = time.perf_counter()

        try:
            # Try to instantiate with no arguments first
            try:
                strategy = self.strategy_class()

                # Inject mock broker to prevent "No broker connection" errors
                if strategy.stub is None:
                    strategy.stub = MockBrokerStub()
                    strategy.broker_address = "mock://validation"

                self.result.add_check(
                    "Initialization",
                    ValidationCheck(
                        name="Instantiation",
                        status=ValidationStatus.PASSED,
                        message="Successfully instantiated with mock broker",
                        duration_ms=(time.perf_counter() - start_time) * 1000,
                    ),
                )
                return strategy
            except TypeError as e:
                # If that fails, try to determine what arguments are needed
                sig = inspect.signature(self.strategy_class.__init__)
                params = [
                    p
                    for p in sig.parameters.values()
                    if p.name not in ["self", "broker_address", "max_retries", "initial_backoff"] and p.default == inspect.Parameter.empty
                ]

                if params:
                    param_names = [p.name for p in params]
                    self.result.add_check(
                        "Initialization",
                        ValidationCheck(
                            name="Instantiation",
                            status=ValidationStatus.FAILED,
                            message="Strategy requires constructor parameters",
                            details=f"Required parameters: {', '.join(param_names)}\nConsider providing default values for deployment",
                            educational_tip="Strategies should instantiate without required parameters for easier deployment",
                            duration_ms=(time.perf_counter() - start_time) * 1000,
                        ),
                    )
                    return None
                else:
                    raise e

        except Exception as e:
            self.result.add_check(
                "Initialization",
                ValidationCheck(
                    name="Instantiation",
                    status=ValidationStatus.FAILED,
                    message=f"Failed to instantiate: {str(e)}",
                    details=traceback.format_exc(),
                    educational_tip="Check for missing imports or initialization errors",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )
            return None

    def _check_initialization(self, strategy: TektiiStrategy) -> None:
        """Check that the strategy can be initialized."""
        start_time = time.perf_counter()

        try:
            # Call on_initalize if it exists
            if hasattr(strategy, "on_initalize") and callable(strategy.on_initalize):
                # on_initalize requires config and symbols parameters
                strategy.on_initalize({}, [])

            self.result.add_check(
                "Initialization",
                ValidationCheck(
                    name="Strategy Initialization",
                    status=ValidationStatus.PASSED,
                    message="Strategy initialized successfully",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )

        except Exception as e:
            self.result.add_check(
                "Initialization",
                ValidationCheck(
                    name="Strategy Initialization",
                    status=ValidationStatus.FAILED,
                    message=f"Initialization failed: {str(e)}",
                    details=traceback.format_exc(),
                    educational_tip="Ensure on_initalize method handles empty config and symbol lists",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )

    def _check_market_data_handling(self, strategy: TektiiStrategy) -> None:
        """Check market data processing with both tick and candle data."""
        self._test_tick_data_handling(strategy)
        self._test_candle_data_handling(strategy)

    def _test_tick_data_handling(self, strategy: TektiiStrategy) -> None:
        """Test tick data handling."""
        tick_start = time.perf_counter()

        try:
            # Test candle data handler
            candle_data = CandleData(
                symbol=DEFAULT_TEST_SYMBOL,
                open=DEFAULT_TEST_PRICE,
                high=DEFAULT_TEST_PRICE + Decimal("0.10"),
                low=DEFAULT_TEST_PRICE - Decimal("0.05"),
                close=DEFAULT_TEST_PRICE + Decimal("0.05"),
                volume=10000,
                candle_type=CandleType.TIME,
            )

            # Test candle data handler if exists
            if hasattr(strategy, "on_candle_data") and callable(strategy.on_candle_data):
                strategy.on_candle_data(candle_data)

            self.result.add_check(
                "Market Data",
                ValidationCheck(
                    name="Tick Data Processing",
                    status=ValidationStatus.PASSED,
                    message="Processes tick data without errors",
                    duration_ms=(time.perf_counter() - tick_start) * 1000,
                ),
            )
        except Exception as e:
            self.result.add_check(
                "Market Data",
                ValidationCheck(
                    name="Tick Data Processing",
                    status=ValidationStatus.FAILED,
                    message=f"Error processing tick data: {str(e)}",
                    details=traceback.format_exc(),
                    educational_tip="Ensure tick data handlers validate inputs before processing",
                    duration_ms=(time.perf_counter() - tick_start) * 1000,
                ),
            )

    def _test_candle_data_handling(self, strategy: TektiiStrategy) -> None:
        """Test candle data handling."""
        candle_start = time.perf_counter()

        try:
            candle_data = CandleData(
                symbol=DEFAULT_TEST_SYMBOL,
                open=DEFAULT_TEST_PRICE,
                high=DEFAULT_TEST_PRICE + Decimal("1.0"),
                low=DEFAULT_TEST_PRICE - Decimal("0.5"),
                close=DEFAULT_TEST_PRICE + Decimal("0.75"),
                volume=1000000,
                candle_size=1,
                candle_size_unit="min",
                candle_type=CandleType.TIME,
                vwap=None,
                trade_count=None,
            )

            # Test candle data handler if exists
            if hasattr(strategy, "on_candle_data") and callable(strategy.on_candle_data):
                strategy.on_candle_data(candle_data)

            self.result.add_check(
                "Market Data",
                ValidationCheck(
                    name="Candle Data Processing",
                    status=ValidationStatus.PASSED,
                    message="Processes candle data without errors",
                    duration_ms=(time.perf_counter() - candle_start) * 1000,
                ),
            )
        except Exception as e:
            self.result.add_check(
                "Market Data",
                ValidationCheck(
                    name="Candle Data Processing",
                    status=ValidationStatus.FAILED,
                    message=f"Error processing candle data: {str(e)}",
                    details=traceback.format_exc(),
                    educational_tip="Ensure candle data handlers validate OHLCV data before processing",
                    duration_ms=(time.perf_counter() - candle_start) * 1000,
                ),
            )

    def _check_order_capabilities(self, strategy: TektiiStrategy) -> None:
        """Check order placement capabilities."""
        start_time = time.perf_counter()

        try:
            # Test creating and validating a sample order
            test_order = PlaceOrderRequest(
                symbol=DEFAULT_TEST_SYMBOL,
                side=BrokerOrderSide.BUY,
                quantity=DEFAULT_TEST_QUANTITY,
                order_type=BrokerOrderType.LIMIT,
                limit_price=DEFAULT_TEST_PRICE,
                time_in_force=BrokerTimeInForce.DAY,
            )

            # Validate with mock broker
            response = self.mock_broker.validate_order(test_order)

            if response.get("valid", False):
                details = self._analyze_broker_capabilities(strategy)
                tip = self._get_order_capability_tip(strategy)

                self.result.add_check(
                    "Order Management",
                    ValidationCheck(
                        name="Order Capabilities",
                        status=ValidationStatus.PASSED,
                        message="Order validation successful",
                        details=details,
                        educational_tip=tip,
                        duration_ms=(time.perf_counter() - start_time) * 1000,
                    ),
                )

                # Track validated orders
                if self.mock_broker.validated_orders:
                    self.result.strategy_info["sample_orders_validated"] = len(self.mock_broker.validated_orders)
            else:
                self.result.add_check(
                    "Order Management",
                    ValidationCheck(
                        name="Order Capabilities",
                        status=ValidationStatus.WARNING,
                        message="Order validation failed",
                        details="; ".join(response.get("errors", [])),
                        educational_tip="Review order creation logic and ensure all required fields are set",
                        duration_ms=(time.perf_counter() - start_time) * 1000,
                    ),
                )

        except Exception as e:
            self.result.add_check(
                "Order Management",
                ValidationCheck(
                    name="Order Capabilities",
                    status=ValidationStatus.WARNING,
                    message=f"Could not check order capabilities: {str(e)}",
                    educational_tip="Implement order placement methods using PlaceOrderRequest",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                ),
            )

    def _analyze_broker_capabilities(self, strategy: TektiiStrategy) -> Optional[str]:
        """Analyze available broker methods in the strategy."""
        broker_methods = ["place_order", "cancel_order", "modify_order", "get_state"]
        available_methods = [method for method in broker_methods if hasattr(strategy, method) and callable(getattr(strategy, method))]

        details_parts = []
        if available_methods:
            details_parts.append(f"Available broker methods: {', '.join(available_methods)}")

        # Check if strategy uses order-related imports
        try:
            module = strategy.__class__.__module__
            if module:
                strategy_module = sys.modules.get(module)
                if strategy_module:
                    module_source = inspect.getsource(strategy_module)
                    if "PlaceOrderRequest" in module_source or "OrderSide" in module_source:
                        details_parts.append("Strategy imports order-related models")
        except Exception:
            pass  # Source inspection is optional

        return "\n".join(details_parts) if details_parts else None

    def _get_order_capability_tip(self, strategy: TektiiStrategy) -> Optional[str]:
        """Get educational tip for order capabilities."""
        broker_methods = ["place_order", "cancel_order", "modify_order"]
        available_methods = [method for method in broker_methods if hasattr(strategy, method) and callable(getattr(strategy, method))]

        if len(available_methods) < 3:
            return "Consider implementing cancel_order and modify_order for better order management"
        return None

    def _check_error_handling(self, strategy: TektiiStrategy) -> None:
        """Check error handling capabilities with various invalid inputs."""
        start_time = time.perf_counter()

        error_scenarios: list[tuple[str, Callable[[], None]]] = [
            ("Invalid Prices", lambda: self._test_negative_prices(strategy)),
            ("Missing Data", lambda: self._test_missing_data(strategy)),
            ("Invalid Symbols", lambda: self._test_invalid_symbols(strategy)),
            ("Extreme Values", lambda: self._test_extreme_values(strategy)),
        ]

        handled_errors = 0
        unhandled: list[str] = []

        for scenario_name, test_func in error_scenarios:
            try:
                test_func()
                # If no exception, strategy may not be validating input
                unhandled.append(scenario_name)
            except Exception:
                # Exception is good - strategy is handling invalid data
                handled_errors += 1

        status, message, tip = self._assess_error_handling(handled_errors, len(error_scenarios), unhandled)

        self.result.add_check(
            "Error Handling",
            ValidationCheck(
                name="Input Validation",
                status=status,
                message=message,
                details=f"May not validate: {', '.join(unhandled)}" if unhandled and status == ValidationStatus.WARNING else None,
                educational_tip=tip,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _assess_error_handling(self, handled: int, total: int, unhandled: list[str]) -> tuple[ValidationStatus, str, str]:
        """Assess error handling quality and return status, message, tip."""
        if handled == total:
            return (
                ValidationStatus.PASSED,
                f"Handles all {total} error scenarios",
                "Excellent error handling - this makes your strategy more robust",
            )
        elif handled > 0:
            return (
                ValidationStatus.WARNING,
                f"Handles {handled}/{total} error scenarios",
                "Add try-catch blocks and input validation for edge cases",
            )
        else:
            return (
                ValidationStatus.WARNING,
                "Strategy may not have robust error handling",
                "Add validation for None values, negative prices, and missing data fields",
            )

    def _test_negative_prices(self, strategy: TektiiStrategy) -> None:
        """Test with negative prices."""
        candle_data = CandleData(
            symbol="TEST",
            open=Decimal("-100.0"),
            high=Decimal("-99.0"),
            low=Decimal("-101.0"),
            close=Decimal("-99.5"),
            volume=1000,
            candle_type=CandleType.TIME,
        )

        if hasattr(strategy, "on_candle_data"):
            strategy.on_candle_data(candle_data)

    def _test_missing_data(self, strategy: TektiiStrategy) -> None:
        """Test with missing/None data."""
        # Skip this test as on_candle_data expects CandleData, not None
        pass

    def _test_invalid_symbols(self, strategy: TektiiStrategy) -> None:
        """Test with invalid symbols."""
        candle_data = CandleData(
            symbol="",  # Empty symbol
            open=Decimal("100.0"),
            high=Decimal("100.1"),
            low=Decimal("99.9"),
            close=Decimal("100.05"),
            volume=1000,
            candle_type=CandleType.TIME,
        )

        if hasattr(strategy, "on_candle_data"):
            strategy.on_candle_data(candle_data)

    def _test_extreme_values(self, strategy: TektiiStrategy) -> None:
        """Test with extreme values."""
        candle_data = CandleData(
            symbol="TEST",
            open=Decimal("10000000000"),  # Very large number
            high=Decimal("10000000001"),
            low=Decimal("9999999999"),
            close=Decimal("10000000000.5"),
            volume=1000000,
            candle_type=CandleType.TIME,
        )

        if hasattr(strategy, "on_candle_data"):
            strategy.on_candle_data(candle_data)

    def _check_edge_cases(self, strategy: TektiiStrategy) -> None:
        """Check strategy behavior with market edge cases."""
        start_time = time.perf_counter()

        edge_cases = [
            ("Zero Volume", self._test_zero_volume),
            ("Wide Spread", self._test_wide_spread),
            ("Price Gap", self._test_price_gap),
            ("Rapid Events", self._test_rapid_events),
            ("Stale Data", self._test_stale_data),
        ]

        passed_cases = 0
        failed_cases: list[str] = []

        for case_name, test_func in edge_cases:
            try:
                test_func(strategy)
                passed_cases += 1
            except Exception as e:
                failed_cases.append(f"{case_name}: {str(e)}")

        status, message, tip = self._assess_edge_cases(passed_cases, len(edge_cases))

        self.result.add_check(
            "Edge Cases",
            ValidationCheck(
                name="Market Edge Cases",
                status=status,
                message=message,
                details="\n".join(failed_cases) if failed_cases else None,
                educational_tip=tip,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            ),
        )

    def _assess_edge_cases(self, passed: int, total: int) -> tuple[ValidationStatus, str, str]:
        """Assess edge case handling and return status, message, tip."""
        if passed == total:
            return (ValidationStatus.PASSED, f"Passed all {total} edge case tests", "Your strategy handles unusual market conditions well")
        elif passed > 0:
            return (ValidationStatus.WARNING, f"Passed {passed}/{total} edge case tests", "Consider adding handling for unusual market conditions")
        else:
            return (ValidationStatus.FAILED, "Failed all edge case tests", "Add error handling for market gaps, wide spreads, and zero volume")

    def _test_zero_volume(self, strategy: TektiiStrategy) -> None:
        """Test with zero volume candle."""
        candle_data = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=DEFAULT_TEST_PRICE,
            high=DEFAULT_TEST_PRICE + Decimal("0.1"),
            low=DEFAULT_TEST_PRICE - Decimal("0.1"),
            close=DEFAULT_TEST_PRICE,
            volume=0,  # Zero volume
            candle_type=CandleType.TIME,
        )

        if hasattr(strategy, "on_candle_data"):
            strategy.on_candle_data(candle_data)

    def _test_wide_spread(self, strategy: TektiiStrategy) -> None:
        """Test with unrealistically wide high-low spread."""
        candle_data = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=Decimal("105.0"),
            high=Decimal("110.0"),  # Wide range
            low=Decimal("100.0"),  # 10% spread
            close=Decimal("105.0"),
            volume=1000,
            candle_type=CandleType.TIME,
        )

        if hasattr(strategy, "on_candle_data"):
            strategy.on_candle_data(candle_data)

    def _test_price_gap(self, strategy: TektiiStrategy) -> None:
        """Test with sudden large price movement."""
        if not hasattr(strategy, "on_candle_data"):
            return

        # Normal price
        candle1 = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=DEFAULT_TEST_PRICE,
            high=DEFAULT_TEST_PRICE + Decimal("0.1"),
            low=DEFAULT_TEST_PRICE - Decimal("0.1"),
            close=DEFAULT_TEST_PRICE + Decimal("0.05"),
            volume=1000,
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(candle1)

        # 50% price gap
        candle2 = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=Decimal("225.0"),
            high=Decimal("225.5"),
            low=Decimal("224.5"),
            close=Decimal("225.05"),
            volume=2000,
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(candle2)

    def _test_rapid_events(self, strategy: TektiiStrategy) -> None:
        """Test rapid-fire market data events."""
        if not hasattr(strategy, "on_candle_data"):
            return

        for i in range(100):
            price_adj = Decimal("0.01") * (i % 10 - 5)  # Small oscillations
            base_price = DEFAULT_TEST_PRICE + price_adj

            candle_data = CandleData(
                symbol=DEFAULT_TEST_SYMBOL,
                open=base_price,
                high=base_price + Decimal("0.1"),
                low=base_price - Decimal("0.05"),
                close=base_price + Decimal("0.05"),
                volume=1000,
                candle_type=CandleType.TIME,
            )
            strategy.on_candle_data(candle_data)

    def _test_stale_data(self, strategy: TektiiStrategy) -> None:
        """Test with old timestamp data."""
        if not hasattr(strategy, "on_candle_data"):
            return

        candle_data = CandleData(
            symbol=DEFAULT_TEST_SYMBOL,
            open=DEFAULT_TEST_PRICE,
            high=DEFAULT_TEST_PRICE + Decimal("0.1"),
            low=DEFAULT_TEST_PRICE - Decimal("0.1"),
            close=DEFAULT_TEST_PRICE + Decimal("0.05"),
            volume=1000,
            candle_type=CandleType.TIME,
        )
        strategy.on_candle_data(candle_data)

    def _check_performance(self, strategy: TektiiStrategy) -> None:
        """Check performance characteristics per event processor."""
        # Define test data for each event processor
        event_processors = self._create_event_processor_test_data()

        # Track which processors are implemented
        implemented_processors = self._get_implemented_processors(strategy, event_processors)

        if not implemented_processors:
            self.result.add_check(
                "Performance",
                ValidationCheck(
                    name="Event Processor Performance",
                    status=ValidationStatus.SKIPPED,
                    message="No event processors implemented to test",
                    educational_tip="Implement market data handlers for performance testing",
                ),
            )
            return

        # Performance metrics per processor
        processor_metrics = self._measure_processor_performance(strategy, implemented_processors)

        # Format metrics for display
        self.result.performance_metrics = self._format_performance_metrics(processor_metrics, event_processors)

        # Assess overall performance
        self._assess_performance_results(processor_metrics)

    def _create_event_processor_test_data(self) -> dict[str, Any]:
        """Create test data for each event processor."""
        from tektii.models.strategy.events import AccountUpdateEvent, OrderUpdateEvent, TradeUpdate
        from tektii.models.strategy.types.order_side import OrderSide
        from tektii.models.strategy.types.order_status import OrderStatus
        from tektii.models.strategy.types.order_type import OrderType

        return {
            "on_candle_data": CandleData(
                symbol=DEFAULT_TEST_SYMBOL,
                open=DEFAULT_TEST_PRICE,
                high=DEFAULT_TEST_PRICE + Decimal("1.0"),
                low=DEFAULT_TEST_PRICE - Decimal("0.5"),
                close=DEFAULT_TEST_PRICE + Decimal("0.75"),
                volume=1000000,
                candle_size=1,
                candle_size_unit="min",
                candle_type=CandleType.TIME,
                vwap=None,
                trade_count=None,
            ),
            "on_order_update": OrderUpdateEvent(
                order_id="TEST-001",
                symbol=DEFAULT_TEST_SYMBOL,
                side=OrderSide.BUY,
                quantity=DEFAULT_TEST_QUANTITY,
                order_type=OrderType.LIMIT,
                limit_price=DEFAULT_TEST_PRICE,
                status=OrderStatus.FILLED,
                filled_quantity=DEFAULT_TEST_QUANTITY,
                created_at_us=1000000,
                updated_at_us=1000001,
            ),
            "on_account_update": AccountUpdateEvent(
                cash_balance=Decimal("100000.00"),
                portfolio_value=Decimal("100000.00"),
                buying_power=Decimal("100000.00"),
                total_pnl=Decimal("0.00"),
            ),
            "on_trade_update": TradeUpdate(
                trade_id="TRADE-001",
                symbol=DEFAULT_TEST_SYMBOL,
                side=OrderSide.BUY,
                quantity=DEFAULT_TEST_QUANTITY,
                remaining_quantity=DEFAULT_TEST_QUANTITY,
                entry_price=DEFAULT_TEST_PRICE,
                entry_timestamp_us=1000000,
                unrealized_pnl=Decimal("0.00"),
                realized_pnl=Decimal("0.00"),
                timestamp_us=1000000,
            ),
            "on_initalize": ({}, []),  # config and symbols parameters
            "on_shutdown": None,  # No parameters needed
        }

    def _get_implemented_processors(self, strategy: TektiiStrategy, event_processors: dict[str, Any]) -> dict[str, Any]:
        """Get implemented event processors from the strategy."""
        implemented = {}

        for processor_name, test_data in event_processors.items():
            if hasattr(strategy, processor_name):
                method = getattr(strategy, processor_name)
                # Check if it's actually implemented (not just inherited base method)
                if callable(method) and method.__qualname__ != f"TektiiStrategy.{processor_name}":
                    implemented[processor_name] = test_data

        return implemented

    def _measure_processor_performance(self, strategy: TektiiStrategy, implemented_processors: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Measure performance for each implemented processor."""
        processor_metrics: dict[str, dict[str, Any]] = {}

        # Suppress logs during performance testing
        with suppress_strategy_logs(strategy):
            for processor_name, test_data in implemented_processors.items():
                processor_method = getattr(strategy, processor_name)

                # Warmup phase
                self._warmup_processor(processor_method, processor_name, test_data)

                # Performance measurement
                latencies = self._measure_processor_latencies(processor_method, processor_name, test_data)

                # Calculate statistics
                if latencies:
                    processor_metrics[processor_name] = self._calculate_performance_stats(latencies)

        return processor_metrics

    def _warmup_processor(self, processor_method: Callable[..., Any], processor_name: str, test_data: Any) -> None:
        """Warm up a processor with test data."""
        for _ in range(self.config.num_warmup_events):
            with suppress(Exception):
                if processor_name == "on_initalize" and isinstance(test_data, tuple):
                    processor_method(test_data[0], test_data[1])
                elif processor_name == "on_shutdown":
                    processor_method()
                else:
                    processor_method(test_data)

    def _measure_processor_latencies(self, processor_method: Callable[..., Any], processor_name: str, test_data: Any) -> list[float]:
        """Measure latencies for a processor."""
        num_events = self.config.num_perf_test_events
        latencies: list[float] = []

        for _ in range(num_events):
            start_time = time.perf_counter()
            with suppress(Exception):
                if processor_name == "on_initalize" and isinstance(test_data, tuple):
                    processor_method(test_data[0], test_data[1])
                elif processor_name == "on_shutdown":
                    processor_method()
                else:
                    processor_method(test_data)
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1_000_000)  # microseconds

        return latencies

    def _calculate_performance_stats(self, latencies: list[float]) -> dict[str, Any]:
        """Calculate performance statistics from latencies."""
        sorted_latencies = sorted(latencies)
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)

        # Calculate percentiles
        n = len(sorted_latencies)
        p95_index = int(0.95 * (n - 1))
        p99_index = int(0.99 * (n - 1))
        p95_latency = sorted_latencies[p95_index]
        p99_latency = sorted_latencies[p99_index]
        max_latency = max(latencies)

        # Calculate throughput
        total_time = sum(latencies) / 1_000_000  # convert to seconds
        events_per_second = len(latencies) / total_time if total_time > 0 else 0

        return {
            "throughput": f"{events_per_second:.0f} events/sec",
            "mean": f"{mean_latency:.2f} μs",
            "median": f"{median_latency:.2f} μs",
            "p95": f"{p95_latency:.2f} μs",
            "p99": f"{p99_latency:.2f} μs",
            "max": f"{max_latency:.2f} μs",
            "_raw": {
                "throughput": events_per_second,
                "p99": p99_latency,
                "max": max_latency,
            },
        }

    def _format_performance_metrics(self, processor_metrics: dict[str, dict[str, Any]], event_processors: dict[str, Any]) -> dict[str, str]:
        """Format performance metrics for display."""
        formatted_metrics = {"_header": "Per Event Processor Latency Metrics"}

        # Add implemented processors with their metrics
        for processor, metrics in processor_metrics.items():
            processor_display = self._format_processor_name(processor)

            # Create a compact metric string
            metric_str = f"Mean: {metrics['mean']}, P99: {metrics['p99']}, Max: {metrics['max']}"
            formatted_metrics[processor_display] = metric_str

            # Also add throughput separately
            throughput_key = f"{processor_display} (throughput)"
            formatted_metrics[throughput_key] = metrics["throughput"]

        # Add not implemented processors
        not_implemented = [processor for processor in event_processors.keys() if processor not in processor_metrics]

        for processor in not_implemented:
            processor_display = self._format_processor_name(processor)
            formatted_metrics[processor_display] = "Not implemented"

        return formatted_metrics

    def _format_processor_name(self, processor_name: str) -> str:
        """Format processor name for display."""
        if processor_name == "on_initalize":
            return "Initialize"
        elif processor_name == "on_position_update":
            return "Position Update"
        else:
            return processor_name.replace("on_", "").replace("_", " ").title()

    def _assess_performance_results(self, processor_metrics: dict[str, dict[str, Any]]) -> None:
        """Assess overall performance and create validation check."""
        status = ValidationStatus.PASSED
        details: list[str] = []
        performance_tier = "Retail"  # Default assumption

        for processor_name, metrics in processor_metrics.items():
            raw = metrics["_raw"]
            processor_display = processor_name.replace("_", " ").title()

            # Determine performance tier based on throughput
            if raw["throughput"] >= self.config.hft_throughput_eps:
                performance_tier = "HFT"
            elif raw["throughput"] >= self.config.recommended_throughput_eps:
                performance_tier = "Professional"

            # Check thresholds
            if raw["throughput"] < self.config.min_throughput_eps:
                status = ValidationStatus.FAILED
                details.append(
                    f"{processor_display}: Very low throughput ({raw['throughput']:.0f} events/sec, minimum: {self.config.min_throughput_eps})"
                )
            elif raw["throughput"] < self.config.recommended_throughput_eps:
                if status == ValidationStatus.PASSED:
                    status = ValidationStatus.WARNING
                details.append(
                    f"{processor_display}: Low throughput ({raw['throughput']:.0f} events/sec, "
                    f"recommended: >{self.config.recommended_throughput_eps})"
                )

            if raw["p99"] > self.config.max_p99_latency_us:
                if status == ValidationStatus.PASSED:
                    status = ValidationStatus.WARNING
                details.append(f"{processor_display}: High P99 latency ({raw['p99']:.0f} μs, recommended: <{self.config.max_p99_latency_us} μs)")

            if raw["max"] > self.config.max_latency_spike_us:
                if status == ValidationStatus.PASSED:
                    status = ValidationStatus.WARNING
                details.append(
                    f"{processor_display}: Very high max latency ({raw['max']:.0f} μs, "
                    f"spikes >{self.config.max_latency_spike_us/1000}ms may impact trading)"
                )

        # Create summary message
        if processor_metrics:
            first_processor = list(processor_metrics.keys())[0]
            summary = f"{len(processor_metrics)} processors tested ({performance_tier} tier)"
            if first_processor in processor_metrics:
                raw = processor_metrics[first_processor]["_raw"]
                summary += f", avg throughput: {raw['throughput']:.0f} events/sec"
        else:
            summary = "No processors to test"

        # Educational tip based on performance tier
        tip = {
            "Retail": "Performance suitable for retail strategies. Consider optimizations for higher frequency trading.",
            "Professional": "Good performance for professional strategies. Monitor latency spikes in production.",
            "HFT": "Excellent performance for high-frequency strategies. Ensure consistent low latency.",
        }.get(performance_tier)

        self.result.add_check(
            "Performance",
            ValidationCheck(
                name="Event Processor Performance",
                status=status,
                message=summary,
                details="\n".join(details) if details else None,
                educational_tip=tip,
            ),
        )

    def _check_memory_leaks(self, strategy: TektiiStrategy) -> None:
        """Check for memory leaks during extended operation."""
        if not hasattr(strategy, "on_candle_data"):
            self.result.add_check(
                "Performance",
                ValidationCheck(
                    name="Memory Leak Test",
                    status=ValidationStatus.SKIPPED,
                    message="No data handlers to test",
                    educational_tip="Implement market data handlers for memory testing",
                ),
            )
            return

        import gc

        # Force garbage collection and start memory tracking
        gc.collect()
        tracemalloc.start()
        memory_start = tracemalloc.get_traced_memory()[0]

        # Run strategy for extended period
        self._run_memory_stress_test(strategy, gc)

        # Final memory check
        memory_current, memory_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        memory_growth_mb = (memory_current - memory_start) / 1024 / 1024
        peak_memory_mb = memory_peak / 1024 / 1024

        self.result.memory_metrics = {
            "peak_memory": f"{peak_memory_mb:.2f} MB",
            "memory_growth": f"{memory_growth_mb:.2f} MB",
            "events_processed": self.config.num_memory_test_events,
        }

        # Assess memory usage
        status, details, tip = self._assess_memory_usage(memory_growth_mb, peak_memory_mb)

        self.result.add_check(
            "Performance",
            ValidationCheck(
                name="Memory Leak Test",
                status=status,
                message=f"Peak: {peak_memory_mb:.2f}MB, Growth: {memory_growth_mb:.2f}MB",
                details="\n".join(details) if details else None,
                educational_tip=tip,
            ),
        )

    def _run_memory_stress_test(self, strategy: TektiiStrategy, gc: Any) -> None:
        """Run memory stress test on the strategy."""
        num_events = self.config.num_memory_test_events

        # Suppress logs during memory testing
        with suppress_strategy_logs(strategy):
            for i in range(num_events):
                # Vary the data slightly to prevent optimization
                price_variation = Decimal(str((i % 100) * 0.01))
                base_price = DEFAULT_TEST_PRICE + price_variation

                candle_data = CandleData(
                    symbol=DEFAULT_TEST_SYMBOL,
                    open=base_price,
                    high=base_price + Decimal("0.1"),
                    low=base_price - Decimal("0.05"),
                    close=base_price + Decimal("0.05"),
                    volume=1000,
                    candle_type=CandleType.TIME,
                )

                if hasattr(strategy, "on_candle_data"):
                    strategy.on_candle_data(candle_data)

                # Force GC periodically
                if i % 1000 == 0:
                    gc.collect()

    def _assess_memory_usage(self, growth_mb: float, peak_mb: float) -> tuple[ValidationStatus, list[str], str]:
        """Assess memory usage and return status, details, and tip."""
        status = ValidationStatus.PASSED
        details: list[str] = []
        tip = "Good memory management - strategy should scale well in production"

        if growth_mb > self.config.max_memory_growth_mb:
            status = ValidationStatus.FAILED
            details.append(f"Significant memory leak: {growth_mb:.2f} MB growth over {self.config.num_memory_test_events} events")
            tip = "Check for unbounded data structures or missing cleanup in event handlers"
        elif growth_mb > self.config.warning_memory_growth_mb:
            status = ValidationStatus.WARNING
            details.append(f"Potential memory leak: {growth_mb:.2f} MB growth over {self.config.num_memory_test_events} events")
            tip = "Monitor memory usage in production and consider limiting historical data storage"

        if peak_mb > self.config.max_peak_memory_mb:
            if status == ValidationStatus.PASSED:
                status = ValidationStatus.WARNING
            details.append(f"High peak memory usage: {peak_mb:.2f} MB")
            if tip == "Good memory management - strategy should scale well in production":
                tip = "Consider optimizing data structures to reduce memory footprint"

        return status, details, tip

    def _collect_strategy_info(self, strategy: TektiiStrategy) -> None:
        """Collect comprehensive information about the strategy."""
        # Basic info
        self.result.strategy_info["name"] = strategy.__class__.__name__
        self.result.strategy_info["module"] = strategy.__class__.__module__

        # Documentation
        if strategy.__class__.__doc__:
            doc_lines = strategy.__class__.__doc__.strip().split("\n")
            self.result.strategy_info["description"] = doc_lines[0]
            if len(doc_lines) > 1:
                self.result.strategy_info["documentation"] = "Multi-line docstring"

        # Memory footprint
        size_bytes = sys.getsizeof(strategy)
        self.result.strategy_info["base_memory"] = f"{size_bytes} bytes"

        # Analyze data structures
        self._analyze_data_structures(strategy)

    def _analyze_data_structures(self, strategy: TektiiStrategy) -> None:
        """Analyze strategy data structures for potential issues."""
        large_structures: list[str] = []
        state_attrs: list[str] = []

        for attr_name in dir(strategy):
            if not attr_name.startswith("_"):
                try:
                    attr = getattr(strategy, attr_name)
                    if not callable(attr):
                        state_attrs.append(attr_name)
                        if hasattr(attr, "__len__"):
                            length = len(attr)
                            if length > 1000:
                                large_structures.append(f"{attr_name} ({length} items)")
                except Exception:
                    pass

        if large_structures:
            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="Data Structures",
                    status=ValidationStatus.WARNING,
                    message="Large data structures detected",
                    details=", ".join(large_structures),
                    educational_tip="Consider using deque with maxlen or periodic cleanup for large datasets",
                ),
            )

        # Check for state complexity
        if len(state_attrs) > 20:
            self.result.add_check(
                "Structure",
                ValidationCheck(
                    name="State Complexity",
                    status=ValidationStatus.WARNING,
                    message=f"Complex state: {len(state_attrs)} attributes",
                    details="Consider simplifying state management",
                    educational_tip="Complex state can make strategies harder to debug and maintain",
                ),
            )
        elif len(state_attrs) > 0:
            self.result.strategy_info["state_attributes"] = len(state_attrs)


@contextmanager
def memory_tracking() -> Generator[None, None, None]:
    """Context manager for memory tracking."""
    tracemalloc.start()
    try:
        yield
    finally:
        tracemalloc.stop()


def validate_strategy(
    strategy_class: Type[TektiiStrategy], comprehensive: bool = True, config: Optional[ValidationConfig] = None
) -> ValidationResult:
    """Validate a strategy class.

    Args:
        strategy_class: Strategy class to validate
        comprehensive: Whether to run comprehensive tests
        config: Optional validation configuration

    Returns:
        Validation result
    """
    validator = StrategyValidator(strategy_class, config=config)
    return validator.validate(comprehensive=comprehensive)


def validate_module(module_path: str, class_name: str, comprehensive: bool = True) -> ValidationResult:
    """Validate a strategy from a module file.

    Args:
        module_path: Path to Python module
        class_name: Name of strategy class
        comprehensive: Whether to run comprehensive tests

    Returns:
        Validation result
    """
    try:
        strategy_class = load_strategy_class(module_path, class_name)
        return validate_strategy(strategy_class, comprehensive=comprehensive)
    except Exception as e:
        result = ValidationResult(is_valid=False)
        result.add_check(
            "Module Loading",
            ValidationCheck(
                name="Load Strategy",
                status=ValidationStatus.FAILED,
                message=f"Failed to load strategy: {str(e)}",
                details=traceback.format_exc(),
                educational_tip="Check for missing imports or syntax errors in your strategy file",
            ),
        )
        return result


def cmd_validate(args: Any) -> int:
    """Validate a strategy implementation using the comprehensive validator."""
    strategy_file = args.file

    if not os.path.exists(strategy_file):
        console.print(f"[bold red]❌ Error: {strategy_file} not found[/bold red]")
        console.print("\n[cyan]Suggestions:[/cyan]")
        console.print("  • Check if the file path is correct")
        console.print("  • Run 'tektii status' to see recent strategies")
        console.print("  • Create a new strategy: tektii new my_strategy")
        return 1

    console.print(Panel.fit(f"[bold cyan]Validating Strategy[/bold cyan]\n{strategy_file}", border_style="cyan"))
    console.print()

    # Load and validate strategy
    strategy_class = _load_strategy_module(strategy_file)
    if not strategy_class:
        return 1

    # Run validation
    comprehensive = not getattr(args, "fast", False)
    validation_mode = "comprehensive" if comprehensive else "fast"
    console.print(f"[dim]Running {validation_mode} validation...[/dim]\n")

    # Temporarily suppress broker warnings during validation
    original_level = logging.getLogger("tektii.strategy").level
    logging.getLogger("tektii.strategy").setLevel(logging.ERROR)

    try:
        result = validate_strategy(strategy_class, comprehensive=comprehensive)
    finally:
        # Restore original logging level
        logging.getLogger("tektii.strategy").setLevel(original_level)

    # Display results
    console.print()
    result.display()

    return 0 if result.is_valid else 1


def _load_strategy_module(strategy_file: str) -> Optional[Type[TektiiStrategy]]:
    """Load strategy module and find strategy class."""
    # Load the strategy module
    with console.status("[cyan]Loading strategy module...") as _:
        try:
            spec = importlib.util.spec_from_file_location("strategy", strategy_file)
            if spec is None:
                raise ValueError("Failed to create module spec")
            module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                raise ValueError("Module spec has no loader")
            spec.loader.exec_module(module)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to load module: {e}[/bold red]")
            console.print("\n[cyan]Common issues:[/cyan]")
            console.print("  • Missing imports: pip install -e .")
            console.print(f"  • Syntax errors: python -m py_compile {strategy_file}")
            console.print("  • Module issues: Check PYTHONPATH and __init__.py files")
            return None

    # Find strategy class
    return _find_strategy_class(module)


def _find_strategy_class(module: ModuleType) -> Optional[Type[TektiiStrategy]]:
    """Find TektiiStrategy subclass in the module."""
    strategy_class = None
    strategy_classes = []

    for name, obj in vars(module).items():
        if isinstance(obj, type) and issubclass(obj, TektiiStrategy) and obj != TektiiStrategy:
            strategy_classes.append((name, obj))
            if strategy_class is None:
                strategy_class = obj

    if not strategy_class:
        console.print("[bold red]❌ No TektiiStrategy subclass found[/bold red]")
        console.print("\n[cyan]Your strategy class must inherit from TektiiStrategy[/cyan]")
        console.print("\nExample:")
        console.print("[dim]from tektii.strategy import TektiiStrategy\n\nclass MyStrategy(TektiiStrategy):\n    pass[/dim]")
        return None

    if len(strategy_classes) > 1:
        class_names = [name for name, _ in strategy_classes]
        console.print(f"[yellow]Found multiple strategy classes: {', '.join(class_names)}[/yellow]")
        console.print(f"[cyan]Using: {strategy_class.__name__}[/cyan]")

    console.print(f"[green]✅ Found strategy class: {strategy_class.__name__}[/green]\n")
    return strategy_class
