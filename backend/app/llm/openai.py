from typing import AsyncIterator, List, Optional

import openai

from app.core.config import settings
from app.llm.base import LLMProvider, LLMResponse, Message


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat(
        self,
        messages: List[Message],
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend({"role": m.role, "content": m.content} for m in messages)
        resp = await self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=msgs,
        )
        usage = {
            "input_tokens": resp.usage.prompt_tokens,
            "output_tokens": resp.usage.completion_tokens,
        }
        return LLMResponse(
            content=resp.choices[0].message.content or "",
            model=resp.model,
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
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend({"role": m.role, "content": m.content} for m in messages)
        stream = await self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=msgs,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
