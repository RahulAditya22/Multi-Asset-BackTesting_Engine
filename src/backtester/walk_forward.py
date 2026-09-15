"""Walk-forward validation utilities for overfitting-aware backtests."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .engine import Backtester, BacktestResult
from .performance import PerformanceAnalyzer
from .strategies.base import Strategy


@dataclass(frozen=True)
class WalkForwardResult:
    """Hold in-sample and held-out validation results side by side."""

    in_sample: dict[str, float | int]
    out_of_sample: dict[str, float | int]
    fit_data: pd.DataFrame
    validation_data: pd.DataFrame
    fit_result: BacktestResult
    validation_result: BacktestResult


class WalkForwardValidator:
    """Split data into parameter-fitting and held-out validation windows."""

    def __init__(
        self,
        backtester: Backtester | None = None,
        analyzer: PerformanceAnalyzer | None = None,
    ) -> None:
        self.backtester = backtester or Backtester()
        self.analyzer = analyzer or PerformanceAnalyzer()

    def run(
        self,
        data: pd.DataFrame,
        strategy: Strategy,
        fit_window: int,
        validation_window: int,
    ) -> WalkForwardResult:
        """Backtest a fitting window and a subsequent held-out validation window."""
        if fit_window < 2 or validation_window < 2:
            raise ValueError("fit_window and validation_window must both be at least 2")
        frame = data.sort_index().copy()
        if len(frame) < fit_window + validation_window:
            raise ValueError("Data must contain enough rows for both walk-forward windows")

        split = fit_window
        fit_data = frame.iloc[:split].copy()
        validation_data = frame.iloc[split : split + validation_window].copy()
        fit_result = self.backtester.run(fit_data, strategy)
        validation_result = self.backtester.run(validation_data, strategy)
        return WalkForwardResult(
            in_sample=self.analyzer.analyze(fit_result.equity_curve, fit_result.trades),
            out_of_sample=self.analyzer.analyze(
                validation_result.equity_curve, validation_result.trades
            ),
            fit_data=fit_data,
            validation_data=validation_data,
            fit_result=fit_result,
            validation_result=validation_result,
        )
