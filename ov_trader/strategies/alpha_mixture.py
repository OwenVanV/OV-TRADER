"""Alpha model blending classical factors and machine learning."""

from __future__ import annotations

import pandas as pd


class AlphaModel:
    """Placeholder alpha model that mixes multiple signals."""

    def __init__(self) -> None:
        self.latest_features: pd.DataFrame | None = None


    def generate_signals(self, dataset, feature_builder) -> pd.DataFrame:
        """Generate alpha scores for each instrument in the dataset.

        Parameters
        ----------
        dataset:
            Qlib dataset object.  Must support ``prepare`` returning a ``pd.DataFrame``.
        feature_builder:
            Instance of :class:`ov_trader.data.features.FeatureBuilder`.
        """

        raw = dataset.prepare("train")  # type: ignore[attr-defined]
        features = feature_builder.build(raw)
        self.latest_features = features
        features["alpha"] = (
            0.4 * features["momentum_10"]
            + 0.3 * features["momentum_21"]
            - 0.1 * features["volatility_21"]
            + 0.2 * (features["close"] / features["ma_10"] - 1)
        )
        pivoted = features["alpha"].unstack(level="instrument")
        return pivoted
