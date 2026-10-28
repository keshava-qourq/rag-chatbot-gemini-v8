"""Integration tests for POST /sessions/{session_id}/messages against the real
database (Postgres + pgvector), covering US-009's acceptance criteria.

Gemini is not one of this project's provisioned services (see ENVIRONMENT.md),
so every test here fakes `app.rag._gemini_client` rather than reaching the real
API -- the fake still exercises the real `_embed_question`/`_generate_answer`
bodies in app.rag (which build the actual request kwargs, including the model
names), it just never makes a network call. Documents and their chunks are
inserted directly against the real database (mirroring test_models.py) so each
test controls exactly which chunks exist and what they embed to, without going
through the S3-backed upload route or the Redis-backed processing job.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.jobs import EMBEDDING_MODEL
from app.main import app
from app.models import Citation, Document, DocumentChunk, Message, User
from app.models import EMBEDDING_DIM as DIM
from app.rag import GENERATION_MODEL, NOT_FOUND_ANSWER

client = TestClient(app)

PASSWORD = "StrongPass1!"


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _signup(email: str) -> str:
    response = client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["access_token"]


def _create_session(token: str, name: str) -> str:
    response = client.post(
        "/sessions", json={"name": name}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    return response.json()["id"]


def _vector(active_index: int, dim: int = DIM) -> list[float]:
    """A unit vector with a 1.0 at ``active_index`` -- identical vectors have
    cosine distance 0; distinct active indices are maximally dissimilar."""
    values = [0.0] * dim
    values[active_index] = 1.0
    return values


def _add_document(
    db, *, session_id: str, user_id: str, filename: str, status: str = "ready"
) -> Document:
    document = Document(
        session_id=uuid.UUID(session_id),
        user_id=uuid.UUID(user_id),
        filename=filename,
        s3_key=f"sessions/{session_id}/{filename}",
        size_bytes=1024,
        status=status,
        page_count=1,
    )
    db.add(document)
    db.flush()
    return document


def _add_chunk(
    db,
    *,
    document: Document,
    session_id: str,
    content: str,
    page_number: int,
    embedding: list[float],
) -> DocumentChunk:
    chunk = DocumentChunk(
        document_id=document.id,
        session_id=uuid.UUID(session_id),
        chunk_index=0,
        page_number=page_number,
        content=content,
        embedding=embedding,
    )
    db.add(chunk)
    db.flush()
    return chunk


def _add_message(
    db, *, session_id: str, role: str, content: str, created_at: datetime
) -> Message:
    message = Message(
        session_id=uuid.UUID(session_id),
        role=role,
        content=content,
        created_at=created_at,
    )
    db.add(message)
    db.flush()
    return message


def _user_id_from_email(db, email: str) -> uuid.UUID:
    return db.query(User).filter(User.email == email).one().id


def _cleanup(db, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        db.delete(user)
        db.commit()
    db.close()


def _make_fake_client(
    *,
    embed_vector: list[float] | None = None,
    embed_error: Exception | None = None,
    answer_text: str | None = None,
    answer_error: Exception | None = None,
):
    """A stand-in for google.genai.Client. Records every call it receives so
    tests can assert *what* was sent to the generation model, without ever
    reaching the real Gemini API."""
    record: dict[str, list[dict]] = {"embed_calls": [], "generate_calls": []}

    class _Models:
        def embed_content(self, *, model, contents, config=None):
            record["embed_calls"].append({"model": model, "contents": contents})
            if embed_error is not None:
                raise embed_error
            return SimpleNamespace(embeddings=[SimpleNamespace(values=embed_vector)])

        def generate_content(self, *, model, contents):
            record["generate_calls"].append({"model": model, "contents": contents})
            if answer_error is not None:
                raise answer_error
            return SimpleNamespace(text=answer_text)

    return SimpleNamespace(models=_Models()), record


def _message_count(db, session_id: str) -> int:
    return db.query(Message).filter(Message.session_id == uuid.UUID(session_id)).count()


def test_ac022_question_is_embedded_retrieved_and_answered_via_gemini_flash(monkeypatch) -> None:
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)
        session_id = _create_session(token, "Policy session")

        document = _add_document(
            db, session_id=session_id, user_id=str(user_id), filename="policy.pdf"
        )
        chunk_vector = _vector(0)
        _add_chunk(
            db,
            document=document,
            session_id=session_id,
            content="Refunds are accepted within 30 days of purchase.",
            page_number=4,
            embedding=chunk_vector,
        )
        db.commit()

        fake_client, record = _make_fake_client(
            embed_vector=chunk_vector,
            answer_text="Refunds are accepted within 30 days of purchase.",
        )
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        response = client.post(
            f"/sessions/{session_id}/messages",
            json={"question": "What is the refund window?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["role"] == "assistant"
        assert body["content"] == "Refunds are accepted within 30 days of purchase."
        assert len(body["citations"]) == 1
        citation = body["citations"][0]
        assert citation["document_id"] == str(document.id)
        assert citation["filename"] == "policy.pdf"
        assert citation["page_number"] == 4

        # AC-022: the question itself was embedded with gemini-embedding-001...
        assert len(record["embed_calls"]) == 1
        assert record["embed_calls"][0]["model"] == EMBEDDING_MODEL
        assert record["embed_calls"][0]["contents"] == "What is the refund window?"

        # ...and the answer was generated via gemini-2.5-flash, grounded in the
        # retrieved chunk's text.
        assert len(record["generate_calls"]) == 1
        assert record["generate_calls"][0]["model"] == GENERATION_MODEL
        assert "Refunds are accepted within 30 days" in record["generate_calls"][0]["contents"]

        # Both the question and the answer were persisted as real messages.
        messages = (
            db.query(Message)
            .filter(Message.session_id == uuid.UUID(session_id))
            .order_by(Message.created_at.asc())
            .all()
        )
        assert [m.role for m in messages] == ["user", "assistant"]
        assert messages[0].content == "What is the refund window?"
        assert messages[1].content == "Refunds are accepted within 30 days of purchase."
    finally:
        _cleanup(db, email)


def test_ac023_other_sessions_chunks_are_never_retrieved_or_referenced(monkeypatch) -> None:
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)

        session_a = _create_session(token, "Session A")
        session_b = _create_session(token, "Session B")

        shared_vector = _vector(0)

        doc_a = _add_document(
            db, session_id=session_a, user_id=str(user_id), filename="session-a.pdf"
        )
        _add_chunk(
            db,
            document=doc_a,
            session_id=session_a,
            content="Session A's own content about vacation policy.",
            page_number=1,
            embedding=shared_vector,
        )

        doc_b = _add_document(
            db, session_id=session_b, user_id=str(user_id), filename="session-b.pdf"
        )
        _add_chunk(
            db,
            document=doc_b,
            session_id=session_b,
            content="OTHER SESSION SECRET CONTENT about vacation policy.",
            page_number=1,
            # Deliberately identical to session A's chunk embedding, so that if
            # retrieval ever failed to scope by session, this chunk would be an
            # equally (or more) likely match -- isolation is proven precisely
            # because it still never shows up.
            embedding=shared_vector,
        )
        db.commit()

        fake_client, record = _make_fake_client(
            embed_vector=shared_vector,
            answer_text="Vacation policy allows 15 days per year.",
        )
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        response = client.post(
            f"/sessions/{session_a}/messages",
            json={"question": "What is the vacation policy?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.json()
        document_ids = {c["document_id"] for c in body["citations"]}
        assert document_ids == {str(doc_a.id)}
        assert str(doc_b.id) not in document_ids

        # The other session's chunk text never made it into the prompt either.
        prompt = record["generate_calls"][0]["contents"]
        assert "OTHER SESSION SECRET CONTENT" not in prompt
    finally:
        _cleanup(db, email)


def test_ac024_no_ready_documents_rejects_without_calling_gemini(monkeypatch) -> None:
    def _unexpected_client():
        raise AssertionError(
            "Gemini must not be called when the session has no ready documents"
        )

    monkeypatch.setattr("app.rag._gemini_client", _unexpected_client)

    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)

        # Case 1: no documents attached at all.
        empty_session = _create_session(token, "Empty session")
        response = client.post(
            f"/sessions/{empty_session}/messages",
            json={"question": "Anything in here?"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
        assert "ready" in response.json()["detail"].lower()
        assert _message_count(db, empty_session) == 0

        # Case 2: a document exists but is still processing, not ready.
        processing_session = _create_session(token, "Processing session")
        _add_document(
            db,
            session_id=processing_session,
            user_id=str(user_id),
            filename="still-processing.pdf",
            status="processing",
        )
        db.commit()

        response = client.post(
            f"/sessions/{processing_session}/messages",
            json={"question": "Anything in here?"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
        assert "ready" in response.json()["detail"].lower()
        assert _message_count(db, processing_session) == 0
    finally:
        _cleanup(db, email)


def test_ac025_irrelevant_chunks_yield_not_found_answer_with_no_citations(monkeypatch) -> None:
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)
        session_id = _create_session(token, "Irrelevant content session")

        document = _add_document(
            db, session_id=session_id, user_id=str(user_id), filename="unrelated.pdf"
        )
        chunk_vector = _vector(1)
        _add_chunk(
            db,
            document=document,
            session_id=session_id,
            content="This document is entirely about gardening tips.",
            page_number=2,
            embedding=chunk_vector,
        )
        db.commit()

        # The generation model itself (correctly) reports it found nothing
        # relevant -- the route must not fabricate a different answer, and
        # must not attach citations to a "not found" answer.
        fake_client, _ = _make_fake_client(embed_vector=chunk_vector, answer_text=NOT_FOUND_ANSWER)
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        response = client.post(
            f"/sessions/{session_id}/messages",
            json={"question": "What is the warranty period?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["content"] == NOT_FOUND_ANSWER
        assert body["citations"] == []

        assistant_message = (
            db.query(Message)
            .filter(Message.session_id == uuid.UUID(session_id), Message.role == "assistant")
            .one()
        )
        assert assistant_message.content == NOT_FOUND_ANSWER
        assert assistant_message.citations == []
    finally:
        _cleanup(db, email)


def test_ac026_missing_gemini_key_returns_clear_error_and_records_no_message(monkeypatch) -> None:
    monkeypatch.setattr("app.rag.GEMINI_API_KEY", "")

    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)
        session_id = _create_session(token, "No key session")

        document = _add_document(
            db, session_id=session_id, user_id=str(user_id), filename="doc.pdf"
        )
        _add_chunk(
            db,
            document=document,
            session_id=session_id,
            content="Some content.",
            page_number=1,
            embedding=_vector(2),
        )
        db.commit()

        before = _message_count(db, session_id)
        response = client.post(
            f"/sessions/{session_id}/messages",
            json={"question": "What does it say?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 503
        assert "gemini" in response.json()["detail"].lower()
        assert _message_count(db, session_id) == before
    finally:
        _cleanup(db, email)


def test_ac026_failing_gemini_call_returns_clear_error_and_records_no_message(monkeypatch) -> None:
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)
        session_id = _create_session(token, "Failing gemini session")

        document = _add_document(
            db, session_id=session_id, user_id=str(user_id), filename="doc.pdf"
        )
        _add_chunk(
            db,
            document=document,
            session_id=session_id,
            content="Some content.",
            page_number=1,
            embedding=_vector(3),
        )
        db.commit()

        # Simulate the embedding call itself timing out / failing repeatedly.
        fake_client, _ = _make_fake_client(embed_error=RuntimeError("simulated timeout"))
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        before = _message_count(db, session_id)
        response = client.post(
            f"/sessions/{session_id}/messages",
            json={"question": "What does it say?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 502
        assert "gemini" in response.json()["detail"].lower()
        assert _message_count(db, session_id) == before
    finally:
        _cleanup(db, email)


def test_ac029_message_history_is_returned_in_chronological_order_across_requests() -> None:
    """GET /sessions/{id}/messages returns every prior Q/A pair, with
    citations, in chronological order -- and it survives across separate
    requests (a fresh TestClient instance per call simulates a logout/login:
    the only thing carried over is the bearer token, nothing in-process)."""
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        user_id = _user_id_from_email(db, email)
        session_id = _create_session(token, "History session")

        document = _add_document(
            db, session_id=session_id, user_id=str(user_id), filename="history.pdf"
        )
        chunk = _add_chunk(
            db,
            document=document,
            session_id=session_id,
            content="The warranty lasts two years.",
            page_number=3,
            embedding=_vector(4),
        )
        db.flush()

        base = datetime.now(timezone.utc)
        # Insert out of chronological order on purpose: the route must sort by
        # created_at, not by insertion/primary-key order.
        third_q = _add_message(
            db,
            session_id=session_id,
            role="user",
            content="Third question?",
            created_at=base + timedelta(minutes=20),
        )
        third_a = _add_message(
            db,
            session_id=session_id,
            role="assistant",
            content="Third answer.",
            created_at=base + timedelta(minutes=21),
        )
        first_q = _add_message(
            db,
            session_id=session_id,
            role="user",
            content="First question?",
            created_at=base,
        )
        first_a = _add_message(
            db,
            session_id=session_id,
            role="assistant",
            content="The warranty lasts two years.",
            created_at=base + timedelta(minutes=1),
        )
        second_q = _add_message(
            db,
            session_id=session_id,
            role="user",
            content="Second question?",
            created_at=base + timedelta(minutes=10),
        )
        second_a = _add_message(
            db,
            session_id=session_id,
            role="assistant",
            content="Second answer.",
            created_at=base + timedelta(minutes=11),
        )
        db.add(
            Citation(
                message_id=first_a.id,
                document_id=document.id,
                chunk_id=chunk.id,
                page_number=3,
                snippet="The warranty lasts two years.",
            )
        )
        db.commit()

        expected_order = [
            (first_q.id, "First question?"),
            (first_a.id, "The warranty lasts two years."),
            (second_q.id, "Second question?"),
            (second_a.id, "Second answer."),
            (third_q.id, "Third question?"),
            (third_a.id, "Third answer."),
        ]

        # Two separate TestClient instances / requests, simulating a
        # logout-then-login: the only shared state is the bearer token.
        for request_client in (TestClient(app), TestClient(app)):
            response = request_client.get(
                f"/sessions/{session_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            body = response.json()
            assert [m["content"] for m in body] == [content for _, content in expected_order]
            assert [m["id"] for m in body] == [str(mid) for mid, _ in expected_order]

            first_answer_out = body[1]
            assert len(first_answer_out["citations"]) == 1
            citation_out = first_answer_out["citations"][0]
            assert citation_out["document_id"] == str(document.id)
            assert citation_out["page_number"] == 3
            assert citation_out["snippet"] == "The warranty lasts two years."

            # Every other message in this history carries no citations.
            for m in body:
                if m["id"] != str(first_a.id):
                    assert m["citations"] == []
    finally:
        _cleanup(db, email)


def test_ac030_messages_from_another_session_are_never_included() -> None:
    """GET /sessions/{id}/messages for one session never includes another
    session's messages, even when both sessions belong to the same user."""
    db = SessionLocal()
    email = _unique_email()
    try:
        token = _signup(email)
        session_a = _create_session(token, "Session A")
        session_b = _create_session(token, "Session B")

        base = datetime.now(timezone.utc)
        msg_a = _add_message(
            db,
            session_id=session_a,
            role="user",
            content="Question only in session A",
            created_at=base,
        )
        msg_b = _add_message(
            db,
            session_id=session_b,
            role="user",
            content="Question only in session B",
            created_at=base,
        )
        db.commit()

        response_a = client.get(
            f"/sessions/{session_a}/messages",
            headers={"Authorization": f"Bearer {token}"},
        )
        response_b = client.get(
            f"/sessions/{session_b}/messages",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response_a.status_code == 200
        assert response_b.status_code == 200

        ids_a = {m["id"] for m in response_a.json()}
        ids_b = {m["id"] for m in response_b.json()}

        assert ids_a == {str(msg_a.id)}
        assert ids_b == {str(msg_b.id)}
        assert str(msg_b.id) not in ids_a
        assert str(msg_a.id) not in ids_b
    finally:
        _cleanup(db, email)
