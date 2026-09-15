"""Strategy interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Abstract interface for deterministic trading strategies."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate target positions aligned to the supplied bars."""
        raise NotImplementedError
