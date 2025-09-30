export interface DataConfig {
  qlib_root: string;
  calendar: string;
  instruments: string[];
  start_time: string;
  end_time?: string | null;
  auto_update?: boolean;
}

export interface LLMConfig {
  provider: string;
  model: string;
  api_key?: string | null;
  temperature?: number;
  max_tokens?: number;
  extra?: Record<string, unknown>;
}

export interface ExecutionConfig {
  server_host: string;
  server_port: number;
  client_id: string;
  account_aliases: string[];
}

export interface RiskConfig {
  max_leverage: number;
  max_drawdown: number;
  position_limit: number;
  stop_loss_pct: number;
  take_profit_pct: number;
  rebalance_frequency: string;
}

export interface BacktestConfig {
  benchmark: string;
  start_time: string;
  end_time: string;
  account: Record<string, number>;
  verbose: boolean;
}

export interface TraderConfig {
  data: DataConfig;
  llm_research: LLMConfig;
  llm_forecasting?: LLMConfig | null;
  execution: ExecutionConfig;
  risk: RiskConfig;
  backtest: BacktestConfig;
}

export interface Order {
  symbol: string;
  quantity: number;
  side: string;
  order_type?: string;
  price?: number | null;
}

export interface Decision {
  symbol?: string;
  action?: string;
  confidence?: number;
  target_weight?: number;
  thesis?: string;
  risk_notes?: string;
  analysis?: unknown;
}

export interface RunSummary {
  decision?: Decision | string | null;
  orders: Order[];
  warnings: string[];
  errors: string[];
}

export interface RunRecord {
  id: string;
  timestamp: string;
  status: string;
  summary: RunSummary;
  shared_memory: Record<string, unknown>;
  market_state: Record<string, unknown>;
  duration?: number;
  notes?: string;
  config_snapshot: TraderConfig;
}

export interface BacktestResultPayload {
  analysis?: Record<string, unknown>;
  report?: Record<string, unknown>;
}

export interface BacktestRecord {
  id: string;
  timestamp: string;
  status: string;
  result?: BacktestResultPayload;
  error?: string;
  notes?: string;
  duration?: number;
  config_snapshot: TraderConfig;
}

export interface DashboardMetrics {
  total_runs: number;
  total_backtests: number;
  total_demos?: number;
}

export interface WalletSnapshot {
  label: string;
  starting_balance: number;
  balance: number;
  summary: string;
  history: { label: string; balance: number }[];
}

export interface DemoRunRecord {
  id: string;
  timestamp: string;
  duration?: number;
  initial_balance: number;
  wallet: WalletSnapshot;
  alpha?: Record<string, unknown>;
  weights?: Record<string, unknown>;
  portfolio_returns?: Record<string, unknown>;
  notes?: string;
}

export interface DashboardData {
  config: TraderConfig;
  latest_run: RunRecord | null;
  runs: RunRecord[];
  backtests: BacktestRecord[];
  latest_demo: DemoRunRecord | null;
  demos: DemoRunRecord[];
  metrics: DashboardMetrics;
  error?: string;
}
