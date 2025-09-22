"""LLM-based decision agent that synthesises quantitative and qualitative data."""

from __future__ import annotations

import json
import re
from typing import Dict, Iterable, Optional

from .base import AgentContext, LLMEnabledAgent
from ..config import LLMConfig
from ..utils.logging import configure_logging


logger = configure_logging()


class DecisionAgent(LLMEnabledAgent):
    """Use an Azure OpenAI (GPT-5) style model to issue trading actions."""

    def __init__(self, llm_config: LLMConfig, top_n: int = 5) -> None:
        super().__init__("llm_decision", llm_config)
        self.top_n = top_n

    def build_prompt(self, context: AgentContext) -> str:  # type: ignore[override]
        alpha_scores: Dict[str, float] = context.market_state.get("alpha", {}) or {}
        market_data: Dict[str, Dict[str, float]] = context.market_state.get("market_data", {}) or {}
        news_summary = context.shared_memory.get("news_sentiment")

        focus_symbol = self._select_focus_symbol(alpha_scores, market_data)
        alpha_section = self._format_alpha_section(alpha_scores)
        market_section = self._format_market_section(focus_symbol, market_data)
        news_section = news_summary if news_summary else "No news sentiment summary available."

        instructions = (
            "Follow this deliberate decision process:\n"
            "1. Quantitative review: interpret the Qlib alpha signals, highlighting magnitude and sign.\n"
            "2. Market structure: analyse the recent price and technical snapshot to infer trend, momentum, and volatility.\n"
            "3. News context: examine the qualitative summary for catalysts and risks.\n"
            "4. Synthesis: integrate the evidence to choose a single action (buy, sell, hold) with a recommended position size."
        )

        return (
            "You are GPT-5, an advanced trading strategist embedded in a portfolio research simulator. "
            "Use the provided market intelligence to recommend an action that aims to beat the broad market in simulation.\n"
            f"Timestamp: {context.timestamp or 'unknown'}\n"
            f"Focus symbol: {focus_symbol or 'not enough data'}\n\n"
            f"### Qlib alpha signals (top {self.top_n})\n{alpha_section or 'No alpha data available.'}\n\n"
            f"### Market feature snapshot for {focus_symbol or 'N/A'}\n{market_section}\n\n"
            f"### News and sentiment overview\n{news_section}\n\n"
            f"{instructions}\n\n"
            "When reasoning, explicitly reference numbers from the datasets above. "
            "Respond with a JSON object containing the following keys:\n"
            "- \"symbol\": ticker analysed.\n"
            "- \"action\": one of \"buy\", \"sell\", or \"hold\".\n"
            "- \"confidence\": integer between 0 and 100.\n"
            "- \"target_weight\": recommended portfolio weight between -1.0 and 1.0.\n"
            "- \"thesis\": concise synthesis (~3 sentences) combining alpha, market data, and news.\n"
            "- \"risk_notes\": explicit downside risks or invalidation points.\n"
            "- \"analysis\": bullet-style breakdown of how each data source influenced the decision.\n"
            "Return *only* the JSON object with no additional commentary."
        )

    def run(self, context: AgentContext) -> AgentContext:  # type: ignore[override]
        prompt = self.build_prompt(context)
        try:
            raw_response = self.call_model(prompt)
        except Exception as exc:  # pragma: no cover - network failures
            logger.exception("Decision agent failed to query LLM: %s", exc)
            fallback = self._fallback_decision(context)
            context.shared_memory[self.name] = {
                "prompt": prompt,
                "error": str(exc),
                "fallback": fallback,
            }
            if fallback:
                context.market_state["llm_decision"] = fallback
            return context

        parsed = self._parse_response(raw_response)
        payload = {
            "prompt": prompt,
            "response": raw_response,
            "parsed": parsed,
        }

        if parsed:
            context.market_state["llm_decision"] = parsed
        else:
            fallback = self._fallback_decision(context)
            if fallback:
                payload["fallback"] = fallback
                context.market_state["llm_decision"] = fallback

        context.shared_memory[self.name] = payload
        return context

    def _select_focus_symbol(
        self,
        scores: Dict[str, float],
        market_data: Dict[str, Dict[str, float]],
    ) -> Optional[str]:
        if not scores:
            return None

        available = [symbol for symbol in scores if symbol in market_data]
        if available:
            return max(available, key=lambda symbol: abs(scores[symbol]))

        return max(scores.items(), key=lambda item: abs(item[1]))[0]

    def _format_alpha_section(self, scores: Dict[str, float]) -> str:
        if not scores:
            return ""

        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top = ordered[: self.top_n]
        bottom: Iterable[tuple[str, float]] = []
        if len(ordered) > self.top_n:
            bottom = ordered[-self.top_n :]

        lines = ["Top ranked signals:"]
        for symbol, score in top:
            lines.append(f"- {symbol}: {score:+.4f}")

        bottom = list(bottom)
        if bottom:
            lines.append("Lowest ranked signals:")
            for symbol, score in bottom:
                lines.append(f"- {symbol}: {score:+.4f}")

        return "\n".join(lines)

    def _format_market_section(
        self,
        symbol: Optional[str],
        market_data: Dict[str, Dict[str, float]],
    ) -> str:
        if not symbol or symbol not in market_data:
            return "No detailed market snapshot available."

        snapshot = market_data[symbol]
        lines = []
        as_of = snapshot.get("as_of")
        if as_of:
            lines.append(f"As of: {as_of}")

        for key, value in snapshot.items():
            if key == "as_of":
                continue
            lines.append(f"{key}: {value:.4f}")

        return "\n".join(lines) if lines else "No detailed market snapshot available."

    def _parse_response(self, response: str) -> Optional[Dict[str, object]]:
        if not response:
            return None

        candidate = self._extract_json_block(response)
        if candidate is None:
            return None

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return None

        if isinstance(parsed, dict):
            return parsed
        return None

    def _extract_json_block(self, text: str) -> Optional[str]:
        cleaned = text.strip()
        if not cleaned:
            return None

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9]*\n", "", cleaned)
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return match.group(0)

        if cleaned.startswith("{") and cleaned.endswith("}"):
            return cleaned
        return None

    def _fallback_decision(self, context: AgentContext) -> Optional[Dict[str, object]]:
        scores: Dict[str, float] = context.market_state.get("alpha", {}) or {}
        if not scores:
            return None

        symbol, score = max(scores.items(), key=lambda item: abs(item[1]))
        if score > 0:
            action = "buy"
        elif score < 0:
            action = "sell"
        else:
            action = "hold"

        confidence = min(100, int(abs(score) * 100))
        target_weight = max(min(float(score), 1.0), -1.0)

        return {
            "symbol": symbol,
            "action": action,
            "confidence": confidence,
            "target_weight": target_weight,
            "thesis": "Fallback derived from quantitative alpha score in absence of GPT-5 output.",
            "risk_notes": "LLM reasoning unavailable; rely on systematic risk controls.",
            "analysis": [
                "Alpha score magnitude used as proxy for conviction.",
                "No qualitative news incorporated due to missing LLM response.",
            ],
        }
