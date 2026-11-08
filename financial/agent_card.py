"""
financial/agent_card.py

Builds the A2A AgentCard for the Financial Agent.
Built ONCE at startup — served on every GET /.well-known/agent.json request.
"""

from a2a.types import AgentCard, AgentSkill, AgentCapabilities, AgentProvider
from financial.config import settings
from google.protobuf.json_format import MessageToDict


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="Financial Agent",
        description=(
            "Specialized agent for financial advice, investments, taxes, "
            "banking, budgeting, and cryptocurrency."
        ),
        version="1.0.0",
        provider=AgentProvider(           
            url=settings.FINANCIAL_AGENT_URL,
            organization="My Finance Co."
        ),
        skills=[
            AgentSkill(
                id="financial_advisory",
                name="financial",
                description=(
                    "Handles questions related to finance, investments, stocks, "
                    "budgeting, accounting, taxes, banking, cryptocurrency, and economic data."
                )
            )
        ],
        capabilities=AgentCapabilities(
            streaming=False,
            push_notifications=False
        )
    )


AGENT_CARD: AgentCard = build_agent_card()
AGENT_CARD_DICT: dict  = MessageToDict(AGENT_CARD) 