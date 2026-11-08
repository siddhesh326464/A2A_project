import logging
import uuid
from orchestrator.config import settings
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from orchestrator.graph.graph import graph
from orchestrator.schema import UserQuery
from orchestrator.graph.graph import graph
from contextlib import asynccontextmanager
from orchestrator.discovery import agent_registry


@asynccontextmanager
async def lifespan(app:FastAPI):

    for agent_name,agent_url in settings.AGENT_URLS.items():
        await agent_registry.descover_agent(
            agent_key=agent_name,
            base_url=agent_url,
            raise_on_failure=False,
        )
    yield

    

app = FastAPI(
    title="Financial Orchestrator API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}



@app.get("/graph")
async def view_graph():
    png_data = await graph.view_graph()

    return Response(content=png_data, media_type="image/png")

@app.post("/chat")
async def chat_endpoint(query:UserQuery):
    response = await graph.aiinvoke(query.question)
    return JSONResponse(response)


