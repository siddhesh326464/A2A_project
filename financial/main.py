import logging
from fastapi import FastAPI, HTTPException
from financial.agent_card import AGENT_CARD_DICT
from financial.schema import FinancialRequest, FinancialResponse
from financial.graph.graph import graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Agent API",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"message": "service is running"}


@app.get("/.well-known/agent-card.json")
@app.get("/.well-known/agent.json")
async def get_agent_card() -> dict:
    """Serves the pre-built A2A Agent Card for discovery."""
    return AGENT_CARD_DICT


@app.post("/chat", response_model=FinancialResponse)
async def chat_endpoint(request: FinancialRequest):
    """
    A2A Endpoint called by the Orchestrator's A2A_client.
    Executes the Financial LangGraph and returns the response.
    """
    logger.info("Received query: '%s' (request_id=%s)", request.question, request.request_id)
    try:
        result = await graph.ainvoke(request.question)
        return FinancialResponse(
            response=result.get("response", ""),
            agent="financial",
            request_id=request.request_id or "",
        )
    except Exception as e:
        logger.exception("Error processing financial query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
