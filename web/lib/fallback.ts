import { DashboardData, TraderConfig } from "./types";

export const fallbackConfig: TraderConfig = {
  data: {
    qlib_root: "",
    calendar: "USNYSE",
    instruments: [],
    start_time: "",
    end_time: "",
    auto_update: false,
  },
  llm_research: {
    provider: "",
    model: "",
    temperature: 0.2,
    max_tokens: 0,
    extra: {},
  },
  llm_forecasting: null,
  execution: {
    server_host: "",
    server_port: 0,
    client_id: "",
    account_aliases: [],
  },
  risk: {
    max_leverage: 0,
    max_drawdown: 0,
    position_limit: 0,
    stop_loss_pct: 0,
    take_profit_pct: 0,
    rebalance_frequency: "",
  },
  backtest: {
    benchmark: "",
    start_time: "",
    end_time: "",
    account: {},
    verbose: false,
  },
};

function cloneConfig(config: TraderConfig): TraderConfig {
  return JSON.parse(JSON.stringify(config)) as TraderConfig;
}

export function createEmptyDashboard(error?: string): DashboardData {
  return {
    config: cloneConfig(fallbackConfig),
    latest_run: null,
    runs: [],
    backtests: [],
    latest_demo: null,
    demos: [],
    metrics: { total_runs: 0, total_backtests: 0, total_demos: 0 },
    error,
  };
}
