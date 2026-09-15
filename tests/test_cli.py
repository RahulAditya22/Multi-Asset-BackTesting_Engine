import json

import pytest

from backtester.cli import main, parse_params


def test_parse_params() -> None:
    assert parse_params("short_window=10,long_window=30,entry_z=1.5") == {
        "short_window": 10,
        "long_window": 30,
        "entry_z": 1.5,
    }


def test_parse_params_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="name=value"):
        parse_params("short_window")


def test_cli_run_with_new_asset(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeYahoo:
        @staticmethod
        def download(*args, **kwargs):
            raise RuntimeError("rate limited")

    import backtester.data_loader as data_loader_module

    monkeypatch.setattr(data_loader_module, "yf", FakeYahoo)
    assert (
        main(
            [
                "run",
                "--asset",
                "S&P 500 E-mini",
                "--strategy",
                "ma-crossover",
                "--params",
                "short_window=2,long_window=3",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    assert output["symbol"] == "ES=F"
    assert output["rows"] == 15
    assert output["strategy"] == "ma-crossover"
    assert "ending_value" in output["metrics"]


def test_cli_run_mean_reversion(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeYahoo:
        @staticmethod
        def download(*args, **kwargs):
            raise RuntimeError("rate limited")

    import backtester.data_loader as data_loader_module

    monkeypatch.setattr(data_loader_module, "yf", FakeYahoo)
    assert (
        main(
            [
                "run",
                "--asset",
                "10-Year T-Note",
                "--strategy",
                "mean-reversion",
                "--params",
                "window=3,entry_z=1.0",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    assert output["symbol"] == "ZN=F"
