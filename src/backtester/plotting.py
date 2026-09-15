"""Plotly charts for backtest results."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def equity_curve_chart(equity_curve: pd.Series) -> go.Figure:
    """Create an interactive equity curve chart."""
    figure = go.Figure(
        go.Scatter(
            x=equity_curve.index, y=equity_curve.values, mode="lines", name="Equity"
        )
    )
    figure.update_layout(
        title="Equity Curve", xaxis_title="Date", yaxis_title="Portfolio Value"
    )
    return figure


def drawdown_chart(equity_curve: pd.Series) -> go.Figure:
    """Create an interactive drawdown chart."""
    drawdown = equity_curve / equity_curve.cummax() - 1
    figure = go.Figure(
        go.Scatter(x=drawdown.index, y=drawdown.values, mode="lines", name="Drawdown")
    )
    figure.update_layout(title="Drawdown", xaxis_title="Date", yaxis_title="Drawdown")
    return figure


def price_signal_chart(data: pd.DataFrame, signals: pd.Series) -> go.Figure:
    """Create a price chart with target-position changes marked."""
    changes = signals.diff().fillna(0)
    figure = go.Figure(
        go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close")
    )
    buys = data.index[changes > 0]
    sells = data.index[changes < 0]
    figure.add_trace(
        go.Scatter(
            x=buys,
            y=data.loc[buys, "Close"],
            mode="markers",
            name="Buy",
            marker_symbol="triangle-up",
            marker_size=10,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=sells,
            y=data.loc[sells, "Close"],
            mode="markers",
            name="Sell",
            marker_symbol="triangle-down",
            marker_size=10,
        )
    )
    figure.update_layout(title="Price & Signals", xaxis_title="Date", yaxis_title="Price")
    return figure
