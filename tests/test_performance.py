import math

import pandas as pd
import pytest

from backtester.engine import Trade
from backtester.performance import PerformanceAnalyzer


def test_known_total_return_and_drawdown() -> None:
    index = pd.date_range("2020-01-01", periods=5, freq="YE")
    curve = pd.Series([100, 120, 90, 110, 130], index=index)
    metrics = PerformanceAnalyzer().analyze(curve)
    assert metrics["total_return"] == pytest.approx(0.30)
    assert metrics["max_drawdown"] == pytest.approx(-0.25)


def test_sharpe_matches_manual_daily_calculation() -> None:
    index = pd.date_range("2025-01-01", periods=4, freq="D")
    curve = pd.Series([100, 101, 103.02, 104.0602], index=index)
    expected_returns = pd.Series([0.01, 0.02, 0.010097068530382503])
    expected = math.sqrt(252) * expected_returns.mean() / expected_returns.std(ddof=1)
    actual = PerformanceAnalyzer().analyze(curve)["sharpe_ratio"]
    assert actual == pytest.approx(expected)


def test_trade_statistics() -> None:
    index = pd.date_range("2025-01-01", periods=2, freq="D")
    curve = pd.Series([100, 110], index=index)
    trades = [
        Trade(index[0], 100.0, 1.0, "BUY", 0.0),
        Trade(index[1], 110.0, -1.0, "SELL", 0.0),
    ]
    metrics = PerformanceAnalyzer().analyze(curve, trades)
    assert metrics["trade_count"] == 1
    assert metrics["win_rate"] == 1.0
    assert metrics["average_win"] == 10.0


def test_invalid_equity_curve_rejected() -> None:
    with pytest.raises(ValueError):
        PerformanceAnalyzer().analyze(pd.Series([100.0, 0.0]))
