# Multi-Asset Backtesting Engine

[![CI](https://github.com/RahulAditya22/Multi-Asset-BackTesting_Engine/actions/workflows/ci.yml/badge.svg)](https://github.com/RahulAditya22/Multi-Asset-BackTesting_Engine/actions/workflows/ci.yml) [![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7)](https://multi-asset-backtesting-engine.onrender.com)

A Python backtesting framework that turns historical market prices into an auditable simulation of a trading strategy. You can select assets including crude oil, gold, EUR/USD, 10-Year T-Note futures, and S&P 500 E-mini futures, test moving-average crossover or mean-reversion rules, include transaction costs and slippage, and inspect return, CAGR, Sharpe ratio, drawdown, win rate, trades, and interactive charts. It is designed as an educational portfolio project: the goal is to make the mechanics of systematic trading understandable while keeping the implementation explicit and free of lookahead bias.

## Live demo

**[Open the interactive backtester](https://multi-asset-backtesting-engine.onrender.com)**

## How it works

1. **Load data** — `DataLoader` retrieves daily OHLCV data through `yfinance` and falls back to committed CSV samples when the network source is unavailable.
2. **Generate a signal** — a strategy converts completed bars into a target position: long, flat, or short.
3. **Execute on the next bar** — the engine deliberately waits one bar before acting on a signal, preventing the strategy from using the price that generated its own signal.
4. **Apply friction** — configurable transaction costs and slippage are charged on traded notional.
5. **Track the portfolio** — cash, position size, equity, and every execution are recorded.
6. **Analyze performance** — return, CAGR, annualized Sharpe, maximum drawdown and duration, win rate, and average win/loss are calculated.

## Supported assets

| Asset | Yahoo Finance ticker |
| --- | --- |
| Crude Oil | `CL=F` |
| Gold | `GC=F` |
| EUR/USD | `EURUSD=X` |
| 10-Year T-Note futures | `ZN=F` |
| S&P 500 E-mini futures | `ES=F` |

## Strategies

### Moving Average Crossover

A fast simple moving average is compared with a slower moving average. A fast average above the slow average produces a long target; otherwise the strategy is flat.

### Mean Reversion

A rolling mean and standard deviation form Bollinger-style bands. The strategy enters long when price falls below the lower band and exits when price returns to the rolling mean.

## Local setup

```bash
git clone https://github.com/RahulAditya22/Multi-Asset-BackTesting_Engine.git
cd Multi-Asset-BackTesting_Engine
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -v --cov=src --cov-report=term-missing
ruff check .
black --check .
streamlit run app/streamlit_app.py
```

## Command-line usage

The engine can also be run without Streamlit. From the repository root, set `PYTHONPATH=src` and invoke the package directly:

```bash
PYTHONPATH=src python -m backtester run --asset "S&P 500 E-mini" --strategy ma-crossover --params short_window=10,long_window=30
```

Available strategies are `ma-crossover` and `mean-reversion`. Strategy parameters are supplied as comma-separated `name=value` pairs. The CLI prints the selected asset, ticker, row count, strategy, and performance metrics as JSON.

## Project structure

```text
src/backtester/
├── __main__.py
├── cli.py
├── data_loader.py
├── engine.py
├── performance.py
├── plotting.py
└── strategies/
    ├── base.py
    ├── moving_average_crossover.py
    ├── mean_reversion.py
    └── walk_forward.py
app/streamlit_app.py
tests/
data/sample_csv/
.github/workflows/ci.yml
render.yaml
pyproject.toml
```

## Design decisions and limitations

- **Daily bars:** this project intentionally focuses on daily data rather than pretending to model intraday execution.
- **No lookahead:** signals generated from bar *t* are executed from bar *t+1*.
- **Simple execution model:** positions use the close as the reference price with configurable percentage slippage and transaction costs. This is not a broker-grade fill simulator.
- **Offline resilience:** small committed CSV fixtures keep the demo functional when Yahoo Finance is unavailable.
- **Educational scope:** there are no margin requirements, contract multipliers, futures roll modeling, borrow fees, corporate-action modeling, market impact, or live-order integration.

## What I'd improve next

- Add futures contract rolls and contract-specific multipliers/margin models.
- Add parameter-sensitivity analysis around walk-forward testing.
- Add portfolio-level allocation across multiple assets and volatility targeting.
- Add more realistic execution models and benchmark comparisons.
- Add downloadable backtest reports and persistent experiment tracking.

## Testing

The test suite covers CSV parsing, API failure fallback, strategy signals on hand-crafted price paths, next-bar execution, forced liquidation, return calculations, Sharpe calculation, drawdown behavior, and CLI parsing/execution. CI enforces Ruff, Black, pytest, and an 80% source-coverage floor.

## Disclaimer

This software is for education and research. Backtested or historical performance is not a guarantee of future results and should not be treated as financial advice.

## License

MIT License. See [LICENSE](LICENSE).
