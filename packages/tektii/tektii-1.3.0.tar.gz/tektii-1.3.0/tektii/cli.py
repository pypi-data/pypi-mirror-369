#!/usr/bin/env python3
"""Tektii CLI entry point."""

import argparse
import sys

from tektii.commands.analyze import cmd_analyze
from tektii.commands.backtest import cmd_backtest
from tektii.commands.new import cmd_new
from tektii.commands.push import cmd_push
from tektii.commands.serve import cmd_serve
from tektii.commands.validator import cmd_validate


def main() -> None:
    """Run the main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Tektii Strategy SDK - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tektii new my_strategy
  tektii validate my_strategy.py
  tektii validate my_strategy.py --fast
  tektii serve my_strategy.py MyStrategy --port 50051
  tektii push my_strategy.py MyStrategy --save-config

Command Aliases:
  n, create  → new
  v, check   → validate
  s, run     → serve
  p, deploy  → push
  bt         → backtest
  a          → analyze

For help on specific commands: tektii <command> --help
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # New command with aliases
    new_parser = subparsers.add_parser("new", aliases=["n", "create"], help="Create a new strategy from template")
    new_parser.add_argument("name", help="Strategy name")
    new_parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    # Validate command with aliases
    validate_parser = subparsers.add_parser("validate", aliases=["v", "check"], help="Validate strategy implementation")
    validate_parser.add_argument("file", help="Strategy file to validate")
    validate_parser.add_argument("--fast", action="store_true", help="Skip performance and memory leak tests (faster validation)")

    # Serve command with aliases
    serve_parser = subparsers.add_parser("serve", aliases=["s", "run"], help="Run strategy as gRPC server")
    serve_parser.add_argument("module", help="Path to Python module containing strategy")
    serve_parser.add_argument("class_name", help="Name of the strategy class")
    serve_parser.add_argument("--port", "-p", type=int, default=50051, help="gRPC server port (default: 50051)")
    serve_parser.add_argument("--max-workers", type=int, default=10, help="Maximum number of worker threads (default: 10)")
    serve_parser.add_argument(
        "--broker", "-b", help="Broker service address (e.g., localhost:50052). If not provided, uses mock broker for development"
    )

    # Push command with aliases
    push_parser = subparsers.add_parser("push", aliases=["p", "deploy"], help="Push strategy to Tektii platform")
    push_parser.add_argument("module", help="Path to Python module containing strategy")
    push_parser.add_argument("class_name", help="Name of the strategy class")
    push_parser.add_argument("--api-url", help="Override API URL (default: https://api.tektii.com)")
    push_parser.add_argument("--save-config", action="store_true", help="Save configuration to ~/.tektii/config.json")
    push_parser.add_argument("--dry-run", action="store_true", help="Perform validation only without pushing")
    push_parser.add_argument("--registry", default="us-central1-docker.pkg.dev/tektii-prod/strategies", help="Container registry URL")
    push_parser.add_argument("--tag", help="Docker image tag (default: latest)")

    # Backtest command - run historical backtests on Tektii platform
    backtest_parser = subparsers.add_parser("backtest", aliases=["bt"], help="Run strategy backtest on Tektii platform")
    backtest_parser.add_argument("module", help="Path to Python module containing strategy")
    backtest_parser.add_argument("class_name", help="Name of the strategy class")
    backtest_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    backtest_parser.add_argument("--symbols", help="Comma-separated list of symbols (default: AAPL,GOOGL)")
    backtest_parser.add_argument("--initial-capital", type=float, default=100000, help="Initial capital (default: 100000)")
    backtest_parser.add_argument("--output", "-o", help="Output file for results (default: backtest_results.json)")
    backtest_parser.add_argument("--commission", type=float, default=0.001, help="Commission per trade (default: 0.001)")
    backtest_parser.add_argument("--slippage", type=float, default=0.0001, help="Slippage factor (default: 0.0001)")

    # Analyze command - analyze backtest results
    analyze_parser = subparsers.add_parser("analyze", aliases=["a"], help="Analyze backtest results and show performance metrics")
    analyze_parser.add_argument("results_file", nargs="?", help="Path to backtest results file (optional if using --backtest-id)")
    analyze_parser.add_argument("--backtest-id", help="Fetch results from platform using backtest ID")
    analyze_parser.add_argument("--save-local", action="store_true", help="Save platform results to local file")
    analyze_parser.add_argument("--metrics", help="Comma-separated metrics (default: all)")
    analyze_parser.add_argument("--benchmark", help="Benchmark symbol for comparison (e.g., SPY)")
    analyze_parser.add_argument("--export", help="Export analysis to file (html, pdf, csv)")
    analyze_parser.add_argument("--plot", action="store_true", help="Generate performance plots")

    args = parser.parse_args()

    if not args.command:
        parser.print_help(sys.stderr)
        sys.exit(2)

    # Handle command aliases
    command_map = {
        "n": "new",
        "create": "new",
        "v": "validate",
        "check": "validate",
        "s": "serve",
        "run": "serve",
        "p": "push",
        "deploy": "push",
        "bt": "backtest",
        "a": "analyze",
    }

    # Resolve aliases
    command = command_map.get(args.command, args.command)

    # Execute command
    if command == "new":
        sys.exit(cmd_new(args))
    elif command == "validate":
        sys.exit(cmd_validate(args))
    elif command == "serve":
        sys.exit(cmd_serve(args))
    elif command == "push":
        sys.exit(cmd_push(args))
    elif command == "backtest":
        sys.exit(cmd_backtest(args))
    elif command == "analyze":
        sys.exit(cmd_analyze(args))

    sys.exit(0)


if __name__ == "__main__":
    main()
