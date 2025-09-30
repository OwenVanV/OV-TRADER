# OV Trader

Multi-agent trading research framework inspired by advanced quantitative funds.
The project integrates [Microsoft Qlib](https://github.com/microsoft/qlib) for
high quality data, embraces modular alpha research pipelines, and provides hooks
for LLM-powered research agents.

> **Disclaimer**
> This repository ships with research tooling only.  Automated trading against
> live brokerage accounts carries material financial risk.  You must obtain
> appropriate regulatory approvals and thoroughly test via paper trading before
> deploying.  Models such as "GPT-5" or "TimeGen1" mentioned in the request are
> not publicly available at the time of writing; integration points are provided
> so that future models can be slotted in without altering the core codebase.

## Features

- Multi-agent architecture consisting of:
  - **NewsSentimentAgent** – aggregates qualitative information and summarises it
    via an LLM.
  - **ForecastAgent** – consumes Qlib datasets and produces alpha signals.
  - **DecisionAgent** – queries Azure OpenAI (configured for future GPT-5
    deployments) to synthesise alpha, price action, and news into a final
    portfolio instruction.
  - **PortfolioAgent** – converts alpha signals into target allocations with
    simple risk constraints.
  - **ExecutionAgent** – bridges to brokers via [PyTrader](https://github.com/MetaQuotes/MetaTrader5-API).
- Configurable data ingestion via Qlib bundles for equities and crypto.
- Backtesting harness using Qlib's `TopkDropoutStrategy`.
- CLI entry point for running a full decision cycle.
- FastAPI control plane with REST endpoints for triggering live cycles, inspecting
  agent telemetry, and launching backtests.
- Next.js dashboard for orchestrating trades, editing configuration, and
  reviewing multi-agent outputs.

## Quick start

1. Install system dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Required packages include `microsoft-qlib`, `pytrader`, `pandas`, `numpy`, and
   an LLM client (e.g. `openai`).  Many of these libraries require Python 3.10+.

2. Download the Qlib US data bundle:

   ```bash
   qlib_init.py download_data --region us --target_dir ~/qlib_data
   ```

3. Configure LLM credentials via environment variables or a JSON config file.
   Example configuration (`config.json`):

   ```json
   {
     "data": {
       "qlib_root": "~/qlib_data",
       "calendar": "USNYSE",
       "instruments": ["SP500"],
       "start_time": "2015-01-01"
     },
     "llm_research": {
       "provider": "openai",
       "model": "gpt-4o-mini",
       "api_key": "sk-..."
     }
   }
   ```

   The value supplied in `model` should match the Azure deployment name configured
   for your GPT-5-capable endpoint.

   To enable Azure OpenAI deployments (e.g. a future GPT-5 capable endpoint) the
   configuration can be extended with the deployment details:

   ```json
   {
     "llm_research": {
       "provider": "azure",
       "model": "gpt-5",
       "api_key": "<azure-openai-key>",
       "extra": {
         "azure_endpoint": "https://your-resource.openai.azure.com/",
         "azure_api_version": "2024-02-15-preview",
         "azure_deployment": "gpt5-trading",
         "system_message": "You are GPT-5, an elite trading strategist."
       }
     }
   }
   ```

4. Run a decision cycle:

   ```bash
   python -m ov_trader.cli --config config.json
   ```

   The CLI logs the output of each agent and records cross-agent communication via
   the shared memory in :class:`~ov_trader.agents.base.AgentContext`.

## Web dashboard

The repository ships with a lightweight API server and Next.js front end for
interactive experimentation.

### Shared environment configuration

A repository level `.env` file is provided so that both the FastAPI backend and
the Next.js frontend read the same configuration.  Update the placeholder
values (for example the API keys) before running the stack locally.

### Quick start (PowerShell)

On Windows you can start both services with a single command:

```powershell
./start.ps1
```

The script loads variables from `.env`, ensures the required tools are
available, and watches both processes.  Use `-NoBackend` or `-NoFrontend` to
skip either service.

### Start the API service

```bash
uvicorn ov_trader.server.api:app --reload --port 8000
```

The FastAPI layer exposes endpoints such as `/dashboard`, `/runs`, `/config`, and
`/backtests`.  These surface the same orchestration flow as the CLI while
persisting run history and configuration updates in memory.

### Start the Next.js client

```bash
cd web
npm install
npm run dev
```

The dashboard expects the API at `http://localhost:8000` by default.  Override
the base URL via `NEXT_PUBLIC_API_BASE_URL` when deploying to another host.
From the UI you can:

- Trigger new agent cycles with optional natural-language guidance.
- Launch backtests and inspect the resulting risk statistics.
- Review per-agent transcripts alongside portfolio instructions.
- Edit data, risk, execution, and LLM configuration values without touching
  configuration files.

## Extending the system

- Replace `NewsSentimentAgent.fetch_headlines` with connections to paid data feeds
  or alternative scrapers.  The resulting text will be summarised by your
  configured LLM.
- Implement `LLMEnabledAgent.call_model` with your actual API calls.  The base
  class raises :class:`NotImplementedError` by default to keep credentials out of
  the repository.
- Expand `AlphaModel.generate_signals` with custom factors, gradient boosted
  models, or deep neural nets using Qlib's task framework.
- Integrate additional agents such as options Greeks calculators, volatility
  surface modellers, or cross-asset arbitrage engines.  The orchestrator simply
  runs agents in sequence, but you can incorporate asynchronous execution or a
  message bus if required.

## Testing

Because Qlib and PyTrader are heavyweight dependencies the default unit tests do
not run them.  Use the included backtesting harness inside a properly configured
environment.  Add pytest-based tests to validate your custom logic.

## License

Apache 2.0 – see `LICENSE` (to be added by project owner).
