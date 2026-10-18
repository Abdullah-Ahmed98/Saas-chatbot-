import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_db
from app.models.database import get_db
from app.models.knowledge import KnowledgeDoc
from app.rag.service import index_document, retrieve, build_context

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class DocOut(BaseModel):
    id: uuid.UUID
    title: str
    source: str | None
    doc_length: int


class IngestResult(BaseModel):
    doc_id: uuid.UUID
    title: str
    chunks: int


@router.post("/ingest", response_model=IngestResult, status_code=201)
async def ingest(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: Annotated[UploadFile | None, File()] = None,
    text: Annotated[str | None, Form()] = None,
    title: Annotated[str | None, Form()] = None,
):
    """Index a document for RAG. Send either a file (text/markdown) or raw text."""
    if user.tenant_id is None:
        raise HTTPException(400, "No tenant associated with user")

    content: str
    if file is not None and file.filename:
        raw = await file.read()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(400, "Only text-based files are supported for now")
        doc_title = title or file.filename
    elif text is not None:
        content = text
        doc_title = title or (text.strip().splitlines()[0][:80] if text.strip() else "Untitled")
    else:
        raise HTTPException(400, "Provide either 'file' or 'text'")

    if not content.strip():
        raise HTTPException(400, "Empty document")

    doc = await index_document(db, user.tenant_id, doc_title, content, source=file.filename if file else None)
    await db.commit()
    return IngestResult(doc_id=doc.id, title=doc.title, chunks=0)


@router.get("/docs", response_model=list[DocOut])
async def list_docs(user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user.tenant_id is None:
        return []
    rows = (
        await db.execute(
            select(KnowledgeDoc).where(KnowledgeDoc.tenant_id == user.tenant_id).order_by(KnowledgeDoc.created_at.desc())
        )
    ).scalars().all()
    return [DocOut(id=d.id, title=d.title, source=d.source, doc_length=d.doc_length) for d in rows]


@router.delete("/docs/{doc_id}")
async def delete_doc(doc_id: uuid.UUID, user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    doc = (
        await db.execute(
            select(KnowledgeDoc).where(KnowledgeDoc.id == doc_id, KnowledgeDoc.tenant_id == user.tenant_id)
        )
    ).scalar_one_or_none()
    if doc is None:
        raise HTTPException(404, "Doc not found")
    from app.models.knowledge import KnowledgeChunk

    await db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.doc_id == doc.id))
    await db.delete(doc)
    await db.commit()
    return {"ok": True}


@router.post("/search")
async def search(user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)], q: str = Query(...), k: int = Query(5, ge=1, le=20)):
    """Return top-k retrieved chunks without calling the LLM (useful for testing RAG wiring)."""
    if user.tenant_id is None:
        return []
    chunks = await retrieve(db, user.tenant_id, q, top_k=k)
    return [
        {"text": c.text, "doc": c.doc_title, "score": round(c.score, 3)} for c in chunks
    ]
