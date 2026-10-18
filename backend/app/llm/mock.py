from typing import AsyncIterator, List, Optional

from app.llm.base import LLMProvider, LLMResponse, Message


class MockProvider(LLMProvider):
    """Echoes back the last user message. Use to develop without API keys."""

    async def chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        last_user = next((m for m in reversed(messages) if m.role == "user"), None)
        content = f"[mock] You said: {last_user.content}" if last_user else "[mock] No message."
        return LLMResponse(content=content, model="mock-1")

    async def stream_chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        resp = await self.chat(messages, system=system, temperature=temperature, max_tokens=max_tokens)
        # Yield in chunks
        for i in range(0, len(resp.content), 8):
            yield resp.content[i : i + 8]
            await _noop()


async def _noop() -> None:
    import asyncio

    await asyncio.sleep(0)
