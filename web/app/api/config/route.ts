import { NextResponse } from "next/server";

import { fallbackConfig } from "@/lib/fallback";
import { backendUnavailableResponse, proxyFetch } from "@/lib/server-proxy";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await proxyFetch("/config", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    const text = await response.text();
    if (!response.ok) {
      return NextResponse.json(
        { error: text || response.statusText, config: fallbackConfig },
        { status: response.status },
      );
    }

    const data = text ? JSON.parse(text) : {};
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ config: fallbackConfig }, { status: 200 });
  }
}

export async function PUT(request: Request) {
  const body = await request.text();

  try {
    const response = await proxyFetch("/config", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body,
    });

    const text = await response.text();
    if (!response.ok) {
      return NextResponse.json(
        { error: text || response.statusText },
        { status: response.status },
      );
    }

    const data = text ? JSON.parse(text) : {};
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return backendUnavailableResponse("Unable to save configuration");
  }
}
