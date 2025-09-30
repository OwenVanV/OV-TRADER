"""Bridge between strategy decisions and brokerage execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

try:  # pragma: no cover
    from pytrader_api import Pytrader_API  # type: ignore
except Exception:  # pragma: no cover
    Pytrader_API = None

from .base import AgentContext, BaseAgent
from ..config import PyTraderConfig
from ..utils.logging import configure_logging


logger = configure_logging()


@dataclass
class Order:
    symbol: str
    quantity: float
    side: str  # "buy" or "sell"
    order_type: str = "market"
    price: float | None = None


class ExecutionAgent(BaseAgent):
    """Execute orders using PyTrader."""

    def __init__(self, config: PyTraderConfig) -> None:
        super().__init__("execution")
        self.config = config
        self.client = None

    def connect(self) -> None:
        if Pytrader_API is None:
            raise RuntimeError(
                "PyTrader API is not installed. Install the private pytrader_api package "
                "to enable live execution (see README section 'Optional: install PyTrader')."
            )
        self.client = Pytrader_API()
        self.client.connect(
            self.config.server_host,
            self.config.server_port,
            self.config.client_id,
        )

    def ensure_connection(self) -> None:
        if self.client is None:
            self.connect()

    def submit_orders(self, orders: Iterable[Order]) -> List[Dict[str, float]]:
        self.ensure_connection()
        results = []
        for order in orders:
            logger.info("Executing %s %s x%s", order.side, order.symbol, order.quantity)
            if self.client is None:
                raise RuntimeError("Execution client not connected")
            result = self.client.order_market(symbol=order.symbol, volume=order.quantity)
            results.append(result)
        return results

    def run(self, context: AgentContext) -> AgentContext:
        orders = context.shared_memory.get("portfolio_orders", [])
        if not orders:
            logger.info("No orders to execute")
            return context

        try:
            execution_results = self.submit_orders(orders)
        except Exception as exc:  # pragma: no cover - network errors
            logger.exception("Order execution failed: %s", exc)
            context.shared_memory[self.name] = {"error": str(exc)}
            return context

        context.shared_memory[self.name] = execution_results
        return context
