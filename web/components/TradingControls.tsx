"use client";

import { useState } from "react";

interface TradingControlsProps {
  busy?: boolean;
  onRun: (notes?: string) => void;
  onBacktest: (notes?: string) => void;
  onRefresh: () => void;
}

export default function TradingControls({
  busy = false,
  onRun,
  onBacktest,
  onRefresh,
}: TradingControlsProps) {
  const [runNotes, setRunNotes] = useState<string>("");
  const [backtestNotes, setBacktestNotes] = useState<string>("");

  return (
    <section className="card space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="card-title">Live trading orchestration</h2>
          <p className="muted text-sm">
            Launch the full multi-agent decision cycle and capture optional guidance for the LLM decision layer.
          </p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          disabled={busy}
          className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 transition hover:border-brand"
        >
          Refresh data
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <label className="block text-sm font-medium text-slate-300" htmlFor="run-notes">
            Trading cycle notes
          </label>
          <textarea
            id="run-notes"
            value={runNotes}
            onChange={(event) => setRunNotes(event.target.value)}
            placeholder="E.g. emphasise large-cap tech or reduce crypto exposure."
            className="h-24 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
          />
          <button
            type="button"
            onClick={() => onRun(runNotes.trim() || undefined)}
            disabled={busy}
            className="w-full rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-light disabled:opacity-50"
          >
            {busy ? "Running..." : "Run trading cycle"}
          </button>
        </div>

        <div className="space-y-3">
          <label className="block text-sm font-medium text-slate-300" htmlFor="backtest-notes">
            Backtest memo
          </label>
          <textarea
            id="backtest-notes"
            value={backtestNotes}
            onChange={(event) => setBacktestNotes(event.target.value)}
            placeholder="E.g. evaluate 2020-2022 drawdowns or tweak factor blend."
            className="h-24 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
          />
          <button
            type="button"
            onClick={() => onBacktest(backtestNotes.trim() || undefined)}
            disabled={busy}
            className="w-full rounded-lg border border-brand px-4 py-2 text-sm font-semibold text-brand transition hover:bg-brand/10 disabled:opacity-50"
          >
            {busy ? "Processing..." : "Run backtest"}
          </button>
        </div>
      </div>
    </section>
  );
}
