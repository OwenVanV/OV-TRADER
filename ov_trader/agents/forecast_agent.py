"""Forecasting agent combining Qlib models and optional LLM reasoning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

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
        context.shared_memory[self.name] = ForecastResult(
            scores=ranked.to_dict(),
            metadata={"latest_date": ranked.name if hasattr(ranked, "name") else "unknown"},
        )
        context.market_state.setdefault("alpha", ranked.to_dict())
        return context
