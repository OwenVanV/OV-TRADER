"""Base classes for multi-agent architecture."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..config import LLMConfig


@dataclass
class AgentContext:
    """Context object shared between agents during a decision cycle."""

    timestamp: Optional[str] = None
    market_state: Dict[str, Any] = field(default_factory=dict)
    shared_memory: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(abc.ABC):
    """Abstract base class for all agents."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abc.abstractmethod
    def run(self, context: AgentContext) -> AgentContext:
        """Execute the agent logic and mutate the shared context."""


class LLMEnabledAgent(BaseAgent):
    """Agent that can call out to a large language model."""

    def __init__(self, name: str, llm_config: LLMConfig) -> None:
        super().__init__(name)
        self.llm_config = llm_config

    def build_prompt(self, context: AgentContext) -> str:
        """Construct a textual prompt for the LLM.

        Subclasses should override this to include relevant market data.
        """

        return (
            "You are an expert financial analyst. Provide a concise summary of the "
            "current market state and actionable insights."
        )

    def call_model(self, prompt: str) -> str:
        """Call the configured model.

        This function intentionally avoids direct API calls because credentials are
        environment-specific.  Integrators can supply a concrete implementation via
        dependency injection.
        """

        raise NotImplementedError(
            "No LLM integration configured. Provide an implementation that calls the "
            "desired provider (e.g. OpenAI GPT-4, future GPT-5, TimeGen1)."
        )

    def run(self, context: AgentContext) -> AgentContext:
        prompt = self.build_prompt(context)
        try:
            response = self.call_model(prompt)
        except NotImplementedError:
            response = "LLM integration not configured."
        context.shared_memory[self.name] = response
        return context
