"""Self-contained demo scenario that runs without external data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..data.features import FeatureBuilder
from ..strategies.alpha_mixture import AlphaModel
from ..utils.wallet import VirtualWallet


def _generate_price_frame(days: int = 90) -> pd.DataFrame:
    """Return a tidy price frame for a handful of synthetic tickers."""

    rng = np.random.default_rng(42)
    tickers = ["AAPL", "MSFT", "GOOG"]
    start_price = np.array([180.0, 330.0, 130.0])
    dates = pd.date_range("2023-01-02", periods=days, freq="B")

    records = []
    prices = start_price.copy()
    for ts in dates:
        daily_move = rng.normal(0.0008, 0.015, size=len(tickers))
        prices *= 1 + daily_move
        for ticker, price, move in zip(tickers, prices, daily_move):
            records.append(
                {
                    "instrument": ticker,
                    "datetime": ts,
                    "close": price,
                    "return": move,
                }
            )
    frame = pd.DataFrame.from_records(records).set_index(["datetime", "instrument"]).sort_index()
    return frame


def run_demo(initial_balance: float = 100.0) -> dict:
    """Execute an end-to-end sample backtest and return the results."""

    prices = _generate_price_frame()
    feature_builder = FeatureBuilder()
    alpha_model = AlphaModel()

    dataset = SimpleDataset(prices)
    alpha_scores = alpha_model.generate_signals(dataset, feature_builder)

    returns = prices["return"].unstack(level="instrument").loc[alpha_scores.index]
    weights = _weights_from_alpha(alpha_scores)
    portfolio_returns = (weights * returns).sum(axis=1)

    wallet = VirtualWallet(starting_balance=initial_balance)
    for timestamp, value in portfolio_returns.items():
        wallet.apply_return(value, timestamp.strftime("%Y-%m-%d"))

    return {
        "wallet": wallet,
        "alpha": alpha_scores,
        "weights": weights,
        "portfolio_returns": portfolio_returns,
    }


def _weights_from_alpha(alpha: pd.DataFrame) -> pd.DataFrame:
    """Convert alpha scores into normalised long-only portfolio weights."""

    clipped = alpha.clip(lower=0)
    weight_sum = clipped.sum(axis=1)
    weights = clipped.div(weight_sum.replace(0, np.nan), axis=0).fillna(1.0 / clipped.shape[1])
    return weights


class SimpleDataset:
    """Minimal dataset wrapper exposing the ``prepare`` API used by AlphaModel."""

    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = frame.reset_index().set_index(["datetime", "instrument"])

    def prepare(self, _split: str) -> pd.DataFrame:
        return self._frame


if __name__ == "__main__":  # pragma: no cover
    results = run_demo()
    wallet = results["wallet"]
    print(wallet.summary())
    print("Final balance history:")
    for label, balance in wallet.history:
        print(f"  {label}: {balance:.2f}")
