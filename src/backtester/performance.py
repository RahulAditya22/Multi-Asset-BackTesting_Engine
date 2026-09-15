"""Portfolio performance statistics."""

from __future__ import annotations

import math

import pandas as pd


class PerformanceAnalyzer:
    """Calculate risk and return metrics from an equity curve."""

    def __init__(self, risk_free_rate: float = 0.0) -> None:
        if risk_free_rate < 0:
            raise ValueError("risk_free_rate cannot be negative")
        self.risk_free_rate = risk_free_rate

    def analyze(
        self, equity_curve: pd.Series, trades: list | None = None
    ) -> dict[str, float | int]:
        """Calculate total return, CAGR, Sharpe, drawdown, and trade statistics."""
        if equity_curve.empty or (equity_curve <= 0).any():
            raise ValueError("Equity curve must be non-empty and positive")
        curve = equity_curve.astype(float).sort_index()
        total_return = curve.iloc[-1] / curve.iloc[0] - 1
        years = max((curve.index[-1] - curve.index[0]).days / 365.25, 1 / 365.25)
        cagr = (curve.iloc[-1] / curve.iloc[0]) ** (1 / years) - 1
        returns = curve.pct_change().dropna()
        daily_rf = (1 + self.risk_free_rate) ** (1 / 252) - 1
        excess = returns - daily_rf
        sharpe = (
            math.sqrt(252) * excess.mean() / excess.std(ddof=1)
            if len(excess) > 1 and excess.std(ddof=1)
            else 0.0
        )
        running_max = curve.cummax()
        drawdown = curve / running_max - 1
        max_drawdown = float(drawdown.min())
        duration = self._max_drawdown_duration(drawdown)
        closed_trades = self._trade_pnls(trades or [])
        wins = [pnl for pnl in closed_trades if pnl > 0]
        losses = [pnl for pnl in closed_trades if pnl < 0]
        win_rate = len(wins) / len(closed_trades) if closed_trades else 0.0
        return {
            "total_return": float(total_return),
            "cagr": float(cagr),
            "sharpe_ratio": float(sharpe),
            "max_drawdown": max_drawdown,
            "max_drawdown_duration_days": int(duration),
            "win_rate": float(win_rate),
            "average_win": float(sum(wins) / len(wins)) if wins else 0.0,
            "average_loss": float(sum(losses) / len(losses)) if losses else 0.0,
            "trade_count": len(closed_trades),
            "ending_value": float(curve.iloc[-1]),
        }

    @staticmethod
    def _max_drawdown_duration(drawdown: pd.Series) -> int:
        """Return the longest calendar duration spent below a prior peak."""
        peak_date = drawdown.index[0]
        max_duration = 0
        for date, value in drawdown.items():
            if value == 0:
                peak_date = date
            else:
                max_duration = max(max_duration, (date - peak_date).days)
        return max_duration

    @staticmethod
    def _trade_pnls(trades: list) -> list[float]:
        """Convert alternating entry/exit trades into approximate net P&L."""
        pnls: list[float] = []
        entry: object | None = None
        for trade in trades:
            if trade.side in {"BUY", "SHORT"}:
                entry = trade
            elif trade.side in {"SELL", "COVER", "CLOSE"} and entry is not None:
                sign = 1 if entry.quantity > 0 else -1
                pnl = sign * (trade.price - entry.price) * abs(entry.quantity)
                pnl -= entry.transaction_cost + trade.transaction_cost
                pnls.append(pnl)
                entry = None
        return pnls
