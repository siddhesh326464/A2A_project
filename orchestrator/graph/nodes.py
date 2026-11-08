from orchestrator.graph.state import orchestratorState
from orchestrator.config import settings
from langchain_groq import ChatGroq
import httpx
import logging
from orchestrator.A2A_client import A2A_client
from orchestrator.discovery import agent_registry

logger = logging.getLogger(__name__)

llm = ChatGroq(
    api_key=settings.GROK_API_KEY,
    model=settings.GROK_MODEL_NAME,
)


async def orchestrator_node(state: orchestratorState) -> orchestratorState:
    """
    Uses the LLM to decide which downstream A2A agent should handle the query.
    Returns the selected agent name in state["selected_agent"].
    """
    query = state["question"]

    available_agents = agent_registry.get_routing_prompt()

    prompt = f"""You are an intelligent orchestrator agent responsible for routing user queries to the most appropriate specialized agent.

Available agents:
{available_agents}

User Query: {query}

Your task:
Analyze the user query and determine which agent is best suited to handle it.
Respond with ONLY the agent name from the list above (e.g., "financial"). Do not include any explanation or extra text.

Selected Agent:"""

    response = await llm.ainvoke(prompt)
    selected_agent = response.content.strip().lower()

    logger.info("orchestrator_node: selected_agent=%s", selected_agent)
    return {"selected_agent": selected_agent}

    
# async def financial_node_call(state: orchestratorState)-> orchestratorState:
#     client = A2A_client(base_url=settings.FINANCIAL_AGENT_URL)
#     response = await client.send(question=state["question"])
#     return {"response":response.answer}

async def a2a_dispatcher_node(state:orchestratorState):
    agent_name = state["selected_agent"]
    card = agent_registry.agents.get(agent_name)
    if not card:
        raise ValueError(f"No agent registered with name: {agent_name}")
    target_url = card.provider.url

    client = A2A_client(base_url=target_url)
    response = await client.send(question=state["question"])
    return {"response":response.answer}
    


