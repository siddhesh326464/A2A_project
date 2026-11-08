from pydantic_settings import BaseSettings


class FinancialSettings(BaseSettings):
    GROK_API_KEY: str
    GROK_MODEL_NAME: str
    FINANCIAL_AGENT_URL: str = "http://127.0.0.1:8001"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = FinancialSettings()
