"""Backtesting utilities leveraging Qlib."""

from __future__ import annotations

from dataclasses import dataclass

try:  # pragma: no cover - qlib optional
    import qlib  # type: ignore
    from qlib.contrib.strategy import TopkDropoutStrategy  # type: ignore
    from qlib.contrib.evaluate import risk_analysis as evaluate_risk  # type: ignore
except Exception:  # pragma: no cover
    qlib = None

from ..config import BacktestConfig, DataConfig
from ..data.dataset import DatasetBuilder
from ..data.features import FeatureBuilder
from ..strategies.alpha_mixture import AlphaModel


@dataclass
class BacktestResult:
    analysis: dict
    report: dict


class Backtester:
    def __init__(
        self,
        data_config: DataConfig,
        backtest_config: BacktestConfig,
        alpha_model: AlphaModel | None = None,
    ) -> None:
        self.data_config = data_config
        self.backtest_config = backtest_config
        self.alpha_model = alpha_model or AlphaModel()
        self.dataset_builder = DatasetBuilder(data_config)
        self.feature_builder = FeatureBuilder()

    def initialise(self) -> None:
        if qlib is None:  # pragma: no cover
            raise RuntimeError("qlib not installed")
        qlib.init(provider_uri=str(self.data_config.qlib_root), region="us")

    def run(self) -> BacktestResult:
        if qlib is None:
            raise RuntimeError("qlib not installed")
        self.initialise()
        dataset = self.dataset_builder.build()
        alpha_df = self.alpha_model.generate_signals(dataset, self.feature_builder)
        strategy = TopkDropoutStrategy(signal=alpha_df, topk=20, n_drop=5)
        analysis_df = strategy.fit()
        risk = evaluate_risk(analysis_df)
        return BacktestResult(analysis=risk, report={"positions": analysis_df})
