from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import fields, is_dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency for serialisation helpers
    import numpy as np
except Exception:  # pragma: no cover - numpy is optional at runtime
    np = None  # type: ignore

try:  # pragma: no cover - pandas optional for timestamp conversion
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore

from ..agents.base import AgentContext
from ..config import (
    DEFAULT_CONFIG,
    TraderConfig,
    apply_config_update,
    trader_config_to_dict,
)
from ..cli import build_orchestrator
from ..samples.quickstart import run_demo as run_quickstart_demo
from ..utils.logging import configure_logging
from ..utils.wallet import VirtualWallet
from ..backtesting.runner import Backtester


logger = configure_logging()


class TradingService:
    """High level façade exposing orchestration and backtesting utilities."""

    def __init__(self, config: TraderConfig | None = None) -> None:
        self._config: TraderConfig = config or DEFAULT_CONFIG
        self._history: List[Dict[str, Any]] = []
        self._backtests: List[Dict[str, Any]] = []
        self._last_context: AgentContext | None = None
        self._demo_runs: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Configuration management
    # ------------------------------------------------------------------
    def get_config(self) -> Dict[str, Any]:
        """Return the active configuration as a serialisable dictionary."""

        return trader_config_to_dict(self._config)

    def update_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Persist configuration changes and return the updated settings."""

        self._config = apply_config_update(self._config, payload)
        return self.get_config()

    # ------------------------------------------------------------------
    # Trading orchestration
    # ------------------------------------------------------------------
    def run_cycle(
        self,
        notes: str | None = None,
        override_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a full agent cycle and return a summary of the results."""

        config = (
            self._config
            if override_config is None
            else apply_config_update(self._config, override_config)
        )

        started = dt.datetime.now(dt.UTC)
        status = "completed"
        try:
            orchestrator = build_orchestrator(config)
            context = orchestrator.run_cycle()
        except Exception as exc:  # pragma: no cover - defensive catch
            logger.exception("Trading cycle failed: %s", exc)
            status = "failed"
            context = AgentContext(timestamp=started.isoformat())
            context.shared_memory["orchestrator"] = {"error": str(exc)}
        else:
            self._last_context = context

        record = self._context_to_record(
            context=context,
            status=status,
            notes=notes,
            config_snapshot=config,
        )
        record["duration"] = (dt.datetime.now(dt.UTC) - started).total_seconds()

        self._history.insert(0, record)
        self._history = self._history[:50]
        return record

    def list_runs(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Return the most recent trading cycles."""

        if limit is None:
            return list(self._history)
        return list(self._history[:limit])

    def latest_run(self) -> Dict[str, Any] | None:
        """Return the most recent run if available."""

        return self._history[0] if self._history else None

    # ------------------------------------------------------------------
    # Backtesting
    # ------------------------------------------------------------------
    def run_backtest(
        self,
        notes: str | None = None,
        override_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a backtest using the configured data pipeline."""

        config = (
            self._config
            if override_config is None
            else apply_config_update(self._config, override_config)
        )

        started = dt.datetime.now(dt.UTC)
        record: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "timestamp": started.isoformat(),
            "status": "completed",
            "config_snapshot": trader_config_to_dict(config),
        }
        if notes:
            record["notes"] = notes

        backtester = Backtester(config.data, config.backtest)
        try:
            result = backtester.run()
        except Exception as exc:  # pragma: no cover - optional deps may be missing
            logger.exception("Backtest failed: %s", exc)
            record["status"] = "failed"
            record["error"] = str(exc)
        else:
            record["result"] = {
                "analysis": self._serialise_value(result.analysis),
                "report": self._serialise_value(result.report),
            }

        record["duration"] = (dt.datetime.now(dt.UTC) - started).total_seconds()
        self._backtests.insert(0, record)
        self._backtests = self._backtests[:20]
        return record

    def list_backtests(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Return stored backtest results."""

        if limit is None:
            return list(self._backtests)
        return list(self._backtests[:limit])

    # ------------------------------------------------------------------
    # Demo / sample scenarios
    # ------------------------------------------------------------------
    def run_sample_demo(
        self,
        *,
        initial_balance: float = 100.0,
        notes: str | None = None,
    ) -> Dict[str, Any]:
        """Execute the quickstart demo and record the resulting wallet stats."""

        started = dt.datetime.now(dt.UTC)
        result = run_quickstart_demo(initial_balance=initial_balance)

        wallet: VirtualWallet = result["wallet"]

        record = {
            "id": str(uuid.uuid4()),
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            "duration": (dt.datetime.now(dt.UTC) - started).total_seconds(),
            "initial_balance": wallet.starting_balance,
            "wallet": {
                "label": wallet.label,
                "starting_balance": wallet.starting_balance,
                "balance": wallet.balance,
                "summary": wallet.summary(),
                "history": [
                    {"label": label, "balance": balance}
                    for label, balance in wallet.history
                ],
            },
            "alpha": self._serialise_value(result.get("alpha")),
            "weights": self._serialise_value(result.get("weights")),
            "portfolio_returns": self._serialise_value(
                result.get("portfolio_returns")
            ),
        }

        if notes:
            record["notes"] = notes

        self._demo_runs.insert(0, record)
        self._demo_runs = self._demo_runs[:10]
        return record

    def list_demo_runs(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Return previously executed demo simulations."""

        if limit is None:
            return list(self._demo_runs)
        return list(self._demo_runs[:limit])

    def latest_demo(self) -> Dict[str, Any] | None:
        """Return the most recent demo run if available."""

        return self._demo_runs[0] if self._demo_runs else None

    # ------------------------------------------------------------------
    # Dashboard helpers
    # ------------------------------------------------------------------
    def get_dashboard(self) -> Dict[str, Any]:
        """Return a combined payload suitable for dashboard rendering."""

        return {
            "config": self.get_config(),
            "latest_run": self.latest_run(),
            "runs": self.list_runs(limit=10),
            "backtests": self.list_backtests(limit=5),
            "latest_demo": self.latest_demo(),
            "demos": self.list_demo_runs(limit=5),
            "metrics": {
                "total_runs": len(self._history),
                "total_backtests": len(self._backtests),
                "total_demos": len(self._demo_runs),
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _context_to_record(
        self,
        *,
        context: AgentContext,
        status: str,
        notes: str | None,
        config_snapshot: TraderConfig,
    ) -> Dict[str, Any]:
        shared = self._serialise_value(context.shared_memory)
        market = self._serialise_value(context.market_state)
        summary = self._build_summary(shared, market)

        record: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "timestamp": context.timestamp or dt.datetime.now(dt.UTC).isoformat(),
            "status": status,
            "shared_memory": shared,
            "market_state": market,
            "summary": summary,
            "config_snapshot": trader_config_to_dict(config_snapshot),
        }
        if notes:
            record["notes"] = notes
        return record

    def _build_summary(
        self,
        shared: Dict[str, Any],
        market: Dict[str, Any],
    ) -> Dict[str, Any]:
        decision = market.get("llm_decision")

        llm_payload = shared.get("llm_decision")
        if not decision and isinstance(llm_payload, dict):
            decision = (
                llm_payload.get("parsed")
                or llm_payload.get("fallback")
                or llm_payload.get("response")
            )

        orders = shared.get("portfolio_orders")
        if not isinstance(orders, list):
            orders = []

        warnings: List[str] = []
        errors: List[str] = []
        for agent, payload in shared.items():
            if isinstance(payload, dict):
                if "warning" in payload:
                    warnings.append(f"{agent}: {payload['warning']}")
                if "error" in payload:
                    errors.append(f"{agent}: {payload['error']}")

        return {
            "decision": decision,
            "orders": orders,
            "warnings": warnings,
            "errors": errors,
        }

    def _serialise_value(self, value: Any) -> Any:
        if is_dataclass(value):
            result: Dict[str, Any] = {}
            for field_info in fields(value):
                result[field_info.name] = self._serialise_value(
                    getattr(value, field_info.name)
                )
            return result

        if isinstance(value, dict):
            return {key: self._serialise_value(val) for key, val in value.items()}

        if isinstance(value, (list, tuple, set)):
            return [self._serialise_value(item) for item in value]

        if isinstance(value, (dt.datetime, dt.date)):
            return value.isoformat()

        if pd is not None:
            if isinstance(value, pd.DataFrame):  # pragma: no cover - optional dependency
                return [
                    {
                        key: self._serialise_value(val)
                        for key, val in record.items()
                    }
                    for record in value.reset_index().to_dict(orient="records")
                ]
            if isinstance(value, pd.Timestamp):
                return value.isoformat()
            if isinstance(value, pd.Series):  # pragma: no cover - optional dependency
                return {
                    key: self._serialise_value(val) for key, val in value.to_dict().items()
                }
            if isinstance(value, pd.Index):  # pragma: no cover
                return [self._serialise_value(item) for item in value.tolist()]

        if np is not None:
            if isinstance(value, np.generic):  # pragma: no cover - depends on numpy
                return value.item()
            if isinstance(value, np.ndarray):  # pragma: no cover
                return [self._serialise_value(item) for item in value.tolist()]

        if isinstance(value, Decimal):
            return float(value)

        if hasattr(value, "isoformat"):
            try:
                return value.isoformat()
            except Exception:  # pragma: no cover - defensive
                pass

        return value
