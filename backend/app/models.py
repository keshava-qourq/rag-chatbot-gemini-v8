"""SQLAlchemy models for the approved data model.

One class per entity in docs/sdlc/architecture/data-model.md. `Base` is bound to
the engine in app.database; app.main imports this module before it creates the
schema, and backend/alembic/env.py imports it for autogenerate. The schema these
models describe is the same one backend/alembic/versions/0001_initial_schema.py
creates by hand -- keep the two in step when either changes.

Primary and foreign keys use the cross-dialect `sqlalchemy.Uuid`, not the
Postgres-only `postgresql.UUID`, so the same models also work against the
SQLite fallback `app.database` uses when DATABASE_URL is unset (local dev, the
frontend's e2e suite). `pgvector.sqlalchemy.Vector` tolerates SQLite too; real
vector search only runs where the `vector` extension exists, i.e. Postgres.
"""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.database import Base

__all__ = [
    "Base",
    "User",
    "ChatSession",
    "Document",
    "DocumentChunk",
    "Message",
    "Citation",
    "RevokedToken",
]

# Gemini embeddings (gemini-embedding-001), truncated to this many dimensions,
# is what document_chunks.embedding stores -- see docs/sdlc/architecture/data-model.md.
EMBEDDING_DIM = 768


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _fk(
    target: str, *, ondelete: str, nullable: bool = False, indexed: bool = True
) -> Mapped[uuid.UUID]:
    return mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(target, ondelete=ondelete),
        nullable=nullable,
        index=indexed,
    )


def _created_at() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _pk()
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = _created_at()

    sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ChatSession(Base):
    """A chat session.

    Named `ChatSession` in Python so it does not shadow `sqlalchemy.orm.Session`;
    the table itself is `sessions`, exactly as the data model names it.
    """

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = _pk()
    user_id: Mapped[uuid.UUID] = _fk("users.id", ondelete="CASCADE")
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = _created_at()

    user: Mapped["User"] = relationship(back_populates="sessions")
    documents: Mapped[list["Document"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = _pk()
    session_id: Mapped[uuid.UUID] = _fk("sessions.id", ondelete="CASCADE")
    user_id: Mapped[uuid.UUID] = _fk("users.id", ondelete="CASCADE")
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(512), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # processing | ready | failed -- see architecture notes for api_backend/worker.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processing")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = _created_at()

    user: Mapped["User"] = relationship(back_populates="documents")
    session: Mapped["ChatSession"] = relationship(back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    citations: Mapped[list["Citation"]] = relationship(back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = _pk()
    document_id: Mapped[uuid.UUID] = _fk("documents.id", ondelete="CASCADE")
    session_id: Mapped[uuid.UUID] = _fk("sessions.id", ondelete="CASCADE")
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    created_at: Mapped[datetime] = _created_at()

    document: Mapped["Document"] = relationship(back_populates="chunks")
    session: Mapped["ChatSession"] = relationship(back_populates="chunks")
    citations: Mapped[list["Citation"]] = relationship(back_populates="chunk")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = _pk()
    session_id: Mapped[uuid.UUID] = _fk("sessions.id", ondelete="CASCADE")
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _created_at()

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
    citations: Mapped[list["Citation"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[uuid.UUID] = _pk()
    message_id: Mapped[uuid.UUID] = _fk("messages.id", ondelete="CASCADE")
    document_id: Mapped[uuid.UUID] = _fk("documents.id", ondelete="CASCADE")
    chunk_id: Mapped[uuid.UUID | None] = _fk(
        "document_chunks.id", ondelete="SET NULL", nullable=True
    )
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    message: Mapped["Message"] = relationship(back_populates="citations")
    document: Mapped["Document"] = relationship(back_populates="citations")
    chunk: Mapped["DocumentChunk | None"] = relationship(back_populates="citations")


class RevokedToken(Base):
    """A blocklist of logged-out JWTs, keyed by their `jti` claim.

    Stateless JWTs can't be invalidated by themselves; logging out inserts the
    token's jti here, and get_current_user (app.deps) rejects any token whose
    jti is present, giving logout a real server-side effect (NFR-004). A single
    small table is sufficient at the tens-to-low-hundreds-of-users scale this
    system targets (NFR-016) -- no distributed session store needed.
    """

    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    revoked_at: Mapped[datetime] = _created_at()
