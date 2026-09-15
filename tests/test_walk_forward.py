import pandas as pd
import pytest

from backtester.engine import Backtester
from backtester.strategies.base import Strategy
from backtester.walk_forward import WalkForwardValidator


class FixedStrategy(Strategy):
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        return pd.Series(0, index=data.index)


def test_walk_forward_reports_both_windows() -> None:
    data = pd.DataFrame(
        {"Close": range(100, 116)},
        index=pd.date_range("2025-01-01", periods=16),
    )
    result = WalkForwardValidator(
        Backtester(initial_capital=1_000, transaction_cost=0, slippage=0)
    ).run(data, FixedStrategy(), fit_window=10, validation_window=6)

    assert len(result.fit_data) == 10
    assert len(result.validation_data) == 6
    assert result.in_sample["ending_value"] == 1_000
    assert result.out_of_sample["ending_value"] == 1_000
    assert set(result.in_sample) == set(result.out_of_sample)


def test_walk_forward_rejects_insufficient_data() -> None:
    data = pd.DataFrame({"Close": [100.0, 101.0, 102.0]})
    with pytest.raises(ValueError, match="enough rows"):
        WalkForwardValidator().run(data, FixedStrategy(), fit_window=2, validation_window=2)


def test_walk_forward_rejects_invalid_window_sizes() -> None:
    data = pd.DataFrame({"Close": [100.0, 101.0, 102.0, 103.0]})
    with pytest.raises(ValueError, match="at least 2"):
        WalkForwardValidator().run(data, FixedStrategy(), fit_window=1, validation_window=2)
