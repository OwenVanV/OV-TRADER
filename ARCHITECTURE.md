# System architecture

The OV Trader framework follows a modular multi-agent design:

```text
+------------------+     +------------------+     +-------------------+
| NewsSentiment    | --> | Forecast          | --> | Portfolio         |
| Agent            |     | Agent             |     | Agent             |
+------------------+     +------------------+     +---------+---------+
                                                         |
                                                         v
                                               +-------------------+
                                               | Execution Agent   |
                                               +-------------------+
```

1. **NewsSentimentAgent** collects qualitative information from the wider
   internet, summarises it with a large language model, and stores the output in
   the shared context.
2. **ForecastAgent** interfaces with Microsoft Qlib to produce numerical alpha
   scores derived from historical data and engineered features.
3. **PortfolioAgent** converts alpha values into target allocations while
   respecting basic risk limits.
4. **ExecutionAgent** forwards the generated orders to brokerage accounts via the
   PyTrader bridge.

Agents share data through :class:`ov_trader.agents.base.AgentContext`.  The
:class:`ov_trader.agents.orchestrator.Orchestrator` initialises the context and
runs each agent sequentially, enabling additional agents (e.g. volatility
forecasting, options pricing) to be added by simply appending them to the list.

Backtesting utilities are provided through `ov_trader.backtesting.runner`, which
can reuse the same alpha generation pipeline on historical data.  This promotes a
research-to-production workflow where strategies are evaluated extensively before
any live deployment.
