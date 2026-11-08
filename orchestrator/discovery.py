"""
orchestrator/discovery.py
Fetches and registers A2A AgentCards from downstream agents.
The Orchestrator calls this on startup to discover what agents are available.
"""

import logging,httpx, asyncio
from a2a.client.card_resolver import A2ACardResolver
from a2a.types import AgentCard


class AgentRegistry:
    def __init__(self):
        self.agents : dict[str, AgentCard] = {}
        self.urls : dict[str,str]= {}
        self._lock = asyncio.Lock()


    async def descover_agent(self,agent_key:str,base_url:str,raise_on_failure:bool = False)->AgentCard:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resolver = A2ACardResolver(
                    httpx_client=client,
                    base_url=base_url
                )
                card: AgentCard = await resolver.get_agent_card()
                async with self._lock:
                    self.agents[agent_key] = card
                    self.urls[agent_key] = base_url

            return card     

        except Exception as e:
            print(e)

    async def refresh_all(self)->None:
        """Re-fetches all registered agent cards. Call periodically."""
        for key, url in dict(self.urls).items():
            await self.descover_agent(key,url)

    def get_routing_prompt(self):
        if not self.agents:
            return "No agents currently registered"
        lines = []
        for key,card in self.agents.items():
            skills = ", ".join(s.name for s in card.skills) if card.skills else "general"
            lines.append(f"- {key}: {card.description} (Skills: {skills})")
        return "\n".join(lines)

    @property
    def registered(self):
        return self.agents


agent_registry = AgentRegistry()


    


        
