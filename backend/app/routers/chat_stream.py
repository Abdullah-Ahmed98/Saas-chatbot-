import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_db
from app.models.schemas import Tenant
from app.services.chat_service import ChatRequest, ChatService

router = APIRouter(prefix="/api/chat", tags=["chat-stream"])


@router.post("/stream/new")
async def stream_new(
    req: Annotated[ChatRequest, Body()],
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Start a new chat session (no existing session_id)."""
    if user.tenant_id is None:
        raise HTTPException(400, "No tenant associated with user")
    tenant = (
        await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    ).scalar_one_or_none()
    if tenant is None:
        raise HTTPException(404, "Tenant not found")

    svc = ChatService(db, tenant, provider=req.provider)

    async def gen():
        async for chunk in svc.stream_chat(req):
            yield json.dumps(
                {
                    "session_id": str(chunk.session_id),
                    "delta": chunk.delta,
                    "done": chunk.done,
                }
            ) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@router.post("/stream/{session_id}")
async def stream_message(
    session_id: uuid.UUID,
    req: Annotated[ChatRequest, Body()],
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    req.session_id = session_id
    if user.tenant_id is None:
        raise HTTPException(400, "No tenant associated with user")
    tenant = (
        await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    ).scalar_one_or_none()
    if tenant is None:
        raise HTTPException(404, "Tenant not found")

    svc = ChatService(db, tenant, provider=req.provider)

    async def gen():
        async for chunk in svc.stream_chat(req):
            yield json.dumps(
                {
                    "session_id": str(chunk.session_id),
                    "delta": chunk.delta,
                    "done": chunk.done,
                }
            ) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")
