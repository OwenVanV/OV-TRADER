import { useMemo, useState } from "react";

import { DemoRunRecord } from "@/lib/types";

interface SampleDemoPanelProps {
  busy: boolean;
  latestDemo: DemoRunRecord | null;
  demos: DemoRunRecord[];
  onRunDemo: (options?: { initialBalance?: number; notes?: string }) => void;
}

export default function SampleDemoPanel({
  busy,
  latestDemo,
  demos,
  onRunDemo,
}: SampleDemoPanelProps) {
  const [initialBalance, setInitialBalance] = useState<number>(100);
  const [notes, setNotes] = useState<string>("");

  const historyRows = useMemo(() => {
    if (!latestDemo?.wallet?.history) return [];
    return latestDemo.wallet.history;
  }, [latestDemo?.wallet?.history]);

  return (
    <section className="card space-y-4">
      <header className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Sample Demo (Synthetic Market)</h2>
          <p className="muted text-sm">
            Runs the CLI quickstart scenario directly from the dashboard. Synthetic price data is
            piped through the alpha model and tracked in a virtual wallet.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
          <label className="flex flex-col text-sm font-medium">
            Initial balance
            <input
              className="input"
              type="number"
              min={1}
              step={1}
              value={initialBalance}
              onChange={(event) => setInitialBalance(Number(event.target.value))}
              disabled={busy}
            />
          </label>
          <label className="flex flex-col text-sm font-medium">
            Notes (optional)
            <input
              className="input"
              type="text"
              placeholder="Why run this demo?"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              disabled={busy}
            />
          </label>
          <button
            type="button"
            className="btn btn-primary self-start sm:self-auto"
            onClick={() => onRunDemo({
              initialBalance: Number.isFinite(initialBalance) ? initialBalance : undefined,
              notes: notes.trim() || undefined,
            })}
            disabled={busy}
          >
            {busy ? "Running..." : "Run sample demo"}
          </button>
        </div>
      </header>

      {latestDemo ? (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <h3 className="font-semibold">Virtual wallet</h3>
            <div className="rounded border border-slate-700 bg-slate-900/50 p-3 text-sm">
              <p className="font-medium">{latestDemo.wallet.summary}</p>
              <p className="text-xs text-slate-400">
                Started with {latestDemo.wallet.starting_balance.toFixed(2)} {latestDemo.wallet.label}
                . Final balance {latestDemo.wallet.balance.toFixed(2)} {latestDemo.wallet.label}.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-300">Balance history</h4>
              <ul className="mt-2 space-y-1 text-sm">
                {historyRows.map((row) => (
                  <li key={`${row.label}-${row.balance}`} className="flex justify-between">
                    <span className="text-slate-400">{row.label}</span>
                    <span className="font-mono">{row.balance.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="space-y-3">
            <h3 className="font-semibold">Analytics snapshots</h3>
            <div className="text-sm text-slate-300">
              <p>
                <span className="font-medium">Alpha signals:</span> {formatDataSize(latestDemo.alpha)}
              </p>
              <p>
                <span className="font-medium">Target weights:</span> {formatDataSize(latestDemo.weights)}
              </p>
              <p>
                <span className="font-medium">Portfolio returns:</span> {formatDataSize(latestDemo.portfolio_returns)}
              </p>
              <p className="text-xs text-slate-500">
                View detailed payloads in the API response or data explorer of your choice.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-300">Recent demo runs</h4>
              <ul className="mt-2 space-y-1 text-sm">
                {demos.map((demo) => (
                  <li key={demo.id} className="flex justify-between">
                    <span className="text-slate-400">
                      {new Date(demo.timestamp).toLocaleString()}
                    </span>
                    <span className="font-mono">
                      {demo.wallet.balance.toFixed(2)} {demo.wallet.label}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-400">
          No demo has been executed yet. Configure an initial balance and run the scenario to see the
          wallet evolve over the synthetic market sample.
        </p>
      )}
    </section>
  );
}

function formatDataSize(payload: Record<string, unknown> | undefined): string {
  if (!payload) return "n/a";
  const keys = Object.keys(payload);
  if (keys.length === 0) return "empty";
  return `${keys.length} keys`;
}
