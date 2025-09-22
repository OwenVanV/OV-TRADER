"""FastAPI application exposing OV Trader's orchestration endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from .service import TradingService


class ConfigPayload(BaseModel):
    """Payload used when updating configuration via the API."""

    model_config = ConfigDict(extra="allow")

    data: Optional[Dict[str, Any]] = None
    llm_research: Optional[Dict[str, Any]] = None
    llm_forecasting: Optional[Dict[str, Any]] = None
    execution: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None
    backtest: Optional[Dict[str, Any]] = None


class RunRequest(BaseModel):
    """Request body for triggering a trading cycle."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    notes: Optional[str] = None
    override_config: Optional[Dict[str, Any]] = Field(default=None, alias="overrideConfig")


class BacktestRequest(BaseModel):
    """Request body for launching a backtest."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    notes: Optional[str] = None
    override_config: Optional[Dict[str, Any]] = Field(default=None, alias="overrideConfig")


service = TradingService()

app = FastAPI(title="OV Trader API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
async def root() -> Dict[str, Any]:
    """Return basic information about the API."""

    return {
        "name": "OV Trader API",
        "version": "0.1.0",
        "endpoints": ["/dashboard", "/runs", "/config", "/backtests"],
    }


@app.get("/health", tags=["meta"])
async def health() -> Dict[str, str]:
    """Health probe used for readiness checks."""

    return {"status": "ok"}


@app.get("/dashboard", tags=["dashboard"])
async def dashboard() -> Dict[str, Any]:
    """Return an aggregated dashboard payload."""

    return service.get_dashboard()


@app.get("/config", tags=["config"])
async def get_config() -> Dict[str, Any]:
    """Fetch the current configuration."""

    return {"config": service.get_config()}


@app.put("/config", tags=["config"])
async def update_config(payload: ConfigPayload) -> Dict[str, Any]:
    """Update persisted configuration values."""

    data = payload.model_dump(exclude_none=True)
    updated = service.update_config(data)
    return {"config": updated}


@app.get("/runs", tags=["trading"])
async def list_runs(limit: int = 20) -> Dict[str, Any]:
    """Return trading cycle history."""

    return {"runs": service.list_runs(limit=limit)}


@app.post("/runs", tags=["trading"])
async def trigger_run(request: RunRequest) -> Dict[str, Any]:
    """Trigger a new trading cycle."""

    record = await run_in_threadpool(
        lambda: service.run_cycle(
            notes=request.notes,
            override_config=request.override_config,
        )
    )
    return {"run": record}


@app.get("/runs/{run_id}", tags=["trading"])
async def get_run(run_id: str) -> Dict[str, Any]:
    """Retrieve a specific trading run by identifier."""

    for run in service.list_runs():
        if run["id"] == run_id:
            return {"run": run}
    raise HTTPException(status_code=404, detail="Run not found")


@app.post("/backtests", tags=["backtesting"])
async def trigger_backtest(request: BacktestRequest) -> Dict[str, Any]:
    """Execute a backtest."""

    record = await run_in_threadpool(
        lambda: service.run_backtest(
            notes=request.notes,
            override_config=request.override_config,
        )
    )
    return {"backtest": record}


@app.get("/backtests", tags=["backtesting"])
async def list_backtests(limit: int = 10) -> Dict[str, Any]:
    """Return previously executed backtests."""

    return {"backtests": service.list_backtests(limit=limit)}
