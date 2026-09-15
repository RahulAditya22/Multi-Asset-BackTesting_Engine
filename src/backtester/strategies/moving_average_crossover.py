"""Moving-average crossover strategy."""

from __future__ import annotations

import pandas as pd

from .base import Strategy


class MovingAverageCrossover(Strategy):
    """Trade when a short simple moving average crosses a long average."""

    def __init__(self, short_window: int = 20, long_window: int = 50) -> None:
        if short_window < 2 or long_window <= short_window:
            raise ValueError("short_window must be >= 2 and smaller than long_window")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Return long/flat target positions based on SMA crossover."""
        if "Close" not in data:
            raise ValueError("Strategy data must contain a Close column")
        short_ma = data["Close"].rolling(self.short_window).mean()
        long_ma = data["Close"].rolling(self.long_window).mean()
        return pd.Series((short_ma > long_ma).astype(int), index=data.index, name="signal")
