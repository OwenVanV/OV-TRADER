import { NextResponse } from "next/server";

const DEFAULT_BACKEND = "http://localhost:8000";

function normalizeBase(url: string): string {
  return url.replace(/\/$/, "");
}

const backendBase = normalizeBase(
  process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_BACKEND,
);

export function getBackendBaseUrl(): string {
  return backendBase;
}

export async function proxyFetch(path: string, init?: RequestInit): Promise<Response> {
  const target = `${backendBase}${path}`;
  return fetch(target, init);
}

export function backendUnavailableResponse(context: string) {
  const message = `${context}. The OV Trader API at ${backendBase} is not reachable. ` +
    `Start it with: uvicorn ov_trader.server.api:app --reload --port 8000`;
  return NextResponse.json({ error: message }, { status: 503 });
}
