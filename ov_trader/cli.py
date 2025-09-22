"""Command line interface for OV Trader."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agents.decision_agent import DecisionAgent
from .agents.execution_agent import ExecutionAgent
from .agents.forecast_agent import ForecastAgent
from .agents.news_agent import NewsSentimentAgent
from .agents.orchestrator import Orchestrator
from .agents.portfolio_agent import PortfolioAgent
from .config import DEFAULT_CONFIG, TraderConfig
from .utils.logging import configure_logging


logger = configure_logging()


def load_config(path: Path | None) -> TraderConfig:
    if path is None:
        return DEFAULT_CONFIG
    data = json.loads(path.read_text())
    return TraderConfig.from_dict(data)


def build_orchestrator(config: TraderConfig) -> Orchestrator:
    news_agent = NewsSentimentAgent(config.llm_research)
    forecast_agent = ForecastAgent(config.data)
    decision_agent = DecisionAgent(config.llm_research)
    portfolio_agent = PortfolioAgent(config.risk)
    execution_agent = ExecutionAgent(config.execution)
    return Orchestrator(
        [news_agent, forecast_agent, decision_agent, portfolio_agent, execution_agent]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the OV Trader agent network")
    parser.add_argument("--config", type=Path, default=None, help="Path to JSON config file")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    orchestrator = build_orchestrator(config)

    logger.info("Starting trading cycle")
    context = orchestrator.run_cycle()
    logger.info("Cycle finished: %s", context.shared_memory)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
