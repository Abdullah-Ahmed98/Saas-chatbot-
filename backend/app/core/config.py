import os
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "env_prefix": "",
    }

    app_name: str = "SAAS Chatbot"
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://saas:saas@localhost:5432/saas"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 14

    # LLM provider selection: "claude", "openai", or "mock"
    llm_provider: str = "mock"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"
    openai_model: str = "gpt-4o-mini"

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    def validate(self) -> None:
        if self.environment == "production" and self.jwt_secret == "change-me":
            raise ValueError("Set a strong JWT_SECRET in production")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Annotated[Settings, "App settings"] = get_settings()
