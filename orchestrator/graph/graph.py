from langgraph.graph import StateGraph, START, END
from orchestrator.graph.state import orchestratorState
from orchestrator.graph.nodes import orchestrator_node, a2a_dispatcher_node
import asyncio


class OrchestratorGraph:
    def __init__(self):
        self.graph = self.build_graph()

    def build_graph(self):
        builder = StateGraph(orchestratorState)

        builder.add_node("orchestrator", orchestrator_node)
        builder.add_node("a2a_dispatcher", a2a_dispatcher_node)

        builder.add_edge(START, "orchestrator")

        builder.add_conditional_edges(
            "orchestrator",
            self._route_to_agent,
            {
                "a2a_dispatcher": "a2a_dispatcher",
                END: END,
            }
        )

        builder.add_edge("a2a_dispatcher", END)

        return builder.compile()

    @staticmethod
    def _route_to_agent(state: orchestratorState) -> str:
        agent = state.get("selected_agent", "").lower()
        if agent and agent != "none":
            return "a2a_dispatcher"
        return END

    async def aiinvoke(self, query: str):
        initial_state = {
            "question": query
        }
        return await self.graph.ainvoke(initial_state)

    async def view_graph(self) -> bytes:
        graph = self.graph.get_graph()
        return await asyncio.to_thread(graph.draw_png)


graph = OrchestratorGraph()
