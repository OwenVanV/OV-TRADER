import { NextResponse } from "next/server";

import { createEmptyDashboard } from "@/lib/fallback";
import { getBackendBaseUrl, proxyFetch } from "@/lib/server-proxy";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await proxyFetch("/dashboard", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      const fallback = createEmptyDashboard(
        `Dashboard request failed with status ${response.status}.`,
      );
      return NextResponse.json(fallback, { status: 200 });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    const fallback = createEmptyDashboard(
      `Unable to reach the OV Trader API at ${getBackendBaseUrl()}. ` +
        "Start the FastAPI server with: uvicorn ov_trader.server.api:app --reload --port 8000.",
    );
    return NextResponse.json(fallback, { status: 200 });
  }
}
