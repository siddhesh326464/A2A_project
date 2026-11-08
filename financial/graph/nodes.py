import logging
from langchain_groq import ChatGroq
from financial.config import settings
from financial.graph.state import FinancialState

logger = logging.getLogger(__name__)

llm = ChatGroq(
    api_key=settings.GROK_API_KEY,
    model=settings.GROK_MODEL_NAME,
)

SYSTEM_PROMPT = """You are an expert financial advisor agent.
Your domain covers personal finance, investments, retirement accounts, taxes, banking, and economics.
Provide clear, accurate, and concise financial guidance."""


async def financial_node(state: FinancialState) -> FinancialState:
    """Processes the query using the Financial LLM and returns the advice."""
    query = state["question"]
    logger.info("financial_node processing question: '%s'", query)

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", query),
    ]
    response = await llm.ainvoke(messages)
    answer = response.content.strip()

    return {"response": answer}

