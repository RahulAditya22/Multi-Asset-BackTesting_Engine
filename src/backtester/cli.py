"""Command-line interface for running a backtest."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .data_loader import DEFAULT_SYMBOLS, DataLoader
from .engine import Backtester
from .performance import PerformanceAnalyzer
from .strategies import MeanReversion, MovingAverageCrossover

STRATEGIES = {
    "ma-crossover": MovingAverageCrossover,
    "mean-reversion": MeanReversion,
}


def parse_params(raw: str | None) -> dict[str, Any]:
    """Parse comma-separated strategy parameters such as ``short_window=10``."""
    if not raw:
        return {}
    params: dict[str, Any] = {}
    for item in raw.split(","):
        if "=" not in item:
            raise ValueError(f"Invalid parameter '{item}'. Use name=value.")
        name, value = item.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name or not value:
            raise ValueError(f"Invalid parameter '{item}'. Use name=value.")
        try:
            params[name] = float(value) if "." in value else int(value)
        except ValueError:
            params[name] = value
    return params


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Run a Multi-Asset backtest.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run a backtest")
    run_parser.add_argument("--asset", choices=list(DEFAULT_SYMBOLS), required=True)
    run_parser.add_argument("--strategy", choices=list(STRATEGIES), required=True)
    run_parser.add_argument(
        "--params",
        help="Comma-separated strategy parameters, e.g. short_window=10,long_window=30",
    )
    run_parser.add_argument("--start")
    run_parser.add_argument("--end")
    run_parser.add_argument("--initial-capital", type=float, default=100_000.0)
    run_parser.add_argument("--transaction-cost", type=float, default=0.0005)
    run_parser.add_argument("--slippage", type=float, default=0.0005)
    return parser


def run_backtest(args: argparse.Namespace) -> dict[str, Any]:
    """Load data, construct the strategy, run the engine, and return metrics."""
    params = parse_params(args.params)
    strategy = STRATEGIES[args.strategy](**params)
    data = DataLoader().load(DEFAULT_SYMBOLS[args.asset], start=args.start, end=args.end)
    result = Backtester(
        initial_capital=args.initial_capital,
        transaction_cost=args.transaction_cost,
        slippage=args.slippage,
    ).run(data, strategy)
    metrics = PerformanceAnalyzer().analyze(result.equity_curve, result.trades)
    return {
        "asset": args.asset,
        "symbol": DEFAULT_SYMBOLS[args.asset],
        "strategy": args.strategy,
        "rows": len(data),
        "metrics": metrics,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and print results as JSON."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = run_backtest(args)
    except (TypeError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(output, indent=2))
    return 0
