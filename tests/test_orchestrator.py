from ov_trader.agents.base import AgentContext, BaseAgent
from ov_trader.agents.orchestrator import Orchestrator


class DummyAgent(BaseAgent):
    def __init__(self, name: str, value: str) -> None:
        super().__init__(name)
        self.value = value

    def run(self, context: AgentContext) -> AgentContext:
        context.shared_memory[self.name] = self.value
        return context


def test_orchestrator_runs_agents_in_order():
    agents = [DummyAgent("a", "first"), DummyAgent("b", "second")]
    orchestrator = Orchestrator(agents)
    context = orchestrator.run_cycle()
    assert context.shared_memory["a"] == "first"
    assert context.shared_memory["b"] == "second"
