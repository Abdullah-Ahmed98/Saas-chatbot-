import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_db
from app.models.schemas import ChatSession, Message as DBMessage, Tenant

router = APIRouter(prefix="/api/chat", tags=["chat"])


class SessionOut(BaseModel):
    id: uuid.UUID
    title: str
    llm_provider: str
    model: str


class SessionMessage(BaseModel):
    id: uuid.UUID
    role: str
    content: str


class SessionDetail(BaseModel):
    id: uuid.UUID
    title: str
    llm_provider: str
    model: str
    messages: List[SessionMessage]


@router.get("/sessions", response_model=List[SessionOut])
async def list_sessions(
    user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    if user.tenant_id is None:
        return []
    rows = (
        await db.execute(
            select(ChatSession)
            .where(ChatSession.tenant_id == user.tenant_id)
            .order_by(ChatSession.created_at.desc())
            .limit(100)
        )
    ).scalars().all()
    return [
        SessionOut(id=s.id, title=s.title, llm_provider=s.llm_provider, model=s.model)
        for s in rows
    ]


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: uuid.UUID,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    s = (
        await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.tenant_id == user.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if s is None:
        raise HTTPException(404, "Session not found")
    msgs = (
        await db.execute(
            select(DBMessage)
            .where(DBMessage.session_id == s.id)
            .order_by(DBMessage.created_at)
        )
    ).scalars().all()
    return SessionDetail(
        id=s.id,
        title=s.title,
        llm_provider=s.llm_provider,
        model=s.model,
        messages=[SessionMessage(id=m.id, role=m.role, content=m.content) for m in msgs],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: uuid.UUID,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    s = (
        await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.tenant_id == user.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if s is None:
        raise HTTPException(404, "Session not found")
    await db.execute(delete(DBMessage).where(DBMessage.session_id == s.id))
    await db.delete(s)
    await db.commit()
    return {"ok": True}
