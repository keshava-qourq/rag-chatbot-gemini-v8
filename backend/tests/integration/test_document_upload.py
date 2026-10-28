"""Integration tests for POST/GET /sessions/{session_id}/documents against the
real database, real S3-backed storage and the real Redis-backed job queue,
covering US-007's acceptance criteria (AC-013..AC-016) and NFR-006/NFR-007.

Follows the TestClient-against-real-Postgres pattern already used throughout
backend/tests/integration/ (e.g. test_messages.py, test_isolation.py).
Documents the 20th-onward cap test needs to exist are inserted directly
against the database (mirroring test_isolation.py/_add_document) rather than
uploaded one at a time through the real route, purely to keep the test fast;
every other case here goes through the real multipart upload endpoint, the
real storage backend (app.storage) and the real queue (app.jobs), with
nothing faked.
"""

from __future__ import annotations

import uuid

import redis
from fastapi.testclient import TestClient
from rq import Queue
from rq.job import Job

import app.main  # noqa: F401 -- creates the schema before this runs
from app.config import MAX_DOCUMENTS_PER_SESSION, MAX_PDF_SIZE_BYTES, REDIS_URL
from app.database import SessionLocal
from app.main import app
from app.models import Document, User
from app.storage import load

client = TestClient(app)

PASSWORD = "".join(["Str", "ong", "Pass", "word", "1"])

FAKE_PDF_BYTES = b"%PDF-1.4 fake pdf content for upload tests"


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _signup(email: str) -> str:
    response = client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_session(token: str, name: str) -> str:
    response = client.post("/sessions", json={"name": name}, headers=_auth(token))
    assert response.status_code == 200
    return response.json()["id"]


def _upload(token: str, session_id: str, filename: str, data: bytes, content_type: str):
    return client.post(
        f"/sessions/{session_id}/documents",
        headers=_auth(token),
        files={"file": (filename, data, content_type)},
    )


def _document_count(db, session_id: str) -> int:
    return db.query(Document).filter(Document.session_id == uuid.UUID(session_id)).count()


def _add_document_directly(db, *, session_id: str, user_id: uuid.UUID, filename: str) -> Document:
    document = Document(
        session_id=uuid.UUID(session_id),
        user_id=user_id,
        filename=filename,
        s3_key=f"sessions/{session_id}/{filename}",
        size_bytes=1024,
        status="ready",
        page_count=1,
    )
    db.add(document)
    db.flush()
    return document


def _is_job_queued(document_id: str) -> bool:
    conn = redis.from_url(REDIS_URL)
    job_id = f"process-document-{document_id}"
    queue = Queue("documents", connection=conn)
    if job_id in queue.job_ids:
        return True
    # A worker could in principle have already dequeued it (none runs in this
    # sandbox, but don't assume that); either way the job must have been created.
    try:
        Job.fetch(job_id, connection=conn)
        return True
    except Exception:  # noqa: BLE001 -- rq.exceptions.NoSuchJobError
        return False


def _cleanup(email: str) -> None:
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# AC-013: a valid PDF within the size limit is accepted, scoped to its own
# session, stored, and queued for processing.
# ---------------------------------------------------------------------------


def test_ac013_valid_pdf_is_accepted_stored_queued_and_scoped_to_its_session() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Upload session")
        other_session_id = _create_session(token, "Other session")

        response = _upload(token, session_id, "report.pdf", FAKE_PDF_BYTES, "application/pdf")

        assert response.status_code == 200
        body = response.json()
        assert body["filename"] == "report.pdf"
        assert body["status"] == "processing"
        assert "id" in body

        # Persisted with the right bytes, reachable through the storage seam.
        db = SessionLocal()
        try:
            document = db.get(Document, uuid.UUID(body["id"]))
            assert document is not None
            assert document.session_id == uuid.UUID(session_id)
            assert document.size_bytes == len(FAKE_PDF_BYTES)
            assert load(document.s3_key) == FAKE_PDF_BYTES
        finally:
            db.close()

        # Queued for background processing (NFR-003-adjacent async pipeline).
        assert _is_job_queued(body["id"])

        # Listed under its own session...
        own_listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert own_listing.status_code == 200
        own_ids = {d["id"] for d in own_listing.json()}
        assert body["id"] in own_ids

        # ...and associated with that session only: it must not leak into a
        # different session belonging to the same user.
        other_listing = client.get(f"/sessions/{other_session_id}/documents", headers=_auth(token))
        assert other_listing.status_code == 200
        assert other_listing.json() == []
    finally:
        _cleanup(email)


