"use client";

import { useCallback, useMemo, useState, useTransition } from "react";

import {
  refreshDashboard,
  runTradingCycle,
  saveConfig,
  startBacktest,
} from "@/lib/api";
import { DashboardData, TraderConfig } from "@/lib/types";
import AgentInsights from "./AgentInsights";
import BacktestPanel from "./BacktestPanel";
import ConfigForm from "./ConfigForm";
import RunHistory from "./RunHistory";
import TradingControls from "./TradingControls";

interface DashboardClientProps {
  initialData: DashboardData;
}

export default function DashboardClient({ initialData }: DashboardClientProps) {
  const [data, setData] = useState<DashboardData>(initialData);
  const [statusMessage, setStatusMessage] = useState<string | null>(
    initialData.error ?? null,
  );
  const [isPending, startTransition] = useTransition();

  const metrics = useMemo(() => data.metrics ?? { total_runs: 0, total_backtests: 0 }, [data.metrics]);

  const refresh = useCallback(async () => {
    const next = await refreshDashboard();
    setData(next);
    return next;
  }, []);

  const handleRun = useCallback(
    (notes?: string) => {
      startTransition(async () => {
        setStatusMessage("Executing trading cycle...");
        try {
          await runTradingCycle(notes ? { notes } : undefined);
          const next = await refresh();
          const timestamp = next.latest_run?.timestamp
            ? new Date(next.latest_run.timestamp).toLocaleString()
            : new Date().toLocaleString();
          setStatusMessage(`Trading cycle completed at ${timestamp}.`);
        } catch (error) {
          setStatusMessage(`Trading cycle failed: ${(error as Error).message}`);
        }
      });
    },
    [refresh],
  );

  const handleBacktest = useCallback(
    (notes?: string) => {
      startTransition(async () => {
        setStatusMessage("Running backtest...");
        try {
          await startBacktest(notes ? { notes } : undefined);
          await refresh();
          setStatusMessage("Backtest finished.");
        } catch (error) {
          setStatusMessage(`Backtest failed: ${(error as Error).message}`);
        }
      });
    },
    [refresh],
  );

  const handleConfigSave = useCallback(
    (config: TraderConfig) => {
      startTransition(async () => {
        setStatusMessage("Saving configuration...");
        try {
          const updated = await saveConfig(config);
          setData((prev) => ({ ...prev, config: updated }));
          setStatusMessage("Configuration saved.");
        } catch (error) {
          setStatusMessage(`Configuration update failed: ${(error as Error).message}`);
        }
      });
    },
    [],
  );

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">OV Trader Command Center</h1>
          <p className="muted">
            Monitor agent insights, trigger fresh trading cycles, and validate strategies via backtests.
          </p>
        </div>
        <div className="text-sm text-right text-slate-400">
          <p>Total cycles: {metrics.total_runs}</p>
          <p>Backtests: {metrics.total_backtests}</p>
        </div>
      </header>

      {statusMessage && (
        <div className="card border-brand/40 bg-brand/10 text-sm">
          {statusMessage}
        </div>
      )}

      <TradingControls
        busy={isPending}
        onRun={handleRun}
        onBacktest={handleBacktest}
        onRefresh={() => {
          startTransition(async () => {
            setStatusMessage("Refreshing dashboard...");
            try {
              await refresh();
              setStatusMessage("Dashboard up to date.");
            } catch (error) {
              setStatusMessage(`Refresh failed: ${(error as Error).message}`);
            }
          });
        }}
      />

      <AgentInsights latestRun={data.latest_run} onRefresh={refresh} />

      <div className="grid gap-6 lg:grid-cols-2">
        <RunHistory runs={data.runs} />
        <BacktestPanel backtests={data.backtests} />
      </div>

      <ConfigForm
        busy={isPending}
        initialConfig={data.config}
        onSubmit={handleConfigSave}
      />
    </div>
  );
}
