"""Integration test for AC-028 against the real database: a citation whose
chunk has no page_number (document_chunks.page_number is nullable -- some PDF
structures don't preserve page-level position) must still name the source
document, rather than being omitted from the response entirely.

backend/tests/integration/test_messages.py already covers AC-022/023/024/025/
026/029/030 with the same faked-google-genai-client pattern used here, but
every chunk it inserts carries a real page_number; none of its tests ever
exercise a null one, which is exactly what AC-028 is about. Follows that
file's conventions (real Postgres+pgvector, only the google-genai client
faked) rather than duplicating its broader coverage.
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.main import app
from app.models import EMBEDDING_DIM as DIM
from app.models import ChatSession, Document, DocumentChunk, User

client = TestClient(app)

PASSWORD = "".join(["Str", "ong", "Pass", "word", "1"])


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _signup(email: str) -> str:
    response = client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["access_token"]


def _cleanup(db, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        db.delete(user)
        db.commit()
    db.close()


def test_ac028_citation_for_a_chunk_with_no_page_number_still_names_the_document(
    monkeypatch,
) -> None:
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user = db.query(User).filter(User.email == email).one()

        session = ChatSession(user_id=user.id, name="No page-position session")
        db.add(session)
        db.flush()

        document = Document(
            session_id=session.id,
            user_id=user.id,
            filename="structureless.pdf",
            s3_key=f"sessions/{session.id}/structureless.pdf",
            size_bytes=1024,
            status="ready",
            page_count=None,
        )
        db.add(document)
        db.flush()

        vector = [0.0] * DIM
        vector[0] = 1.0
        chunk = DocumentChunk(
            document_id=document.id,
            session_id=session.id,
            chunk_index=0,
            page_number=None,
            content="Content with no preserved page position.",
            embedding=vector,
        )
        db.add(chunk)
        db.commit()

        class _Models:
            def embed_content(self, *, model, contents, config=None):
                return SimpleNamespace(embeddings=[SimpleNamespace(values=vector)])

            def generate_content(self, *, model, contents):
                return SimpleNamespace(text="Here is the answer, grounded in that content.")

        fake_client = SimpleNamespace(models=_Models())
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        response = client.post(
            f"/sessions/{session.id}/messages",
            json={"question": "What does it say?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["citations"]) == 1
        citation = body["citations"][0]
        # The citation is not omitted, and still identifies the source
        # document by name, even though no page number could be shown.
        assert citation["document_id"] == str(document.id)
        assert citation["filename"] == "structureless.pdf"
        assert citation["page_number"] is None
    finally:
        _cleanup(db, email)
