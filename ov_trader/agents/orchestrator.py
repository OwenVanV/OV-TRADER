"""Coordinator for running the multi-agent pipeline."""

from __future__ import annotations

import datetime as dt
from typing import Iterable, List

from .base import AgentContext, BaseAgent
from ..utils.logging import configure_logging


logger = configure_logging()


class Orchestrator:
    """Execute a sequence of agents and collect their outputs."""

    def __init__(self, agents: Iterable[BaseAgent]) -> None:
        self.agents: List[BaseAgent] = list(agents)

    def run_cycle(self) -> AgentContext:
        context = AgentContext(timestamp=dt.datetime.now(dt.UTC).isoformat())
        for agent in self.agents:
            logger.info("Running agent: %s", agent.name)
            context = agent.run(context)
        return context
