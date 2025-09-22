import { BacktestRecord } from "@/lib/types";

interface BacktestPanelProps {
  backtests: BacktestRecord[];
}

function renderMetrics(record: BacktestRecord): Array<[string, string]> {
  const metrics: Array<[string, string]> = [];
  const analysis = (record.result?.analysis ?? {}) as Record<string, unknown>;
  const keys = Object.keys(analysis);
  for (const key of keys.slice(0, 4)) {
    const value = analysis[key];
    if (value === null || value === undefined) {
      continue;
    }
    if (typeof value === "number") {
      metrics.push([key, value.toFixed(4)]);
    } else {
      metrics.push([key, String(value)]);
    }
  }
  return metrics;
}

export default function BacktestPanel({ backtests }: BacktestPanelProps) {
  if (!backtests || backtests.length === 0) {
    return (
      <section className="card h-full">
        <h2 className="card-title">Backtesting</h2>
        <p className="muted text-sm">Run a backtest to populate performance analytics.</p>
      </section>
    );
  }

  return (
    <section className="card h-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="card-title">Backtesting</h2>
        <span className="text-xs uppercase tracking-wide text-slate-500">
          Showing latest {Math.min(5, backtests.length)}
        </span>
      </div>
      <ul className="space-y-3 text-sm">
        {backtests.slice(0, 5).map((backtest) => {
          const metrics = renderMetrics(backtest);
          return (
            <li key={backtest.id} className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-slate-100">
                    {new Date(backtest.timestamp).toLocaleString()}
                  </p>
                  <p className="text-xs text-slate-400">Backtest ID {backtest.id}</p>
                </div>
                <span
                  className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                    backtest.status === "completed"
                      ? "bg-emerald-500/10 text-emerald-300"
                      : "bg-orange-500/10 text-orange-300"
                  }`}
                >
                  {backtest.status}
                </span>
              </div>
              {backtest.error && (
                <p className="mt-2 text-xs text-orange-300">{backtest.error}</p>
              )}
              {metrics.length > 0 && (
                <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-slate-200">
                  {metrics.map(([key, value]) => (
                    <div key={key}>
                      <p className="uppercase text-slate-500">{key}</p>
                      <p>{value}</p>
                    </div>
                  ))}
                </div>
              )}
              {backtest.result?.report && (
                <details className="mt-3 text-xs">
                  <summary className="cursor-pointer text-slate-400">View raw report</summary>
                  <pre className="mt-2 max-h-48 overflow-y-auto rounded bg-slate-900/80 p-3">
                    {JSON.stringify(backtest.result.report, null, 2)}
                  </pre>
                </details>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
