"""Interactive Streamlit showcase for the backtesting engine."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from backtester.data_loader import DEFAULT_SYMBOLS, DataLoader
from backtester.engine import Backtester
from backtester.performance import PerformanceAnalyzer
from backtester.plotting import drawdown_chart, equity_curve_chart, price_signal_chart
from backtester.strategies import MeanReversion, MovingAverageCrossover

st.set_page_config(page_title="Multi-Asset Backtesting Engine", page_icon="📈", layout="wide")
st.title("Multi-Asset Backtesting Engine")
st.caption(
    "A transparent, no-lookahead framework for testing systematic trading ideas on historical data."
)

with st.sidebar:
    st.header("Backtest Controls")
    asset_name = st.selectbox("Asset", list(DEFAULT_SYMBOLS))
    strategy_name = st.selectbox("Strategy", ["MA Crossover", "Mean Reversion"])
    initial_capital = st.number_input(
        "Initial capital", min_value=1_000.0, value=100_000.0, step=5_000.0
    )
    transaction_cost = st.slider("Transaction cost (%)", 0.0, 1.0, 0.05, 0.01) / 100
    slippage = st.slider("Slippage (%)", 0.0, 1.0, 0.05, 0.01) / 100

    if strategy_name == "MA Crossover":
        short_window = st.slider("Short MA", 2, 100, 20)
        long_window = st.slider("Long MA", 3, 250, 50)
        if short_window >= long_window:
            st.error("Short MA must be smaller than Long MA.")
            st.stop()
        strategy = MovingAverageCrossover(short_window, long_window)
    else:
        mean_window = st.slider("Mean window", 5, 100, 20)
        entry_z = st.slider("Entry Z-score", 0.5, 3.5, 2.0, 0.1)
        strategy = MeanReversion(mean_window, entry_z)


@st.cache_data(ttl=900, show_spinner=False)
def load_data(symbol: str) -> pd.DataFrame:
    """Load cached market data for the selected symbol."""
    return DataLoader().load(symbol)


try:
    data = load_data(DEFAULT_SYMBOLS[asset_name])
    if len(data) < 5:
        st.error("Not enough historical data is available for this selection.")
        st.stop()
    engine = Backtester(initial_capital, transaction_cost, slippage)
    result = engine.run(data, strategy)
    metrics = PerformanceAnalyzer().analyze(result.equity_curve, result.trades)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

metric_cols = st.columns(5)
metric_cols[0].metric("Total return", f"{metrics['total_return']:.2%}")
metric_cols[1].metric("CAGR", f"{metrics['cagr']:.2%}")
metric_cols[2].metric("Sharpe", f"{metrics['sharpe_ratio']:.2f}")
metric_cols[3].metric("Max drawdown", f"{metrics['max_drawdown']:.2%}")
metric_cols[4].metric("Win rate", f"{metrics['win_rate']:.2%}")

st.plotly_chart(equity_curve_chart(result.equity_curve), use_container_width=True)
st.plotly_chart(drawdown_chart(result.equity_curve), use_container_width=True)
signals = strategy.generate_signals(data)
st.plotly_chart(price_signal_chart(data, signals), use_container_width=True)

with st.expander("Trade statistics"):
    st.dataframe(pd.DataFrame([metrics]), use_container_width=True)

st.divider()
st.subheader("About this project")
st.write(
    "This project lets you test simple trading rules against historical market prices. "
    "The engine processes each completed daily bar in order and only executes a signal "
    "on the following bar, preventing future prices from leaking into the decision. "
    "Transaction costs and slippage are included so results are less optimistic than a "
    "frictionless toy backtest."
)
st.caption("Educational project only — historical backtests do not guarantee future performance.")
