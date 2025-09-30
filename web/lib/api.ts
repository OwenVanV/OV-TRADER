import { DashboardData, RunRecord, BacktestRecord, TraderConfig } from "./types";
import { createEmptyDashboard } from "./fallback";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api").replace(/\/$/, "");

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    try {
      const parsed = text ? JSON.parse(text) : null;
      if (parsed && typeof parsed.error === "string") {
        throw new Error(parsed.error);
      }
    } catch (error) {
      if (error instanceof SyntaxError) {
        // Ignore JSON parse issues; fall back to raw text below.
      } else {
        throw error instanceof Error ? error : new Error(String(error));
      }
    }
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
