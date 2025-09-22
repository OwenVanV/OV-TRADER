"use client";

import { useMemo, useState } from "react";

import { RunRecord, Order, Decision } from "@/lib/types";

interface AgentInsightsProps {
  latestRun: RunRecord | null;
  onRefresh: () => Promise<unknown> | void;
}

function isDecision(value: unknown): value is Decision {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function formatOrder(order: Order, index: number): string {
  const quantityValue = Number(order.quantity ?? 0);
  const quantity = Number.isFinite(quantityValue) ? quantityValue.toFixed(4) : "0";
  return `${index + 1}. ${order.side?.toUpperCase() ?? "HOLD"} ${order.symbol} (${quantity})`;
}

function renderAnalysis(analysis: unknown): string[] {
  if (Array.isArray(analysis)) {
    return analysis.map((item) => String(item));
  }
  if (typeof analysis === "string") {
    return [analysis];
  }
  return [];
}

export default function AgentInsights({ latestRun, onRefresh }: AgentInsightsProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  const decision = useMemo(() => {
    if (!latestRun) {
      return null;
    }
    const rawDecision = latestRun.summary?.decision;
    if (isDecision(rawDecision)) {
      return rawDecision;
    }
    if (typeof rawDecision === "string") {
      try {
        const parsed = JSON.parse(rawDecision) as Decision;
        if (isDecision(parsed)) {
          return parsed;
        }
      } catch (error) {
        return { thesis: rawDecision } as Decision;
      }
    }
    return null;
  }, [latestRun]);

  const orders = useMemo(() => latestRun?.summary?.orders ?? [], [latestRun?.summary?.orders]);

  if (!latestRun) {
    return (
      <section className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="card-title">Latest agent synthesis</h2>
            <p className="muted text-sm">Trigger a trading cycle to populate the dashboard.</p>
          </div>
          <button
            type="button"
            onClick={() => onRefresh?.()}
            className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-brand"
          >
            Refresh
          </button>
        </div>
      </section>
    );
  }

  const sharedEntries = Object.entries(latestRun.shared_memory);

  return (
    <section className="card space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="card-title">Latest agent synthesis</h2>
          <p className="muted text-sm">
            Cycle ID {latestRun.id} · {new Date(latestRun.timestamp).toLocaleString()} · Status: {latestRun.status}
          </p>
        </div>
        <button
          type="button"
          onClick={() => onRefresh?.()}
          className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-brand"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300">Decision summary</h3>
          {decision ? (
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-100">
              <p className="font-semibold text-slate-200">
                {decision.symbol ?? "N/A"} · {decision.action?.toUpperCase() ?? "HOLD"}
              </p>
              <p className="muted">
                Confidence: {decision.confidence ?? "--"} · Target weight: {decision.target_weight ?? "--"}
              </p>
              {decision.thesis && <p className="mt-2 text-slate-200">{decision.thesis}</p>}
              {decision.risk_notes && (
                <p className="mt-2 text-xs text-orange-300">Risk: {decision.risk_notes}</p>
              )}
              {decision.analysis && (
                <ul className="mt-3 list-disc space-y-1 pl-4 text-xs text-slate-300">
                  {renderAnalysis(decision.analysis).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <p className="rounded-lg border border-dashed border-slate-800 p-4 text-sm text-slate-400">
              The decision agent did not return a structured recommendation.
            </p>
          )}
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300">Portfolio instructions</h3>
          {orders.length > 0 ? (
            <ul className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-100">
              {orders.map((order, index) => (
                <li key={`${order.symbol}-${index}`}>{formatOrder(order, index)}</li>
              ))}
            </ul>
          ) : (
            <p className="rounded-lg border border-dashed border-slate-800 p-4 text-sm text-slate-400">
              No executable orders were generated for this cycle.
            </p>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-300">Agent transcripts</h3>
        <div className="divide-y divide-slate-800 rounded-lg border border-slate-800 bg-slate-950/40">
          {sharedEntries.map(([agent, payload]) => {
            const isOpen = expanded === agent;
            return (
              <div key={agent} className="p-4">
                <button
                  type="button"
                  onClick={() => setExpanded(isOpen ? null : agent)}
                  className="flex w-full items-center justify-between text-left text-sm font-semibold text-slate-200"
                >
                  <span>{agent}</span>
                  <span className="text-xs text-slate-400">{isOpen ? "Hide" : "Show"}</span>
                </button>
                {isOpen && (
                  <pre className="mt-3 max-h-64 overflow-y-auto rounded bg-slate-900/80 p-3 text-xs text-slate-200">
                    {JSON.stringify(payload, null, 2)}
                  </pre>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
