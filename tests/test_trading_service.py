from ov_trader.server import TradingService


def test_trading_service_updates_config():
    service = TradingService()
    updated = service.update_config({"risk": {"max_leverage": 3.0}})
    assert updated["risk"]["max_leverage"] == 3.0


def test_trading_service_run_cycle_creates_history():
    service = TradingService()
    result = service.run_cycle(notes="unit-test")

    assert result["id"]
    assert "shared_memory" in result
    assert result["status"] in {"completed", "failed"}
    history = service.list_runs()
    assert history and history[0]["id"] == result["id"]


def test_trading_service_backtest_handles_missing_dependencies():
    service = TradingService()
    record = service.run_backtest(notes="unit-test")

    assert record["status"] in {"completed", "failed"}
    assert "config_snapshot" in record


def test_dashboard_payload_contains_expected_keys():
    service = TradingService()
    service.run_cycle()
    service.run_backtest()
    payload = service.get_dashboard()

    assert {"config", "latest_run", "runs", "backtests", "metrics"} <= payload.keys()
