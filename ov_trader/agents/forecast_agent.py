"""Forecasting agent combining Qlib models and optional LLM reasoning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

import pandas as pd

try:  # pragma: no cover - qlib is heavy and optional
    import qlib  # type: ignore
except Exception:  # pragma: no cover - degrade gracefully when qlib missing
    qlib = None

from .base import AgentContext, BaseAgent
from ..config import DataConfig
from ..data.features import FeatureBuilder
from ..data.dataset import DatasetBuilder
from ..strategies.alpha_mixture import AlphaModel


@dataclass
class ForecastResult:
    scores: Dict[str, float]
    metadata: Dict[str, float]


class ForecastAgent(BaseAgent):
    """Train or load models using Qlib and produce forecasts."""

    def __init__(self, data_config: DataConfig, alpha_model: Optional[AlphaModel] = None) -> None:
        super().__init__("forecast")
        self.data_config = data_config
        self.alpha_model = alpha_model or AlphaModel()
        self.dataset_builder = DatasetBuilder(data_config)
        self.feature_builder = FeatureBuilder()

    def initialise_qlib(self) -> None:
        if qlib is None:  # pragma: no cover - require external dependency
            raise RuntimeError(
                "Qlib is not installed. Install microsoft/qlib to use the forecasting "
                "agent."
            )
        qlib.init(provider_uri=str(self.data_config.qlib_root), region="us")

    def run(self, context: AgentContext) -> AgentContext:
        if qlib is None:
            context.shared_memory[self.name] = {
                "error": "qlib not installed; forecasting skipped",
            }
            return context

        self.initialise_qlib()
        dataset = self.dataset_builder.build()
        alpha_df = self.alpha_model.generate_signals(dataset, self.feature_builder)
        ranked = alpha_df.iloc[-1].sort_values(ascending=False)
        market_snapshot = self._build_market_snapshot(ranked.index[:5])
        context.shared_memory[self.name] = ForecastResult(
            scores=ranked.to_dict(),
            metadata={"latest_date": ranked.name if hasattr(ranked, "name") else "unknown"},
        )
        context.market_state.setdefault("alpha", ranked.to_dict())
        if market_snapshot:
            context.market_state.setdefault("market_data", {}).update(market_snapshot)
        return context

    def _build_market_snapshot(self, instruments: Iterable[str]) -> Dict[str, Dict[str, float]]:
        features = getattr(self.alpha_model, "latest_features", None)
        if features is None or not isinstance(features, pd.DataFrame):
            return {}
        if features.empty:
            return {}
        if not isinstance(features.index, pd.MultiIndex):
            return {}

        index_names = list(features.index.names)
        try:
            instrument_level = index_names.index("instrument")
        except ValueError:
            instrument_level = len(index_names) - 1

        snapshot: Dict[str, Dict[str, float]] = {}
        for instrument in instruments:
            try:
                instrument_frame = features.xs(instrument, level=instrument_level)
            except Exception:  # pragma: no cover - qlib structure may vary
                continue

            if getattr(instrument_frame, "empty", False):
                continue

            if hasattr(instrument_frame, "iloc"):
                row = instrument_frame.iloc[-1]
            else:  # pragma: no cover - defensive fallback
                row = instrument_frame

            serialised = self._serialise_feature_row(row)
            if serialised:
                snapshot[str(instrument)] = serialised

        return snapshot

    def _serialise_feature_row(self, row: pd.Series) -> Dict[str, float]:
        metrics: Dict[str, float] = {}
        timestamp = getattr(row, "name", None)
        if timestamp is not None:
            metrics["as_of"] = str(timestamp)

        fields = [
            "close",
            "open",
            "high",
            "low",
            "volume",
            "ma_5",
            "ma_10",
            "ma_21",
            "momentum_5",
            "momentum_10",
            "momentum_21",
            "volatility_21",
        ]

        for field in fields:
            if field in row.index:
                value = row[field]
                if pd.notna(value):
                    metrics[field] = float(value)

        return metrics
