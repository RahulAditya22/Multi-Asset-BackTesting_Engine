"""Bollinger-band mean-reversion strategy."""

from __future__ import annotations

import pandas as pd

from .base import Strategy


class MeanReversion(Strategy):
    """Buy below the lower Bollinger Band and exit at the rolling mean."""

    def __init__(self, window: int = 20, entry_z: float = 2.0) -> None:
        if window < 2 or entry_z <= 0:
            raise ValueError("window must be >= 2 and entry_z must be positive")
        self.window = window
        self.entry_z = entry_z

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Return a long/flat position series from Bollinger conditions."""
        if "Close" not in data:
            raise ValueError("Strategy data must contain a Close column")
        close = data["Close"]
        mean = close.rolling(self.window).mean()
        std = close.rolling(self.window).std(ddof=0)
        lower = mean - self.entry_z * std
        signal = pd.Series(0, index=data.index, dtype=int)
        in_trade = False
        for timestamp in data.index:
            price = close.loc[timestamp]
            if not in_trade and pd.notna(lower.loc[timestamp]) and price < lower.loc[timestamp]:
                in_trade = True
            elif in_trade and pd.notna(mean.loc[timestamp]) and price >= mean.loc[timestamp]:
                in_trade = False
            signal.loc[timestamp] = int(in_trade)
        signal.name = "signal"
        return signal
