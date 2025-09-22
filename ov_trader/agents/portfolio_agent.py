"""Portfolio construction and risk management agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from .base import AgentContext, BaseAgent
from .execution_agent import Order
from ..config import RiskConfig


@dataclass
class PortfolioState:
    positions: Dict[str, float]
    cash: float


class PortfolioAgent(BaseAgent):
    """Translate alpha scores into executable orders."""

    def __init__(self, risk_config: RiskConfig, target_gross_exposure: float = 1.0) -> None:
        super().__init__("portfolio")
        self.risk_config = risk_config
        self.target_gross_exposure = target_gross_exposure

    def run(self, context: AgentContext) -> AgentContext:
        alpha = context.market_state.get("alpha")
        if not alpha:
            context.shared_memory[self.name] = {"warning": "no alpha data"}
            return context

        scores = np.array(list(alpha.values()))
        tickers = list(alpha.keys())
        if scores.sum() == 0:
            weights = np.repeat(1 / len(scores), len(scores))
        else:
            weights = scores / np.abs(scores).sum()

        orders: List[Order] = []
        for ticker, weight in zip(tickers, weights):
            orders.append(
                Order(
                    symbol=ticker,
                    quantity=float(weight * self.target_gross_exposure),
                    side="buy" if weight >= 0 else "sell",
                )
            )

        context.shared_memory["portfolio_orders"] = orders
        context.shared_memory[self.name] = {
            "target_weights": dict(zip(tickers, weights)),
        }
        return context
