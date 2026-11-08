from langgraph.graph import StateGraph, START, END
from financial.graph.state import FinancialState
from financial.graph.nodes import financial_node


class FinancialGraph:
    def __init__(self):
        self.graph = self.build_graph()

    def build_graph(self):
        builder = StateGraph(FinancialState)

        builder.add_node("financial_agent", financial_node)

        builder.add_edge(START, "financial_agent")
        builder.add_edge("financial_agent", END)

        return builder.compile()

    async def ainvoke(self, query: str) -> dict:
        initial_state = {
            "question": query,
            "response": ""
        }
        return await self.graph.ainvoke(initial_state)


graph = FinancialGraph()

