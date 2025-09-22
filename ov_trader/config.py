"""Configuration objects for the OV Trader system.

The project makes heavy use of dataclasses to keep configuration explicit and
serialisable.  Where possible, configuration values are namespaced per module so
that individual components can be swapped without editing other parts of the
system.

Note on large language models
------------------------------
The original specification references models such as GPT-5 and TimeGen1.  These
models are not publicly available at the time of writing; consequently the
configuration below exposes generic interfaces so that future models can be
plugged in easily once released.  During development you can integrate any
available provider (e.g. OpenAI's GPT-4) by supplying the relevant settings via
the :class:`LLMConfig`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass(slots=True)
class LLMConfig:
    """Settings for large language model usage inside the agent network."""

    provider: str
    """Identifier of the LLM provider (e.g. ``"openai"``, ``"anthropic"``)."""

    model: str
    """The model name, such as ``"gpt-4-turbo"``.  Placeholder for future GPT-5."""

    api_key: Optional[str] = None
    """API key used to authenticate against the provider."""

    temperature: float = 0.2
    max_tokens: int = 2048
    extra: Dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class DataConfig:
    """Configuration for data ingestion and caching."""

    qlib_root: Path
    """Location where Qlib data is stored (``qlib.init`` uses this path)."""

    calendar: str = "USNYSE"
    instruments: Iterable[str] = ("SP500",)
    start_time: str = "2015-01-01"
    end_time: Optional[str] = None
    auto_update: bool = False


@dataclass(slots=True)
class PyTraderConfig:
    """Settings for the PyTrader execution bridge."""

    server_host: str = "127.0.0.1"
    server_port: int = 33333
    client_id: str = "ov-trader"
    account_aliases: List[str] = field(default_factory=lambda: ["td", "wealthsimple"])


@dataclass(slots=True)
class RiskConfig:
    """Configuration for risk management and portfolio constraints."""

    max_leverage: float = 2.0
    max_drawdown: float = 0.2
    position_limit: float = 0.1
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.15
    rebalance_frequency: str = "1d"


@dataclass(slots=True)
class BacktestConfig:
    """Parameters used when running backtests via Qlib."""

    benchmark: str = "SH000300"
    start_time: str = "2018-01-01"
    end_time: str = "2023-12-31"
    account: Dict[str, float] = field(default_factory=lambda: {"cash": 1_000_000})
    verbose: bool = True


@dataclass(slots=True)
class TraderConfig:
    """Top-level configuration for the trading system."""

    data: DataConfig
    llm_research: LLMConfig
    llm_forecasting: Optional[LLMConfig] = None
    execution: PyTraderConfig = field(default_factory=PyTraderConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "TraderConfig":
        """Create a :class:`TraderConfig` from nested dictionaries."""

        data_cfg = dict(data.get("data", {}))
        qlib_root = data_cfg.get("qlib_root")
        if qlib_root is not None and not isinstance(qlib_root, Path):
            data_cfg["qlib_root"] = Path(qlib_root)
        llm_research_cfg = data.get("llm_research", {})
        llm_forecasting_cfg = data.get("llm_forecasting")
        execution_cfg = data.get("execution", {})
        risk_cfg = data.get("risk", {})
        backtest_cfg = data.get("backtest", {})

        return cls(
            data=DataConfig(**data_cfg),
            llm_research=LLMConfig(**llm_research_cfg),
            llm_forecasting=LLMConfig(**llm_forecasting_cfg) if llm_forecasting_cfg else None,
            execution=PyTraderConfig(**execution_cfg) if execution_cfg else PyTraderConfig(),
            risk=RiskConfig(**risk_cfg) if risk_cfg else RiskConfig(),
            backtest=BacktestConfig(**backtest_cfg) if backtest_cfg else BacktestConfig(),
        )


DEFAULT_CONFIG = TraderConfig(
    data=DataConfig(qlib_root=Path.home() / "qlib_data"),
    llm_research=LLMConfig(provider="openai", model="gpt-4o-mini"),
)
"""A sensible default configuration for experimentation."""


def _serialise_dataclass(value: Any) -> Any:
    """Recursively convert dataclass instances into serialisable dictionaries."""

    if is_dataclass(value):
        result: Dict[str, Any] = {}
        for field_info in fields(value):
            result[field_info.name] = _serialise_dataclass(getattr(value, field_info.name))
        return result

    if isinstance(value, dict):
        return {key: _serialise_dataclass(val) for key, val in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_serialise_dataclass(item) for item in value]

    if isinstance(value, Path):
        return str(value)

    return value


def trader_config_to_dict(config: TraderConfig) -> Dict[str, Any]:
    """Convert a :class:`TraderConfig` into a plain dictionary."""

    return _serialise_dataclass(config)


def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deep merged copy of ``base`` updated with ``update``."""

    merged = dict(base)
    for key, value in update.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def apply_config_update(config: TraderConfig, update: Dict[str, Any]) -> TraderConfig:
    """Return a new configuration with ``update`` applied on top of ``config``."""

    if not update:
        return config

    current = trader_config_to_dict(config)
    merged = _deep_merge(current, update)
    return TraderConfig.from_dict(merged)
