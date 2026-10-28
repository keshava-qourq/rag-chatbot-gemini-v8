"""Integration tests proving a queued document is actually processed end to
end by a real `rq worker documents --burst` subprocess, against the real
Postgres database, the real Redis 'documents' queue and the real storage
backend -- covering US-016-3's AC-041/AC-042.

Mirrors test_worker_entrypoint.py's pattern of spawning a real worker
subprocess rather than calling app.jobs.process_document in-process, so this
actually proves the job gets *picked up and processed by a worker*, not just
that the function body works when called directly.

The google-genai client is the only thing ever faked, and only for AC-041 (the
one case that reaches it): a tiny fake `google.genai` package is written to a
temp directory and prepended to the worker subprocess's PYTHONPATH, so the
real `from google import genai` import inside app.jobs._gemini_client resolves
to the fake instead of making a real network call. Postgres, Redis and storage
are never mocked anywhere in this file. AC-042's two failure cases (a
corrupted PDF and a scanned/image-only PDF) never reach the Gemini call at
all, so the worker subprocess runs with no Gemini faking whatsoever for those.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

import app.main  # noqa: F401 -- creates the schema before this runs
from app.config import REDIS_URL
from app.database import SessionLocal
from app.main import app
from app.models import Document, DocumentChunk, User

client = TestClient(app)

PASSWORD = "".join(["Str", "ong", "Pass", "word", "1"])
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Matches app.jobs._mark_failed's exact wording for each classified failure.
CORRUPTED_MESSAGE_FRAGMENT = "could not be read as a pdf"
SCANNED_MESSAGE_FRAGMENT = "scanned or image-only"


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


def _upload(token: str, session_id: str, filename: str, data: bytes):
    return client.post(
        f"/sessions/{session_id}/documents",
        headers=_auth(token),
        files={"file": (filename, data, "application/pdf")},
    )


def _cleanup(email: str) -> None:
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


def _run_worker_burst(extra_env: dict[str, str] | None = None) -> None:
    """Drains the real 'documents' Redis queue with a real `rq worker
    documents --burst` subprocess, exactly mirroring
    test_worker_entrypoint.py's AC-039 pattern. Burst mode exits once the
    queue is empty, so this never hangs.

    A generous timeout: other integration tests may leave jobs (including
    ones for invalid fixture PDFs from test_document_upload.py) on the same
    shared queue, and this drains all of them too.
    """
    env = dict(os.environ)
    env["REDIS_URL"] = REDIS_URL
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, "-m", "rq.cli", "worker", "documents", "--burst", "--url", REDIS_URL],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _write_fake_gemini_package(tmp_path: Path, *, embedding_dim: int = 768) -> Path:
    """Writes a minimal fake `google.genai` package to a temp directory and
    returns that directory, ready to be prepended to a subprocess's
    PYTHONPATH. Standing in only for the google-genai client: it never
    touches Postgres, Redis or storage, and the real app.jobs module's
    control flow (building request kwargs, retry decorator, etc.) still runs
    unmodified -- only the network call at the bottom is replaced.
    """
    pkg_dir = tmp_path / "fake_gemini_pkg"
    genai_dir = pkg_dir / "google" / "genai"
    genai_dir.mkdir(parents=True)

    (genai_dir / "__init__.py").write_text(
        "class _Values:\n"
        "    def __init__(self, values):\n"
        "        self.values = values\n"
        "\n"
        "class _EmbedResponse:\n"
        "    def __init__(self, values):\n"
        "        self.embeddings = [_Values(values)]\n"
        "\n"
        "class _Models:\n"
        "    def embed_content(self, *, model, contents, config=None):\n"
        f"        return _EmbedResponse([1.0] + [0.0] * {embedding_dim - 1})\n"
        "    def generate_content(self, *, model, contents):\n"
        "        class _Resp:\n"
        "            text = 'stubbed answer'\n"
        "        return _Resp()\n"
        "\n"
        "class Client:\n"
        "    def __init__(self, *args, **kwargs):\n"
        "        self.models = _Models()\n"
    )
    (genai_dir / "types.py").write_text(
        "class EmbedContentConfig:\n"
        "    def __init__(self, **kwargs):\n"
        "        self.kwargs = kwargs\n"
    )
    return pkg_dir


def _valid_pdf_bytes(text: str = "Refunds within 30 days") -> bytes:
    """A minimal, genuinely valid single-page PDF with extractable text."""
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


def _corrupted_pdf_bytes() -> bytes:
    """Starts with a PDF header (passes the route's content-sniffing) but has
    no valid internal structure at all -- pypdf must raise on it."""
    return b"%PDF-1.4\n" + b"this is not a real pdf structure, just garbage bytes. " * 10


def _scanned_pdf_bytes() -> bytes:
    """A structurally valid, single blank page PDF with no extractable text
    at all -- standing in for a scanned/image-only PDF, which this pipeline
    does not OCR."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# AC-041: a valid PDF is processed end to end by a real worker and ends up
# ready, with real chunks a subsequent question can be grounded in.
# ---------------------------------------------------------------------------


def test_ac041_valid_pdf_is_processed_by_a_real_worker_and_becomes_ready_with_usable_chunks(
    monkeypatch, tmp_path
) -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Real worker session")

        upload = _upload(token, session_id, "report.pdf", _valid_pdf_bytes())
        assert upload.status_code == 200
        document_id = upload.json()["id"]
        assert upload.json()["status"] == "processing"

        fake_pkg_dir = _write_fake_gemini_package(tmp_path)
        _run_worker_burst(
            extra_env={
                "PYTHONPATH": f"{fake_pkg_dir}{os.pathsep}{os.environ.get('PYTHONPATH', '')}",
                "GEMINI_API_KEY": "fake-key-for-worker-subprocess-tests",
            }
        )

        db = SessionLocal()
        try:
            document = db.get(Document, uuid.UUID(document_id))
            assert document is not None
            assert document.status == "ready"
            assert document.error_message is None

            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).all()
            assert len(chunks) >= 1
            assert chunks[0].content.strip() != ""
            assert chunks[0].page_number == 1
        finally:
            db.close()

        # GET reflects the ready status too.
        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.status_code == 200
        [doc_out] = listing.json()
        assert doc_out["status"] == "ready"
        assert doc_out["error_message"] is None

        # A subsequent question gets a real 200 answer grounded in the real
        # chunk the worker just persisted. Only the google-genai client is
        # faked here, same as test_messages.py, now in-process for the
        # message request itself (the worker subprocess above already did
        # its own, separately-faked embedding call).
        from types import SimpleNamespace

        class _Models:
            def embed_content(self, *, model, contents, config=None):
                return SimpleNamespace(embeddings=[SimpleNamespace(values=[1.0] + [0.0] * 767)])

            def generate_content(self, *, model, contents):
                assert "Refunds within 30 days" in contents
                return SimpleNamespace(text="Refunds are accepted within 30 days.")

        fake_client = SimpleNamespace(models=_Models())
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        answer = client.post(
            f"/sessions/{session_id}/messages",
            json={"question": "What is the refund window?"},
            headers=_auth(token),
        )

        assert answer.status_code == 200
        body = answer.json()
        assert body["content"] == "Refunds are accepted within 30 days."
        assert len(body["citations"]) >= 1
        assert body["citations"][0]["document_id"] == document_id
    finally:
        _cleanup(email)


