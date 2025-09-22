"""Agent responsible for gathering qualitative signals."""

from __future__ import annotations

import datetime as dt
from typing import Iterable, List

from .base import AgentContext, LLMEnabledAgent
from ..config import LLMConfig


class NewsSentimentAgent(LLMEnabledAgent):
    """Collect news headlines and summarise them with an LLM."""

    def __init__(self, llm_config: LLMConfig, sources: Iterable[str] | None = None) -> None:
        super().__init__("news_sentiment", llm_config)
        self.sources = list(sources or ["https://newsapi.org/", "https://cryptopanic.com/"])

    def fetch_headlines(self) -> List[str]:
        """Fetch the latest headlines.

        The implementation is intentionally left as a stub because most data sources
        require API keys.  Replace this method with calls to your preferred news
        aggregation service.
        """

        now = dt.datetime.now(dt.timezone.utc)
        return [
            f"[{now:%Y-%m-%d %H:%M}] Placeholder headline about macro environment",
            f"[{now:%Y-%m-%d %H:%M}] Placeholder crypto regulation update",
        ]

    def build_prompt(self, context: AgentContext) -> str:
        headlines = self.fetch_headlines()
        joined = "\n".join(f"- {headline}" for headline in headlines)
        return (
            "You are a global macro strategist. Analyse the following headlines and "
            "produce:\n"
            "1. A sentiment score between -1 (bearish) and +1 (bullish).\n"
            "2. Key catalysts relevant to equities and crypto.\n"
            "3. A list of tickers that could be impacted.\n"
            f"\nHeadlines:\n{joined}\n"
        )
