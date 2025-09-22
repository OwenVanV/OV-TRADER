from __future__ import annotations

import json

from ov_trader.agents.base import AgentContext
from ov_trader.agents.decision_agent import DecisionAgent
from ov_trader.config import LLMConfig


class _StubDecisionAgent(DecisionAgent):
    def call_model(self, prompt: str) -> str:  # pragma: no cover - deterministic stub
        payload = {
            "symbol": "AAPL",
            "action": "buy",
            "confidence": 82,
            "target_weight": 0.35,
            "thesis": "Stub thesis",
            "risk_notes": "Stub risks",
            "analysis": [
                "Alpha is strong.",
                "News is positive.",
            ],
        }
        return json.dumps(payload)


class _ErrorDecisionAgent(DecisionAgent):
    def call_model(self, prompt: str) -> str:  # pragma: no cover - deterministic failure
        raise RuntimeError("LLM unavailable")


def _build_context() -> AgentContext:
    context = AgentContext(timestamp="2024-06-01T00:00:00Z")
    context.market_state["alpha"] = {"AAPL": 0.42, "MSFT": 0.21, "TSLA": -0.15}
    context.market_state["market_data"] = {
        "AAPL": {
            "as_of": "2024-05-31",
            "close": 189.21,
            "ma_10": 185.5,
            "momentum_10": 0.034,
        }
    }
    context.shared_memory["news_sentiment"] = "Overall bullish tone driven by product launch."
    return context


def test_decision_agent_builds_prompt_with_required_sections():
    config = LLMConfig(provider="azure", model="gpt-5")
    agent = DecisionAgent(config)
    prompt = agent.build_prompt(_build_context())

    assert "Qlib alpha signals" in prompt
    assert "News and sentiment overview" in prompt
    assert "Respond with a JSON object" in prompt
    assert "AAPL" in prompt  # focus symbol should appear in prompt


def test_decision_agent_parses_successful_model_response():
    config = LLMConfig(provider="azure", model="gpt-5")
    agent = _StubDecisionAgent(config)
    context = _build_context()

    updated = agent.run(context)
    decision = updated.market_state["llm_decision"]

    assert decision["action"] == "buy"
    assert updated.shared_memory["llm_decision"]["parsed"]["symbol"] == "AAPL"


def test_decision_agent_uses_fallback_when_model_fails():
    config = LLMConfig(provider="azure", model="gpt-5")
    agent = _ErrorDecisionAgent(config)
    context = _build_context()

    updated = agent.run(context)
    fallback = updated.market_state["llm_decision"]

    assert fallback["symbol"] == "AAPL"
    assert updated.shared_memory["llm_decision"]["error"] == "LLM unavailable"