# ---------------------------------------------------------------------------
# AC-042: a corrupted PDF and a scanned/image-only PDF both end up failed,
# each with its own distinguishing, human-readable error_message. Neither
# case reaches the Gemini call, so nothing is faked for the worker here.
# ---------------------------------------------------------------------------


def test_ac042_corrupted_pdf_and_scanned_pdf_both_fail_with_distinguishing_messages() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        session_id = _create_session(token, "Real worker failure session")

        corrupted_upload = _upload(token, session_id, "corrupted.pdf", _corrupted_pdf_bytes())
        scanned_upload = _upload(token, session_id, "scanned.pdf", _scanned_pdf_bytes())
        assert corrupted_upload.status_code == 200
        assert scanned_upload.status_code == 200
        corrupted_id = corrupted_upload.json()["id"]
        scanned_id = scanned_upload.json()["id"]

        # Neither case ever reaches the google-genai client, so the worker
        # subprocess runs here with no faking at all -- only Postgres, Redis
        # and storage, all real.
        _run_worker_burst()

        db = SessionLocal()
        try:
            corrupted_doc = db.get(Document, uuid.UUID(corrupted_id))
            scanned_doc = db.get(Document, uuid.UUID(scanned_id))

            assert corrupted_doc.status == "failed"
            assert corrupted_doc.error_message is not None
            assert CORRUPTED_MESSAGE_FRAGMENT in corrupted_doc.error_message.lower()

            assert scanned_doc.status == "failed"
            assert scanned_doc.error_message is not None
            assert SCANNED_MESSAGE_FRAGMENT in scanned_doc.error_message.lower()

            # The two messages genuinely distinguish the cases from one another.
            assert corrupted_doc.error_message != scanned_doc.error_message

            # No chunks were ever created for either failed document.
            assert (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == corrupted_doc.id)
                .count()
                == 0
            )
            assert (
                db.query(DocumentChunk).filter(DocumentChunk.document_id == scanned_doc.id).count()
                == 0
            )
        finally:
            db.close()

        listing = client.get(f"/sessions/{session_id}/documents", headers=_auth(token))
        assert listing.status_code == 200
        by_id = {d["id"]: d for d in listing.json()}

        assert by_id[corrupted_id]["status"] == "failed"
        assert CORRUPTED_MESSAGE_FRAGMENT in by_id[corrupted_id]["error_message"].lower()

        assert by_id[scanned_id]["status"] == "failed"
        assert SCANNED_MESSAGE_FRAGMENT in by_id[scanned_id]["error_message"].lower()
    finally:
        _cleanup(email)
