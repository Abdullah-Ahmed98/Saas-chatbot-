from typing import AsyncIterator, List, Optional

import anthropic

from app.core.config import settings
from app.llm.base import LLMProvider, LLMResponse, Message


class ClaudeProvider(LLMProvider):
    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        msg = await self.client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        usage = {
            "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens,
        }
        return LLMResponse(
            content=msg.content[0].text,
            model=msg.model,
            usage=usage,
        )

    async def stream_chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        ) as stream:
            async for text in stream.text_stream:
                yield text
