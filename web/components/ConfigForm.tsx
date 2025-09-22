"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { TraderConfig } from "@/lib/types";

interface ConfigFormProps {
  initialConfig: TraderConfig;
  onSubmit: (config: TraderConfig) => void;
  busy?: boolean;
}

function cloneConfig(config: TraderConfig): TraderConfig {
  return JSON.parse(JSON.stringify(config)) as TraderConfig;
}

export default function ConfigForm({
  initialConfig,
  onSubmit,
  busy = false,
}: ConfigFormProps) {
  const [formState, setFormState] = useState<TraderConfig>(cloneConfig(initialConfig));

  useEffect(() => {
    setFormState(cloneConfig(initialConfig));
  }, [initialConfig]);

  const instrumentString = useMemo(
    () => formState.data.instruments.join(", "),
    [formState.data.instruments],
  );

  const handleFieldChange = (path: string, value: unknown) => {
    setFormState((prev) => {
      const next = cloneConfig(prev);
      const segments = path.split(".");
      let cursor: Record<string, unknown> = next as unknown as Record<string, unknown>;
      for (const segment of segments.slice(0, -1)) {
        if (cursor[segment] === undefined || cursor[segment] === null) {
          cursor[segment] = {};
        }
        cursor = cursor[segment] as Record<string, unknown>;
      }
      cursor[segments[segments.length - 1]] = value;
      return next;
    });
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit(formState);
  };

  return (
    <section className="card space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="card-title">Configuration</h2>
          <p className="muted text-sm">
            Adjust data sources, LLM preferences, execution connectivity, and risk tolerances. Changes apply to subsequent runs.
          </p>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={() => setFormState(cloneConfig(initialConfig))}
          className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-brand"
        >
          Reset
        </button>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-2">
        <fieldset className="space-y-4">
          <legend className="text-sm font-semibold text-slate-300">Data & research LLM</legend>
          <label className="block text-sm">
            <span className="text-slate-400">Qlib root</span>
            <input
              type="text"
              value={formState.data.qlib_root}
              onChange={(event) => handleFieldChange("data.qlib_root", event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Calendar</span>
            <input
              type="text"
              value={formState.data.calendar}
              onChange={(event) => handleFieldChange("data.calendar", event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Instruments</span>
            <input
              type="text"
              value={instrumentString}
              onChange={(event) =>
                handleFieldChange(
                  "data.instruments",
                  event.target.value
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean),
                )
              }
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <div className="grid grid-cols-2 gap-4">
            <label className="block text-sm">
              <span className="text-slate-400">Start</span>
              <input
                type="text"
                value={formState.data.start_time}
                onChange={(event) => handleFieldChange("data.start_time", event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">End</span>
              <input
                type="text"
                value={formState.data.end_time ?? ""}
                onChange={(event) => handleFieldChange("data.end_time", event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
          </div>
          <label className="block text-sm">
            <span className="text-slate-400">LLM provider</span>
            <input
              type="text"
              value={formState.llm_research.provider}
              onChange={(event) => handleFieldChange("llm_research.provider", event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">LLM model</span>
            <input
              type="text"
              value={formState.llm_research.model}
              onChange={(event) => handleFieldChange("llm_research.model", event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-sm font-semibold text-slate-300">Risk & execution</legend>
          <div className="grid grid-cols-2 gap-4">
            <label className="block text-sm">
              <span className="text-slate-400">Max leverage</span>
              <input
                type="number"
                step="0.1"
                value={formState.risk.max_leverage}
                onChange={(event) => handleFieldChange("risk.max_leverage", Number(event.target.value))}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Max drawdown</span>
              <input
                type="number"
                step="0.01"
                value={formState.risk.max_drawdown}
                onChange={(event) => handleFieldChange("risk.max_drawdown", Number(event.target.value))}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Position limit</span>
              <input
                type="number"
                step="0.01"
                value={formState.risk.position_limit}
                onChange={(event) => handleFieldChange("risk.position_limit", Number(event.target.value))}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Stop loss %</span>
              <input
                type="number"
                step="0.01"
                value={formState.risk.stop_loss_pct}
                onChange={(event) => handleFieldChange("risk.stop_loss_pct", Number(event.target.value))}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Take profit %</span>
              <input
                type="number"
                step="0.01"
                value={formState.risk.take_profit_pct}
                onChange={(event) => handleFieldChange("risk.take_profit_pct", Number(event.target.value))}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Rebalance frequency</span>
              <input
                type="text"
                value={formState.risk.rebalance_frequency}
                onChange={(event) => handleFieldChange("risk.rebalance_frequency", event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
          </div>

          <label className="block text-sm">
            <span className="text-slate-400">Execution host</span>
            <input
              type="text"
              value={formState.execution.server_host}
              onChange={(event) => handleFieldChange("execution.server_host", event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Execution port</span>
            <input
              type="number"
              value={formState.execution.server_port}
              onChange={(event) => handleFieldChange("execution.server_port", Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Client ID</span>
            <input
              type="text"
              value={formState.execution.client_id}
              onChange={(event) => handleFieldChange("execution.client_id", event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Accounts</span>
            <input
              type="text"
              value={formState.execution.account_aliases.join(", ")}
              onChange={(event) =>
                handleFieldChange(
                  "execution.account_aliases",
                  event.target.value
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean),
                )
              }
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>
        </fieldset>

        <fieldset className="space-y-4 lg:col-span-2">
          <legend className="text-sm font-semibold text-slate-300">Backtest defaults</legend>
          <div className="grid grid-cols-2 gap-4">
            <label className="block text-sm">
              <span className="text-slate-400">Benchmark</span>
              <input
                type="text"
                value={formState.backtest.benchmark}
                onChange={(event) => handleFieldChange("backtest.benchmark", event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Start</span>
              <input
                type="text"
                value={formState.backtest.start_time}
                onChange={(event) => handleFieldChange("backtest.start_time", event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">End</span>
              <input
                type="text"
                value={formState.backtest.end_time}
                onChange={(event) => handleFieldChange("backtest.end_time", event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Verbose</span>
              <select
                value={formState.backtest.verbose ? "true" : "false"}
                onChange={(event) => handleFieldChange("backtest.verbose", event.target.value === "true")}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              >
                <option value="true">Enabled</option>
                <option value="false">Disabled</option>
              </select>
            </label>
          </div>
          <label className="block text-sm">
            <span className="text-slate-400">Starting cash</span>
            <input
              type="number"
              value={formState.backtest.account.cash ?? 0}
              onChange={(event) =>
                handleFieldChange("backtest.account", {
                  ...formState.backtest.account,
                  cash: Number(event.target.value),
                })
              }
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </label>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={busy}
              className="rounded-lg bg-brand px-5 py-2 text-sm font-semibold text-white transition hover:bg-brand-light disabled:opacity-50"
            >
              {busy ? "Saving..." : "Save configuration"}
            </button>
          </div>
        </fieldset>
      </form>
    </section>
  );
}
