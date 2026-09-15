import pandas as pd
import pytest

from backtester.strategies import MeanReversion, MovingAverageCrossover


def test_ma_crossover_known_signal() -> None:
    data = pd.DataFrame({"Close": [1, 1, 1, 10, 10, 10]})
    signals = MovingAverageCrossover(short_window=2, long_window=3).generate_signals(data)
    assert signals.tolist() == [0, 0, 0, 1, 1, 1]


def test_ma_rejects_invalid_windows() -> None:
    with pytest.raises(ValueError):
        MovingAverageCrossover(short_window=5, long_window=5)


def test_mean_reversion_enters_then_exits() -> None:
    data = pd.DataFrame({"Close": [100, 100, 100, 50, 100]})
    signals = MeanReversion(window=3, entry_z=1.0).generate_signals(data)
    assert signals.tolist() == [0, 0, 0, 1, 0]
