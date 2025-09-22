import { DashboardData, RunRecord, BacktestRecord, TraderConfig } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const fallbackConfig: TraderConfig = {
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

function createEmptyDashboard(error?: string): DashboardData {
  return {
    config: cloneConfig(fallbackConfig),
    latest_run: null,
    runs: [],
    backtests: [],
    metrics: { total_runs: 0, total_backtests: 0 },
    error,
  };
}

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    throw new Error(text || response.statusText);
  }
  return text ? (JSON.parse(text) as T) : ({} as T);
}

export async function fetchDashboard(): Promise<DashboardData> {
  try {
    const response = await fetch(`${API_BASE}/dashboard`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Dashboard request failed: ${response.status}`);
    }
    const data = (await response.json()) as DashboardData;
    return data;
  } catch (error) {
    return createEmptyDashboard((error as Error).message);
  }
}

export async function runTradingCycle(body?: {
  notes?: string;
  overrideConfig?: Partial<TraderConfig>;
}): Promise<RunRecord> {
  const response = await fetch(`${API_BASE}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  const data = await parseResponse<{ run: RunRecord }>(response);
  return data.run;
}

export async function startBacktest(body?: {
  notes?: string;
  overrideConfig?: Partial<TraderConfig>;
}): Promise<BacktestRecord> {
  const response = await fetch(`${API_BASE}/backtests`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  const data = await parseResponse<{ backtest: BacktestRecord }>(response);
  return data.backtest;
}

export async function saveConfig(config: TraderConfig): Promise<DashboardData["config"]> {
  const response = await fetch(`${API_BASE}/config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(config),
  });
  const data = await parseResponse<{ config: TraderConfig }>(response);
  return data.config;
}

export async function refreshDashboard(): Promise<DashboardData> {
  return fetchDashboard();
}
