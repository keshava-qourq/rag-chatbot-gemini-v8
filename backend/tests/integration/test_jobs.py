"""Integration tests for app.jobs.process_document and
app.jobs.enqueue_document_processing against the real database and the real
Redis-backed 'documents' queue, covering US-008's AC-018/AC-019/AC-021 and
the job's own idempotency contract ("jobs must be safe to run twice").

backend/tests/integration/test_worker_processing.py already proves the full
pipeline end to end through a real `rq worker --burst` subprocess for a valid
PDF (AC-041) and for a corrupted/scanned PDF (AC-042), but never exercises a
missing/invalid GEMINI_API_KEY (AC-021) or idempotent re-processing anywhere.
This file calls app.jobs.process_document directly (in-process, the same
pattern test_models.py and test_messages.py already use for direct model/
service access) against the real database, with only the google-genai client
faked where a test needs to simulate a Gemini failure -- Postgres and the
Redis queue are never mocked.
"""

from __future__ import annotations

import io
import logging
import uuid

import redis
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from rq import Queue
from sqlalchemy import select

import app.main  # noqa: F401 -- creates the schema before this runs
from app.config import REDIS_URL
from app.database import SessionLocal
from app.jobs import enqueue_document_processing, process_document
from app.models import Document, DocumentChunk, User
from app.storage import make_key, save


def _valid_pdf_bytes(text: str = "Some real extractable content here") -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)

    stream_obj = DecodedStreamObject()
    stream_obj.set_data(f"BT /F1 24 Tf 10 100 Td ({text}) Tj ET".encode())
    stream_ref = writer._add_object(stream_obj)

    font = DictionaryObject()
    font[NameObject("/Type")] = NameObject("/Font")
    font[NameObject("/Subtype")] = NameObject("/Type1")
    font[NameObject("/BaseFont")] = NameObject("/Helvetica")
    font_ref = writer._add_object(font)

    resources = DictionaryObject()
    font_dict = DictionaryObject()
    font_dict[NameObject("/F1")] = font_ref
    resources[NameObject("/Font")] = font_dict
    page[NameObject("/Resources")] = resources
    page[NameObject("/Contents")] = stream_ref

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _make_user_session_and_document(db) -> tuple[User, uuid.UUID, Document]:
    """Builds a real user, session and a 'processing' document whose bytes
    are genuinely saved through app.storage, without going through the HTTP
    upload route (keeping this file's scope to app.jobs, not app.routers)."""
    from app.models import ChatSession

    user = User(email=_unique_email(), password_hash="not-a-real-hash")
    db.add(user)
    db.flush()

    session = ChatSession(user_id=user.id, name="Job test session")
    db.add(session)
    db.flush()

    key = make_key(str(session.id), "job-test.pdf")
    save(key, _valid_pdf_bytes())

    document = Document(
        session_id=session.id,
        user_id=user.id,
        filename="job-test.pdf",
        s3_key=key,
        size_bytes=100,
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return user, session.id, document


def _cleanup(db, user: User) -> None:
    db.delete(user)
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# AC-018: while processing, status stays 'processing' and nothing is queryable.
# ---------------------------------------------------------------------------


def test_ac018_document_starts_processing_with_no_chunks_before_the_job_runs() -> None:
    db = SessionLocal()
    user, _session_id, document = _make_user_session_and_document(db)
    try:
        assert document.status == "processing"
        chunks = (
            db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document.id))
            .scalars()
            .all()
        )
        assert chunks == []
    finally:
        _cleanup(db, user)


# ---------------------------------------------------------------------------
# AC-021: a missing/invalid GEMINI_API_KEY fails the document gracefully with
# a configuration-related error, logged, and no chunks persisted.
# ---------------------------------------------------------------------------


def test_ac021_missing_gemini_api_key_marks_document_failed_with_configuration_error(
    monkeypatch, caplog
) -> None:
    monkeypatch.setattr("app.jobs.GEMINI_API_KEY", "")

    db = SessionLocal()
    user, _session_id, document = _make_user_session_and_document(db)
    try:
        with caplog.at_level(logging.WARNING, logger="app.jobs"):
            process_document(str(document.id))

        db.refresh(document)
        assert document.status == "failed"
        assert document.error_message is not None
        assert "gemini" in document.error_message.lower()
        assert "configur" in document.error_message.lower()

        # The failure is logged (AC-021), not just silently recorded in the DB.
        assert any(
            str(document.id) in record.message and "not configured" in record.message.lower()
            for record in caplog.records
        )

        chunks = (
            db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document.id))
            .scalars()
            .all()
        )
        assert chunks == []
    finally:
        _cleanup(db, user)