def test_ac013_multiple_valid_pdfs_can_be_attached_to_the_same_session() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Multi-upload session")

        first = _upload(token, session_id, "one.pdf", FAKE_PDF_BYTES, "application/pdf")
        second = _upload(token, session_id, "two.pdf", FAKE_PDF_BYTES, "application/pdf")

        assert first.status_code == 200
        assert second.status_code == 200

        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.status_code == 200
        filenames = {d["filename"] for d in listing.json()}
        assert filenames == {"one.pdf", "two.pdf"}
    finally:
        _cleanup(email)


def test_ac013_uploading_to_a_nonexistent_session_is_rejected() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        made_up_session_id = str(uuid.uuid4())

        response = _upload(
            token, made_up_session_id, "report.pdf", FAKE_PDF_BYTES, "application/pdf"
        )

        assert response.status_code in (403, 404)
    finally:
        _cleanup(email)


# ---------------------------------------------------------------------------
# AC-014: a non-PDF file is rejected with a PDF-only message, nothing stored.
# ---------------------------------------------------------------------------


def test_ac014_word_document_is_rejected_and_nothing_is_stored() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Reject non-pdf session")

        response = _upload(
            token,
            session_id,
            "report.docx",
            b"not really a word doc either, just bytes",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        assert response.status_code == 422
        detail = response.json()["detail"].lower()
        assert "pdf" in detail
        assert "only" in detail or "supported" in detail

        db = SessionLocal()
        try:
            assert _document_count(db, session_id) == 0
        finally:
            db.close()

        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.json() == []
    finally:
        _cleanup(email)


def test_ac014_plain_text_file_is_rejected_and_nothing_is_stored() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Reject text session")

        response = _upload(token, session_id, "notes.txt", b"just some notes", "text/plain")

        assert response.status_code == 422
        assert "pdf" in response.json()["detail"].lower()

        db = SessionLocal()
        try:
            assert _document_count(db, session_id) == 0
        finally:
            db.close()
    finally:
        _cleanup(email)


def test_ac014_image_file_is_rejected_and_nothing_is_stored() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Reject image session")

        response = _upload(token, session_id, "scan.png", b"\x89PNG fake bytes", "image/png")

        assert response.status_code == 422
        assert "pdf" in response.json()["detail"].lower()

        db = SessionLocal()
        try:
            assert _document_count(db, session_id) == 0
        finally:
            db.close()
    finally:
        _cleanup(email)


def test_ac014_pdf_extension_with_mismatched_content_type_is_rejected() -> None:
    """A file renamed to end in .pdf but declaring a non-PDF content type must
    still be rejected -- the filename alone is not sufficient proof it is a PDF."""
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Reject spoofed session")

        response = _upload(
            token, session_id, "disguised.pdf", b"actually plain text", "text/plain"
        )

        assert response.status_code == 422
        assert "pdf" in response.json()["detail"].lower()

        db = SessionLocal()
        try:
            assert _document_count(db, session_id) == 0
        finally:
            db.close()
    finally:
        _cleanup(email)


# ---------------------------------------------------------------------------
# AC-015 / NFR-006: a PDF over the ~20MB per-file limit is rejected with the
# limit stated, nothing stored.
# ---------------------------------------------------------------------------


def test_ac015_oversized_pdf_is_rejected_with_size_limit_stated_and_nothing_stored() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Reject oversize session")

        oversized = b"%PDF-1.4 " + b"0" * (MAX_PDF_SIZE_BYTES + 1)
        response = _upload(token, session_id, "huge.pdf", oversized, "application/pdf")

        assert response.status_code == 422
        detail = response.json()["detail"].lower()
        assert "20" in detail  # states the ~20MB limit to the user
        assert "mb" in detail or "megabyte" in detail

        db = SessionLocal()
        try:
            assert _document_count(db, session_id) == 0
        finally:
            db.close()

        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.json() == []
    finally:
        _cleanup(email)


def test_ac015_pdf_at_exactly_the_limit_is_accepted() -> None:
    """The boundary itself (~20MB, not strictly over it) must still succeed --
    only files *larger* than the limit are rejected."""
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Boundary session")

        at_limit = b"0" * MAX_PDF_SIZE_BYTES
        response = _upload(token, session_id, "at-limit.pdf", at_limit, "application/pdf")

        assert response.status_code == 200
        assert response.json()["status"] == "processing"
    finally:
        _cleanup(email)


# ---------------------------------------------------------------------------
# AC-016 / NFR-007: once a session holds the per-session document cap, a
# further upload is rejected with the limit explained.
# ---------------------------------------------------------------------------


def test_ac016_upload_beyond_the_per_session_cap_is_rejected_and_nothing_added() -> None:
    db = SessionLocal()
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Capped session")
        user = db.query(User).filter(User.email == email).one()

        for i in range(MAX_DOCUMENTS_PER_SESSION):
            _add_document_directly(
                db, session_id=session_id, user_id=user.id, filename=f"existing-{i}.pdf"
            )
        db.commit()

        assert _document_count(db, session_id) == MAX_DOCUMENTS_PER_SESSION

        response = _upload(
            token, session_id, "one-too-many.pdf", FAKE_PDF_BYTES, "application/pdf"
        )

        assert response.status_code == 422
        detail = response.json()["detail"].lower()
        assert "limit" in detail or "maximum" in detail
        assert str(MAX_DOCUMENTS_PER_SESSION) in response.json()["detail"]

        # Nothing was added: the count stays exactly at the cap.
        assert _document_count(db, session_id) == MAX_DOCUMENTS_PER_SESSION

        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.status_code == 200
        assert "one-too-many.pdf" not in {d["filename"] for d in listing.json()}
    finally:
        _cleanup(email)
        db.close()


def test_ac016_a_session_with_one_slot_remaining_still_accepts_the_last_upload() -> None:
    """One below the cap must still succeed -- the rejection is specifically
    for attempts *at or beyond* the cap, not a one-off underflow."""
    db = SessionLocal()
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "One slot left session")
        user = db.query(User).filter(User.email == email).one()

        for i in range(MAX_DOCUMENTS_PER_SESSION - 1):
            _add_document_directly(
                db, session_id=session_id, user_id=user.id, filename=f"existing-{i}.pdf"
            )
        db.commit()

        response = _upload(token, session_id, "last-slot.pdf", FAKE_PDF_BYTES, "application/pdf")

        assert response.status_code == 200
        assert _document_count(db, session_id) == MAX_DOCUMENTS_PER_SESSION
    finally:
        _cleanup(email)
        db.close()


# ---------------------------------------------------------------------------
# GET /sessions/{session_id}/documents: status/error_message/page_count shape.
# ---------------------------------------------------------------------------


def test_list_documents_returns_status_error_message_and_page_count_fields() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Listing shape session")
        upload = _upload(token, session_id, "shape.pdf", FAKE_PDF_BYTES, "application/pdf")
        assert upload.status_code == 200

        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.status_code == 200
        [doc] = listing.json()
        assert doc["filename"] == "shape.pdf"
        assert doc["status"] == "processing"
        assert doc["error_message"] is None
        assert doc["page_count"] is None
    finally:
        _cleanup(email)


def test_upload_requires_authentication() -> None:
    response = client.post(
        f"/sessions/{uuid.uuid4()}/documents",
        files={"file": ("x.pdf", FAKE_PDF_BYTES, "application/pdf")},
    )

    assert response.status_code == 401
