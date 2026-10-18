from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict] = None


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]: ...


def create_llm_provider(provider_name: str) -> LLMProvider:
    if provider_name == "claude":
        from app.llm.claude import ClaudeProvider

        return ClaudeProvider()
    if provider_name == "openai":
        from app.llm.openai import OpenAIProvider

        return OpenAIProvider()
    from app.llm.mock import MockProvider

    return MockProvider()
