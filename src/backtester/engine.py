"""Event-driven portfolio backtesting engine."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from .strategies.base import Strategy

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Trade:
    """Represent one executed portfolio position change."""

    date: pd.Timestamp
    price: float
    quantity: float
    side: str
    transaction_cost: float


@dataclass
class BacktestResult:
    """Container for backtest portfolio history and trades."""

    equity_curve: pd.Series
    trades: list[Trade]
    positions: pd.Series


class Backtester:
    """Run a strategy without lookahead bias using next-bar execution."""

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        transaction_cost: float = 0.0005,
        slippage: float = 0.0005,
    ) -> None:
        if initial_capital <= 0 or transaction_cost < 0 or slippage < 0:
            raise ValueError("Capital must be positive and costs cannot be negative")
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage

    def run(self, data: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        """Execute a strategy against OHLCV data."""
        if data.empty or "Close" not in data:
            raise ValueError("Backtest data must be non-empty and contain Close")
        frame = data.sort_index().copy()
        signals = (
            strategy.generate_signals(frame)
            .reindex(frame.index)
            .fillna(0)
            .astype(int)
        )
        if not signals.isin([-1, 0, 1]).all():
            raise ValueError("Strategy signals must be -1, 0, or 1")

        cash = self.initial_capital
        quantity = 0.0
        trades: list[Trade] = []
        equity: list[float] = []
        positions: list[float] = []
        pending_target = 0

        for index, row in frame.iterrows():
            price = float(row["Close"])
            target = pending_target
            current_direction = 0 if quantity == 0 else (1 if quantity > 0 else -1)

            if target != current_direction:
                if quantity != 0:
                    execution_price = price * (
                        1 - self.slippage if quantity > 0 else 1 + self.slippage
                    )
                    fee = abs(quantity * execution_price) * self.transaction_cost
                    cash += quantity * execution_price - fee
                    trades.append(
                        Trade(
                            index,
                            execution_price,
                            -quantity,
                            "SELL" if quantity > 0 else "COVER",
                            fee,
                        )
                    )
                    quantity = 0.0

                if target != 0:
                    execution_price = price * (
                        1 + self.slippage if target > 0 else 1 - self.slippage
                    )
                    quantity = target * (
                        cash / (execution_price * (1 + self.transaction_cost))
                    )
                    fee = abs(quantity * execution_price) * self.transaction_cost
                    cash -= quantity * execution_price + fee
                    trades.append(
                        Trade(
                            index,
                            execution_price,
                            quantity,
                            "BUY" if target > 0 else "SHORT",
                            fee,
                        )
                    )

            equity.append(cash + quantity * price)
            positions.append(quantity)
            pending_target = int(signals.loc[index])

        if quantity != 0:
            index = frame.index[-1]
            price = float(frame["Close"].iloc[-1])
            execution_price = price * (
                1 - self.slippage if quantity > 0 else 1 + self.slippage
            )
            fee = abs(quantity * execution_price) * self.transaction_cost
            cash += quantity * execution_price - fee
            trades.append(
                Trade(
                    index,
                    execution_price,
                    -quantity,
                    "SELL" if quantity > 0 else "COVER",
                    fee,
                )
            )
            quantity = 0.0
            equity[-1] = cash
            positions[-1] = 0.0
            LOGGER.info("Forced final liquidation at %s", index)

        return BacktestResult(
            equity_curve=pd.Series(equity, index=frame.index, name="equity"),
            trades=trades,
            positions=pd.Series(positions, index=frame.index, name="position"),
        )
