import { NextResponse } from "next/server";

import { backendUnavailableResponse, proxyFetch } from "@/lib/server-proxy";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.text();

  try {
    const response = await proxyFetch("/runs", {
      method: "POST",
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
    return backendUnavailableResponse("Unable to start a trading cycle");
  }
}
