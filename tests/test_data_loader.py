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
    loader = DataLoader(tmp_path)

    class FakeYahoo:
        @staticmethod
        def download(*args, **kwargs):
            raise RuntimeError("rate limited")

    import backtester.data_loader as data_loader_module

    monkeypatch.setattr(data_loader_module, "yf", FakeYahoo)
    assert len(loader.load("TEST")) == 3


@pytest.mark.parametrize("symbol", ["ZN=F", "ES=F"])
def test_new_asset_csv_fallback_loads(symbol: str) -> None:
    fallback_dir = Path(__file__).resolve().parents[1] / "data" / "sample_csv"
    data = DataLoader(fallback_dir).load_csv(symbol)
    assert list(data.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert len(data) == 15
    assert data.index.is_monotonic_increasing


@pytest.mark.parametrize("symbol", ["ZN=F", "ES=F"])
def test_new_asset_api_failure_falls_back_to_csv(
    symbol: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    fallback_dir = Path(__file__).resolve().parents[1] / "data" / "sample_csv"
    loader = DataLoader(fallback_dir)

    class FakeYahoo:
        @staticmethod
        def download(*args, **kwargs):
            raise RuntimeError("rate limited")

    import backtester.data_loader as data_loader_module

    monkeypatch.setattr(data_loader_module, "yf", FakeYahoo)
    data = loader.load(symbol)
    assert len(data) == 15
    assert data.index.is_monotonic_increasing


def test_missing_fallback_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No market data"):
        DataLoader(tmp_path).load_csv("MISSING")
