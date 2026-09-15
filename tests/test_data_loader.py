from pathlib import Path

import pandas as pd
import pytest

from backtester.data_loader import DataLoader


def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "TEST.csv"
    pd.DataFrame(
        {
            "Date": pd.date_range("2025-01-01", periods=3),
            "Open": [10, 11, 12],
            "High": [11, 12, 13],
            "Low": [9, 10, 11],
            "Close": [10.5, 11.5, 12.5],
            "Volume": [100, 110, 120],
        }
    ).to_csv(path, index=False)
    return path


def test_load_csv_parses_ohlcv(tmp_path: Path) -> None:
    sample_csv(tmp_path)
    data = DataLoader(tmp_path).load_csv("TEST")
    assert list(data.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert data.iloc[-1]["Close"] == 12.5


def test_api_failure_falls_back_to_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sample_csv(tmp_path)
    class FakeYahoo:
        @staticmethod
        def download(*args, **kwargs):
            raise RuntimeError("rate limited")
    import backtester.data_loader as data_loader_module
    monkeypatch.setattr(data_loader_module, "yf", FakeYahoo)
    assert len(DataLoader(tmp_path).load("TEST")) == 3


def test_missing_fallback_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No market data"):
        DataLoader(tmp_path).load_csv("MISSING")
