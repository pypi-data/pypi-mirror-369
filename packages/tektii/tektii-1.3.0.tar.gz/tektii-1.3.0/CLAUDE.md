# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Setup & Development
```bash
# First-time setup
make setup          # Complete setup with virtual environment, dependencies, and proto generation

# Install dependencies
make install        # Install package (includes proto dependencies from buf.build)
make install-dev    # Install with development dependencies

# Proto Dependencies
# The project now uses pre-built proto packages from buf.build/gen/python
# Proto files are installed as Python packages via pip with --extra-index-url https://buf.build/gen/python
# Located in: .venv/lib/python3.*/site-packages/broker/v1/ and .venv/lib/python3.*/site-packages/strategy/v1/
# No manual proto generation needed - packages are fetched from buf.build registry
```

### Quality Checks (ALWAYS run before completing tasks)
```bash
# Run ALL quality checks
make check          # Runs lint, type-check, and test

# Individual checks
make lint           # Run flake8 and bandit security checks
make type-check     # Run mypy type checking
make test           # Run all tests with coverage
make format         # Auto-format with black and isort
```

### Testing Commands
```bash
# Test execution
make test           # Run all tests with coverage
make test-unit      # Run unit tests only
make test-fast      # Run fast unit tests (skip slow tests)

# Run specific test
pytest tests/unit/models/test_orders.py::TestOrderBuilder::test_fluent_api -xvs
```

## High-Level Architecture

The **tektii** Python SDK provides a comprehensive framework for building algorithmic trading strategies with a refactored dual-service architecture that cleanly separates broker operations from strategy logic.

### Core Components

**Strategy Base (`tektii/strategy.py`)**
- `TektiiStrategy` abstract base class that all strategies inherit from
- `TektiiStrategyServer` gRPC server with robust event routing and error handling
- Event-driven architecture with methods like `on_market_data()`, `on_order_update()`, etc.
- Manages order lifecycle, position tracking, and account state

**Dual Model Architecture (`tektii/models/`)**

*Base Layer (`tektii/models/base.py`)*
- `ProtoConvertible[T]` protocol for type-safe proto conversions
- `ProtoEnum` base class with business logic methods
- `PreciseDecimal` for 6-decimal financial precision
- Shared protocols and type definitions

*Broker Service Models (`tektii/models/broker/`)*
- Request/response handlers for broker operations
- Core types: `Order`, `Account`, `Position`, `Fill`
- Proto conversions for broker-specific messages
- Handler models for `place_order`, `cancel_order`, `get_state`, etc.

*Strategy Service Models (`tektii/models/strategy/`)*
- Event models for market data and updates
- Strategy-specific order types with validation
- Business logic-aware enums (e.g., `OrderStatus.is_terminal()`)
- Proto conversions for strategy messages

**CLI (`tektii/cli.py` & `tektii/commands/`)**
- `tektii new` (alias: `n`): Create new strategy from template
- `tektii serve` (alias: `s`): Run strategy as gRPC service
- `tektii test` (alias: `t`): Test strategy functionality
- `tektii validate` (alias: `v`): Validate strategy code
- `tektii push` (alias: `p`): Deploy to Tektii platform

**Testing Framework**
- Proto validation tests for all models
- Integration tests for gRPC communication
- Mock broker service for development

### Key Design Patterns

1. **Protocol-Based Architecture**: `ProtoConvertible[T]` protocol enables type-safe proto conversions
2. **Dual-Service Separation**: Clear boundaries between broker operations and strategy logic
3. **Enhanced Type Safety**: Generic protocols with full mypy/pyright support
4. **Financial Precision**: `PreciseDecimal` with 6-decimal places for all monetary values
5. **Business Logic Enums**: Enums with methods like `is_terminal()`, `is_active()`, `from_string()`
6. **Event Routing**: Automatic proto event detection and model conversion
7. **Robust gRPC Server**: Exponential backoff retry, health checks, graceful error handling

### Development Workflow

1. Create strategy by inheriting from `TektiiStrategy`
2. Implement event handlers using models from `tektii.models.strategy.events`
3. Create orders using:
   - Strategy's fluent builder API
   - Direct model instantiation (`MarketOrder`, `LimitOrder`, etc.)
   - Broker request models (`PlaceOrderRequest`)
4. Test with proto validation and integration tests
5. Run locally with `tektii serve` (gRPC server with retry logic)
6. Deploy with `tektii push` command

### Important Implementation Notes

#### Model System
- **Proto Protocol**: All models implement `ProtoConvertible[T]` for bidirectional conversion
- **Decimal Precision**: Use `PreciseDecimal` (6 decimal places) for all monetary values
- **Field Mapping**: Proto conversions handle field name differences automatically
- **Validation**: Pydantic validates models; additional business logic in model methods

#### Service Architecture
- **Broker Models**: Located in `tektii.models.broker` for broker operations
- **Strategy Models**: Located in `tektii.models.strategy` for strategy events
- **Shared Types**: Common enums/types may exist in both with service-specific logic
- **Handler Pattern**: Request/response models for each broker operation

#### Proto Integration
- **Pre-built Packages**: Proto files from buf.build registry (no manual generation)
- **Import Structure**:
  - Broker: `broker.v1.broker_common_pb2`, `broker.v1.handler_*_pb2`
  - Strategy: `strategy.v1.strategy_common_pb2`, `strategy.v1.handler_*_pb2`
- **Type Stubs**: `.pyi` files provide IDE support for proto imports

#### gRPC Server
- **Event Routing**: Automatic detection of proto event type and conversion
- **Connection Management**: Exponential backoff with health checks
- **Error Handling**: Proper gRPC status codes and detailed logging
- **Graceful Shutdown**: Clean resource cleanup on termination
