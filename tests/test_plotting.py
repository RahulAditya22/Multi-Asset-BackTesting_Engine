import pandas as pd

from backtester.plotting import drawdown_chart, equity_curve_chart, price_signal_chart


def test_plotting_functions_return_figures() -> None:
    index = pd.date_range("2025-01-01", periods=4)
    data = pd.DataFrame({"Close": [100, 105, 103, 108]}, index=index)
    signals = pd.Series([0, 1, 1, 0], index=index)
    assert len(equity_curve_chart(data["Close"]).data) == 1
    assert len(drawdown_chart(data["Close"]).data) == 1
    assert len(price_signal_chart(data, signals).data) == 3
