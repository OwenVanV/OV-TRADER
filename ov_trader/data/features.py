"""Feature engineering helpers."""

from __future__ import annotations

import pandas as pd


class FeatureBuilder:
    """Generate factor features required by the alpha model."""

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add simple technical indicators.

        The default implementation provides a handful of moving averages and
        momentum indicators; customise as required for your strategy universe.
        """

        augmented = df.copy()
        for window in (5, 10, 21):
            augmented[f"ma_{window}"] = df["close"].rolling(window).mean()
            augmented[f"momentum_{window}"] = df["close"].pct_change(window)
        augmented["volatility_21"] = df["close"].pct_change().rolling(21).std()
        augmented.dropna(inplace=True)
        return augmented
