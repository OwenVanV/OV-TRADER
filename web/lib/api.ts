import {
  DashboardData,
  RunRecord,
  BacktestRecord,
  TraderConfig,
  DemoRunRecord,
} from "./types";
import { createEmptyDashboard } from "./fallback";

function normaliseBase(base: string): string {
  return base.replace(/\/$/, "");
}

function getApiBases(): string[] {
  const isServer = typeof window === "undefined";
  const candidates = isServer
    ? [
        process.env.API_BASE_URL,
        process.env.NEXT_PUBLIC_API_BASE_URL,
        "http://127.0.0.1:8000",
        "http://localhost:8000",
      ]
    : [process.env.NEXT_PUBLIC_API_BASE_URL, "/api"];

  const bases: string[] = [];
  for (const value of candidates) {
    if (!value) continue;
    const normalised = normaliseBase(value);
    if (!bases.includes(normalised)) {
      bases.push(normalised);
    }
  }

  if (bases.length === 0) {
    bases.push(isServer ? "http://127.0.0.1:8000" : "/api");
  }

  return bases;
}

async function fetchFromApi(path: string, init?: RequestInit): Promise<Response> {
  const bases = getApiBases();
  let lastError: unknown = null;

  for (const base of bases) {
    try {
      const url = base.startsWith("http") ? `${base}${path}` : `${base}${path}`;
      return await fetch(url, init);
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError instanceof Error
    ? lastError
    : new Error("Unable to reach OV Trader API");
}

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
    const response = await fetchFromApi("/dashboard", {
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
  const response = await fetchFromApi("/runs", {
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
  const response = await fetchFromApi("/backtests", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  const data = await parseResponse<{ backtest: BacktestRecord }>(response);
  return data.backtest;
}

export async function saveConfig(config: TraderConfig): Promise<DashboardData["config"]> {
  const response = await fetchFromApi("/config", {
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

export async function runSampleDemo(body?: {
  initialBalance?: number;
  notes?: string;
}): Promise<DemoRunRecord> {
  const response = await fetchFromApi("/demo", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      initialBalance: body?.initialBalance,
      notes: body?.notes,
    }),
  });
  const data = await parseResponse<{ demo: DemoRunRecord }>(response);
  return data.demo;
}
