import { RunRecord, Decision } from "@/lib/types";

interface RunHistoryProps {
  runs: RunRecord[];
}

function extractAction(summaryDecision: RunRecord["summary"]["decision"]): string {
  if (!summaryDecision) {
    return "--";
  }
  if (typeof summaryDecision === "string") {
    return summaryDecision;
  }
  const decision = summaryDecision as Decision;
  return decision.action ? decision.action.toUpperCase() : "--";
}

export default function RunHistory({ runs }: RunHistoryProps) {
  if (!runs || runs.length === 0) {
    return (
      <section className="card h-full">
        <h2 className="card-title">Recent trading cycles</h2>
        <p className="muted text-sm">No live cycles recorded yet.</p>
      </section>
    );
  }

  return (
    <section className="card h-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="card-title">Recent trading cycles</h2>
        <span className="text-xs uppercase tracking-wide text-slate-500">
          Showing latest {Math.min(8, runs.length)}
        </span>
      </div>
      <ul className="space-y-3 text-sm">
        {runs.slice(0, 8).map((run) => (
          <li key={run.id} className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-semibold text-slate-100">
                  {new Date(run.timestamp).toLocaleString()}
                </p>
                <p className="text-xs text-slate-400">Cycle ID {run.id}</p>
              </div>
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                  run.status === "completed"
                    ? "bg-emerald-500/10 text-emerald-300"
                    : "bg-orange-500/10 text-orange-300"
                }`}
              >
                {run.status}
              </span>
            </div>
            <div className="mt-3 grid gap-3 lg:grid-cols-2">
              <div>
                <p className="text-xs uppercase text-slate-500">Action</p>
                <p className="text-slate-200">{extractAction(run.summary.decision)}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-slate-500">Orders</p>
                <p className="text-slate-200">{run.summary.orders.length}</p>
              </div>
            </div>
            {(run.summary.warnings.length > 0 || run.summary.errors.length > 0) && (
              <details className="mt-3">
                <summary className="cursor-pointer text-xs text-orange-300">Diagnostics</summary>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-orange-200">
                  {run.summary.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                  {run.summary.errors.map((error) => (
                    <li key={error}>{error}</li>
                  ))}
                </ul>
              </details>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
