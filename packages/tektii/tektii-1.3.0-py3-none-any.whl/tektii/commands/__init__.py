"""Command handlers for the Tektii CLI."""

from .analyze import cmd_analyze
from .backtest import cmd_backtest
from .new import cmd_new
from .push import cmd_push, push_strategy
from .serve import cmd_serve
from .validator import cmd_validate, validate_module, validate_strategy

__all__ = [
    # CLI command handlers
    "cmd_analyze",
    "cmd_backtest",
    "cmd_new",
    "cmd_push",
    "cmd_serve",
    "cmd_validate",
    # API functions
    "push_strategy",
    "validate_strategy",
    "validate_module",
]
