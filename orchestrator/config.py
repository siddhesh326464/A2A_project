from pydantic_settings import BaseSettings


class OrchestratorSettings(BaseSettings):
    GROK_API_KEY: str
    GROK_MODEL_NAME : str
    FINANCIAL_AGENT_URL: str = "http://localhost:8001"
    AGENT_URLS: dict = {
        "financial": "http://localhost:8001",
    }

    model_config = {"env_file": ".env"}


settings = OrchestratorSettings()
