import uuid
from typing import AsyncIterator, List

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.base import LLMProvider, Message, create_llm_provider
from app.models.schemas import ChatSession, Message as DBMessage, Tenant


class ChatRequest(BaseModel):
    session_id: uuid.UUID | None = None
    content: str
    provider: str | None = None
    system: str | None = None
    use_rag: bool = False


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    response: str
    provider: str


class ChatStreamResponse(BaseModel):
    session_id: uuid.UUID
    delta: str
    done: bool


class ChatService:
    def __init__(self, db: AsyncSession, tenant: Tenant, provider: str | None = None) -> None:
        self.db = db
        self.tenant = tenant
        self.provider_name = provider or "mock"
        self.llm: LLMProvider = create_llm_provider(self.provider_name)

    async def _get_or_create_session(self, session_id: uuid.UUID | None) -> ChatSession:
        if session_id is not None:
            s = (
                await self.db.execute(
                    select(ChatSession).where(
                        ChatSession.id == session_id,
                        ChatSession.tenant_id == self.tenant.id,
                    )
                )
            ).scalar_one_or_none()
            if s is None:
                raise ValueError("Session not found for tenant")
            return s

        s = ChatSession(
            tenant_id=self.tenant.id,
            llm_provider=self.provider_name,
        )
        self.db.add(s)
        await self.db.flush()
        return s

    async def _build_messages(self, session_id: uuid.UUID, user_msg: Message) -> List[Message]:
        rows = (
            await self.db.execute(
                select(DBMessage)
                .where(DBMessage.session_id == session_id)
                .order_by(DBMessage.created_at)
            )
        ).scalars().all()
        history = [Message(role=r.role, content=r.content) for r in rows]
        history.append(user_msg)
        return history

    async def _augment_system(self, req: ChatRequest) -> str | None:
        """Optionally prepend retrieved knowledge to the system prompt (RAG)."""
        base = req.system
        if req.use_rag:
            from app.rag.service import build_context, retrieve

            chunks = await retrieve(self.db, self.tenant.id, req.content, top_k=5)
            ctx = build_context(chunks)
            if ctx:
                base = (base + "\n\n" if base else "") + ctx
        return base

    async def chat(self, req: ChatRequest) -> ChatResponse:
        session = await self._get_or_create_session(req.session_id)
        user_msg = Message(role="user", content=req.content)

        self.db.add(DBMessage(session_id=session.id, role="user", content=req.content))
        await self.db.flush()

        system = await self._augment_system(req)
        msgs = await self._build_messages(session.id, user_msg)
        resp = await self.llm.chat(msgs, system=system)

        self.db.add(
            DBMessage(
                session_id=session.id,
                role="assistant",
                content=resp.content,
                meta={"model": resp.model, "usage": resp.usage},
            )
        )
        session.title = session.title or req.content[:60]
        await self.db.commit()
        return ChatResponse(
            session_id=session.id,
            response=resp.content,
            provider=self.provider_name,
        )

    async def stream_chat(self, req: ChatRequest):
        session = await self._get_or_create_session(req.session_id)
        user_msg = Message(role="user", content=req.content)

        self.db.add(DBMessage(session_id=session.id, role="user", content=req.content))
        await self.db.flush()

        system = await self._augment_system(req)
        msgs = await self._build_messages(session.id, user_msg)

        chunks: list[str] = []
        async for delta in self.llm.stream_chat(msgs, system=system):
            chunks.append(delta)
            yield ChatStreamResponse(session_id=session.id, delta=delta, done=False)
        full = "".join(chunks)
        self.db.add(DBMessage(session_id=session.id, role="assistant", content=full))
        session.title = session.title or req.content[:60]
        await self.db.commit()
        yield ChatStreamResponse(session_id=session.id, delta="", done=True)

