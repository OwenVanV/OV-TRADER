"""Base classes for multi-agent architecture."""

from __future__ import annotations

import abc
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency during tests
    from openai import AzureOpenAI, OpenAI  # type: ignore
except Exception:  # pragma: no cover
    AzureOpenAI = None  # type: ignore
    OpenAI = None  # type: ignore

from ..config import LLMConfig
from ..utils.logging import configure_logging


logger = configure_logging()


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
        """Call the configured model using the provided :class:`LLMConfig`."""

        provider = (self.llm_config.provider or "").lower()
        system_message = self.llm_config.extra.get(
            "system_message",
            "You are a highly capable financial analysis assistant.",
        )

        if provider in {"azure", "azure_openai"}:
            if AzureOpenAI is None:  # pragma: no cover - import guard for environments
                raise RuntimeError(
                    "The openai package with Azure OpenAI support is required to use "
                    "Azure-based models."
                )

            endpoint = self.llm_config.extra.get("azure_endpoint") or os.getenv(
                "AZURE_OPENAI_ENDPOINT"
            )
            api_key = self.llm_config.api_key or os.getenv("AZURE_OPENAI_API_KEY")
            api_version = self.llm_config.extra.get("azure_api_version") or os.getenv(
                "AZURE_OPENAI_API_VERSION",
            ) or "2024-02-15-preview"
            deployment = self.llm_config.extra.get("azure_deployment") or self.llm_config.model

            if not endpoint or not api_key or not deployment:
                raise RuntimeError(
                    "Azure OpenAI configuration incomplete. Ensure endpoint, API key, "
                    "and deployment/model names are provided."
                )

            client = AzureOpenAI(  # type: ignore[call-arg]
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version,
            )

            response = client.chat.completions.create(  # type: ignore[attr-defined]
                model=deployment,
                temperature=self.llm_config.temperature,
                max_tokens=self.llm_config.max_tokens,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
            )

            if not response.choices:
                return ""
            return response.choices[0].message.content or ""

        if provider == "openai":
            if OpenAI is None:  # pragma: no cover
                raise RuntimeError("The openai package is required to call OpenAI models.")

            api_key = self.llm_config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OpenAI API key missing. Set OPENAI_API_KEY or config.api_key")

            client = OpenAI(api_key=api_key)  # type: ignore[call-arg]
            response = client.chat.completions.create(  # type: ignore[attr-defined]
                model=self.llm_config.model,
                temperature=self.llm_config.temperature,
                max_tokens=self.llm_config.max_tokens,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
            )

            if not response.choices:
                return ""
            return response.choices[0].message.content or ""

        raise NotImplementedError(
            f"LLM provider '{self.llm_config.provider}' not supported."
        )

    def run(self, context: AgentContext) -> AgentContext:
        prompt = self.build_prompt(context)
        try:
            response = self.call_model(prompt)
        except NotImplementedError:
            response = "LLM integration not configured."
        except Exception as exc:  # pragma: no cover - network/runtime failures
            logger.exception("LLM call failed for agent %s: %s", self.name, exc)
            response = f"LLM call failed: {exc}"
        context.shared_memory[self.name] = response
        return context
