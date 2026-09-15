"""Market data loading with an offline CSV fallback."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import pandas as pd

try:
    import yfinance as yf
except ModuleNotFoundError:
    yf = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)
REQUIRED_COLUMNS: Final = ["Open", "High", "Low", "Close", "Volume"]
DEFAULT_SYMBOLS: Final[dict[str, str]] = {
    "Crude Oil": "CL=F",
    "Gold": "GC=F",
    "EUR/USD": "EURUSD=X",
}


class DataLoader:
    """Load OHLCV market data from Yahoo Finance or local CSV files."""

    def __init__(self, fallback_dir: str | Path = "data/sample_csv") -> None:
        self.fallback_dir = Path(fallback_dir)

    def load(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
    ) -> pd.DataFrame:
        """Return normalized OHLCV data for a symbol."""
        try:
            if yf is None:
                raise RuntimeError("yfinance is not installed")
            data = yf.download(
                symbol, start=start, end=end, auto_adjust=False, progress=False, threads=False
            )
            normalized = self._normalize(data)
            if not normalized.empty:
                return normalized
        except Exception as exc:
            LOGGER.warning("Yahoo Finance failed for %s: %s", symbol, exc)
        return self.load_csv(symbol, start=start, end=end)

    def load_csv(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
    ) -> pd.DataFrame:
        """Load and validate a symbol's fallback CSV."""
        path = self._fallback_path(symbol)
        if not path.exists():
            raise ValueError(f"No market data is available for {symbol}.")
        try:
            data = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
        except (OSError, ValueError, pd.errors.ParserError) as exc:
            raise ValueError(f"Could not parse fallback data for {symbol}.") from exc
        normalized = self._normalize(data)
        if start is not None:
            normalized = normalized.loc[normalized.index >= pd.Timestamp(start)]
        if end is not None:
            normalized = normalized.loc[normalized.index < pd.Timestamp(end)]
        if normalized.empty:
            raise ValueError(f"No market data is available for {symbol} in the requested range.")
        return normalized

    def _fallback_path(self, symbol: str) -> Path:
        """Return the conventional fallback path for a ticker."""
        safe_symbol = symbol.replace("=", "_").replace("/", "_")
        return self.fallback_dir / f"{safe_symbol}.csv"

    @staticmethod
    def _normalize(data: pd.DataFrame) -> pd.DataFrame:
        """Normalize Yahoo or CSV columns to a stable OHLCV schema."""
        if data is None or data.empty:
            return pd.DataFrame(columns=REQUIRED_COLUMNS)
        frame = data.copy()
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        frame.columns = [str(column).title() for column in frame.columns]
        missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(f"Market data is missing columns: {', '.join(missing)}")
        frame = frame[REQUIRED_COLUMNS].copy()
        frame.index = pd.to_datetime(frame.index)
        frame = frame[~frame.index.duplicated(keep="last")].sort_index()
        return frame.dropna(subset=["Open", "High", "Low", "Close"])
