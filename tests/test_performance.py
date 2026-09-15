import math

import pandas as pd
import pytest

from backtester.performance import PerformanceAnalyzer


def test_known_total_return_and_drawdown() -> None:
    index = pd.date_range("2020-01-01", periods=5, freq="YE")
    curve = pd.Series([100, 120, 90, 110, 130], index=index)
    metrics = PerformanceAnalyzer().analyze(curve)
    assert metrics["total_return"] == pytest.approx(0.30)
    assert metrics["max_drawdown"] == pytest.approx(-0.25)


def test_sharpe_matches_manual_daily_calculation() -> None:
    index = pd.date_range("2025-01-01", periods=4, freq="D")
    curve = pd.Series([100, 101, 102.01, 103.0301], index=index)
    expected_returns = pd.Series([0.01, 0.01, 0.01])
    expected = math.sqrt(252) * expected_returns.mean() / expected_returns.std(ddof=1)
    actual = PerformanceAnalyzer().analyze(curve)["sharpe_ratio"]
    assert actual == pytest.approx(expected)