def test_ac021_failing_embedding_call_marks_document_failed_after_retries(monkeypatch) -> None:
    from types import SimpleNamespace

    class _Models:
        def embed_content(self, *, model, contents, config=None):
            raise RuntimeError("simulated persistent embedding failure")

    fake_client = SimpleNamespace(models=_Models())
    monkeypatch.setattr("app.jobs._gemini_client", lambda: fake_client)

    db = SessionLocal()
    user, _session_id, document = _make_user_session_and_document(db)
    try:
        process_document(str(document.id))

        db.refresh(document)
        assert document.status == "failed"
        assert document.error_message is not None
        assert "gemini" in document.error_message.lower()

        chunks = (
            db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document.id))
            .scalars()
            .all()
        )
        assert chunks == []
    finally:
        _cleanup(db, user)


# ---------------------------------------------------------------------------
# AC-019: processing completes successfully -> 'ready', chunks persisted.
# ---------------------------------------------------------------------------


def test_ac019_successful_processing_marks_ready_and_persists_chunks(monkeypatch) -> None:
    from types import SimpleNamespace

    from app.models import EMBEDDING_DIM

    class _Models:
        def embed_content(self, *, model, contents, config=None):
            return SimpleNamespace(
                embeddings=[SimpleNamespace(values=[1.0] + [0.0] * (EMBEDDING_DIM - 1))]
            )

    fake_client = SimpleNamespace(models=_Models())
    monkeypatch.setattr("app.jobs._gemini_client", lambda: fake_client)

    db = SessionLocal()
    user, _session_id, document = _make_user_session_and_document(db)
    try:
        process_document(str(document.id))

        db.refresh(document)
        assert document.status == "ready"
        assert document.error_message is None
        assert document.page_count == 1

        chunks = (
            db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document.id))
            .scalars()
            .all()
        )
        assert len(chunks) >= 1
        assert chunks[0].content.strip() != ""
    finally:
        _cleanup(db, user)


# ---------------------------------------------------------------------------
# "Jobs must be safe to run twice": process_document is idempotent.
# ---------------------------------------------------------------------------


def test_process_document_is_a_no_op_once_already_ready(monkeypatch) -> None:
    from types import SimpleNamespace

    from app.models import EMBEDDING_DIM

    call_count = {"n": 0}

    class _Models:
        def embed_content(self, *, model, contents, config=None):
            call_count["n"] += 1
            return SimpleNamespace(
                embeddings=[SimpleNamespace(values=[1.0] + [0.0] * (EMBEDDING_DIM - 1))]
            )

    fake_client = SimpleNamespace(models=_Models())
    monkeypatch.setattr("app.jobs._gemini_client", lambda: fake_client)

    db = SessionLocal()
    user, _session_id, document = _make_user_session_and_document(db)
    try:
        process_document(str(document.id))
        db.refresh(document)
        assert document.status == "ready"
        first_call_count = call_count["n"]
        chunk_ids_first_run = {
            c.id
            for c in db.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == document.id)
            )
            .scalars()
            .all()
        }

        # Re-running the job body for an already-'ready' document (e.g. a
        # worker crash that re-delivers the same job) must not call Gemini
        # again or touch the persisted chunks.
        process_document(str(document.id))

        db.refresh(document)
        assert document.status == "ready"
        assert call_count["n"] == first_call_count

        chunk_ids_second_run = {
            c.id
            for c in db.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == document.id)
            )
            .scalars()
            .all()
        }
        assert chunk_ids_second_run == chunk_ids_first_run
    finally:
        _cleanup(db, user)


def test_process_document_is_a_no_op_once_already_failed(monkeypatch) -> None:
    monkeypatch.setattr("app.jobs.GEMINI_API_KEY", "")

    db = SessionLocal()
    user, _session_id, document = _make_user_session_and_document(db)
    try:
        process_document(str(document.id))
        db.refresh(document)
        assert document.status == "failed"
        first_error_message = document.error_message

        # Re-running must not flip it back to 'processing' or change the message.
        process_document(str(document.id))
        db.refresh(document)
        assert document.status == "failed"
        assert document.error_message == first_error_message
    finally:
        _cleanup(db, user)


def test_enqueue_document_processing_does_not_double_queue_the_same_document() -> None:
    """Calling enqueue twice for the same document id must result in exactly
    one job on the real Redis queue, keyed by the deterministic job id."""
    document_id = uuid.uuid4()
    conn = redis.from_url(REDIS_URL)
    queue = Queue("documents", connection=conn)
    job_id = f"process-document-{document_id}"

    # Ensure a clean slate even if a previous failed run left this id behind
    # (vanishingly unlikely given the random uuid, but keeps this test honest).
    existing = queue.fetch_job(job_id)
    if existing is not None:
        existing.delete()

    try:
        enqueue_document_processing(document_id)
        first_job = queue.fetch_job(job_id)
        assert first_job is not None

        enqueue_document_processing(document_id)
        second_job = queue.fetch_job(job_id)

        assert second_job is not None
        assert second_job.id == first_job.id
        # Still only reachable under the one deterministic job id -- no
        # second, differently-keyed job was created for the same document.
        assert queue.job_ids.count(job_id) <= 1
    finally:
        job = queue.fetch_job(job_id)
        if job is not None:
            job.delete()
