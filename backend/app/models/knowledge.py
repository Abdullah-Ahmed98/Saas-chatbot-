import uuid
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

EMBED_DIM = 384  # all-MiniLM-L6-v2 (sentence-transformers) produces 384-d vectors


class KnowledgeDoc(Base, TimestampMixin):
    """A user-uploaded document that has been split and embedded for RAG."""

    __tablename__ = "knowledge_docs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # URL / file name
    content: Mapped[str] = mapped_column(String, nullable=False)  # full raw text
    doc_length: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class KnowledgeChunk(Base, TimestampMixin):
    """A single embedded chunk of a KnowledgeDoc, stored as a pgvector row."""

    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    doc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(EMBED_DIM), nullable=True
    )
