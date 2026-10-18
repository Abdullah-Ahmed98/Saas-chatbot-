"""RAG pipeline: index documents, retrieve chunks, build LLM context."""
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import KnowledgeChunk, KnowledgeDoc
from app.rag.embeddings import embed, embed_query

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


@dataclass
class RetrievedChunk:
    text: str
    doc_title: str
    score: float


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Naive sliding-window splitter. Good enough for a starter; swap for
    a structure-aware splitter (e.g. by section headings) later."""
    if len(text) <= size:
        return [text] if text.strip() else []
    step = max(size - overlap, 1)
    chunks = []
    for i in range(0, len(text), step):
        piece = text[i : i + size]
        if piece.strip():
            chunks.append(piece)
        if i + size >= len(text):
            break
    return chunks


async def index_document(
    db: AsyncSession, tenant_id, title: str, content: str, source: str | None = None
) -> KnowledgeDoc:
    """Embed a document, store it + its chunks. Returns the doc row."""
    doc = KnowledgeDoc(
        tenant_id=tenant_id, title=title, content=content, source=source,
        doc_length=len(content),
    )
    db.add(doc)
    await db.flush()

    pieces = split_text(content)
    if not pieces:
        pieces = [content[:2000]] if content.strip() else [""]
    vectors = embed(pieces)
    for idx, (text, vec) in enumerate(zip(pieces, vectors)):
        db.add(
            KnowledgeChunk(
                doc_id=doc.id,
                tenant_id=tenant_id,
                chunk_index=idx,
                text=text,
                embedding=vec,
            )
        )
    await db.flush()
    return doc


async def retrieve(
    db: AsyncSession, tenant_id, query: str, top_k: int = 5
) -> list[RetrievedChunk]:
    """Vector-similarity search over the tenant's chunks. Fallback to the
    query vector if no chunks exist yet (returns empty)."""
    rows = (
        await db.execute(
            select(KnowledgeChunk).where(KnowledgeChunk.tenant_id == tenant_id)
        )
    ).scalars().all()
    if not rows:
        return []

    q_vec = embed_query(query)
    import numpy as np

    scored = []
    for r in rows:
        if r.embedding is None:
            continue
        c_vec = np.asarray(r.embedding, dtype=np.float32)
        q = np.asarray(q_vec, dtype=np.float32)
        sim = float(np.dot(c_vec, q) / (np.linalg.norm(c_vec) * np.linalg.norm(q)))
        scored.append((r, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:top_k]

    doc_titles = {}
    if top:
        doc_ids = {r.doc_id for r, _ in top}
        docs = (
            await db.execute(
                select(KnowledgeDoc).where(KnowledgeDoc.id.in_(list(doc_ids)))
            )
        ).scalars().all()
        doc_titles = {d.id: d.title for d in docs}

    return [
        RetrievedChunk(text=r.text, doc_title=doc_titles.get(r.doc_id, "unknown"), score=s)
        for r, s in top
    ]


def build_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks as a system-prompt context block."""
    if not chunks:
        return ""
    blocks = [
        f"[Source: {c.doc_title}] (relevance {c.score:.2f})\n{c.text}"
        for c in chunks
    ]
    return "Relevant knowledge:\n" + "\n\n---\n\n".join(blocks)
