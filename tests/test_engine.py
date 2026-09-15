import pandas as pd

from backtester.engine import Backtester
from backtester.strategies.base import Strategy


class FixedStrategy(Strategy):
    def __init__(self, signals: list[int]) -> None:
        self.signals = signals

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        return pd.Series(self.signals, index=data.index)


def test_engine_executes_on_next_bar_and_liquidates() -> None:
    data = pd.DataFrame({"Close": [100.0, 110.0, 120.0]}, index=pd.date_range("2025-01-01", periods=3))
    result = Backtester(initial_capital=1_000, transaction_cost=0, slippage=0).run(data, FixedStrategy([1, 0, 0]))
    assert len(result.trades) == 2
    assert result.positions.tolist() == [0.0, 1000 / 110, 0.0]
    assert result.equity_curve.iloc[-1] == 1000 + (120 - 110) * (1000 / 110)
