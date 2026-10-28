"""Round-trips a row through every model against the real database.

`app.main` already creates the schema (via Base.metadata.create_all) on import,
including the pgvector-backed document_chunks table, so this proves the models,
not just that they import cleanly: a User, a ChatSession, a Document, a
DocumentChunk with an embedding, a Message and a Citation can be written and
read back with their relationships intact, then cleaned up.
"""

import uuid

import app.main  # noqa: F401 -- import order: creates the schema before this runs
from app.database import SessionLocal
from app.models import ChatSession, Citation, Document, DocumentChunk, Message, User


def test_full_graph_round_trips() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"{uuid.uuid4()}@example.com", password_hash="not-a-real-hash")
        db.add(user)
        db.flush()

        session = ChatSession(user_id=user.id, name="Test session")
        db.add(session)
        db.flush()

        document = Document(
            session_id=session.id,
            user_id=user.id,
            filename="test.pdf",
            s3_key="sessions/test/test.pdf",
            size_bytes=1024,
            status="ready",
            page_count=1,
        )
        db.add(document)
        db.flush()

        chunk = DocumentChunk(
            document_id=document.id,
            session_id=session.id,
            chunk_index=0,
            page_number=1,
            content="hello world",
            embedding=[0.0] * 768,
        )
        db.add(chunk)
        db.flush()

        message = Message(session_id=session.id, role="assistant", content="hi")
        db.add(message)
        db.flush()

        citation = Citation(
            message_id=message.id,
            document_id=document.id,
            chunk_id=chunk.id,
            page_number=1,
            snippet="hello",
        )
        db.add(citation)
        db.commit()

        db.refresh(citation)
        assert citation.chunk_id == chunk.id
        assert len(chunk.embedding) == 768

        db.delete(user)
        db.commit()
    finally:
        db.close()
