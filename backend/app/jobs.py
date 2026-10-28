"""Background job enqueue and body for document processing.

The job fetches the uploaded PDF (app.storage.load), parses and chunks it
(app.document_processing), embeds each chunk via gemini-embedding-001 (the
google-genai SDK) and persists DocumentChunk rows, then flips Document.status
to 'ready'. Any classified failure along the way -- a corrupted/empty PDF, a
missing/invalid Gemini configuration, or a Gemini call that keeps failing
after retries -- flips it to 'failed' with a clear error_message instead
(AC-017..AC-021).
"""

from __future__ import annotations

import logging
import uuid

import redis
from rq import Queue
from rq.exceptions import DuplicateJobError
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import GEMINI_API_KEY, REDIS_URL
from app.database import SessionLocal
from app.document_processing import CorruptedPDFError, NoExtractableTextError, chunk_pdf_bytes
from app.models import Document, DocumentChunk, EMBEDDING_DIM
from app.storage import load

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "gemini-embedding-001"

_redis_conn: redis.Redis | None = None


class EmbeddingConfigError(Exception):
    """Raised when Gemini is not configured (missing API key)."""


class EmbeddingCallError(Exception):
    """Raised when the Gemini embedding call keeps failing after retries."""


def _queue() -> Queue:
    global _redis_conn
    if _redis_conn is None:
        _redis_conn = redis.from_url(REDIS_URL)
    return Queue("documents", connection=_redis_conn)


def _mark_failed(db: Session, doc: Document, message: str) -> None:
    doc.status = "failed"
    doc.error_message = message
    db.commit()


def _gemini_client():
    """A configured google-genai client, or raise EmbeddingConfigError.

    No retry here: an empty/missing API key is a configuration problem, not a
    transient failure, so it must fail immediately (NFR-011).
    """
    if not GEMINI_API_KEY:
        raise EmbeddingConfigError("GEMINI_API_KEY is not configured.")
    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def _embed_text(client, text: str) -> list[float]:
    """Embed a single chunk's text via gemini-embedding-001, retried on transient errors."""
    from google.genai import types as genai_types

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=genai_types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    return list(response.embeddings[0].values)


def _embed_chunks(client, chunks) -> list[list[float]]:
    try:
        return [_embed_text(client, chunk.content) for chunk in chunks]
    except Exception as exc:  # noqa: BLE001 -- tenacity already exhausted retries
        raise EmbeddingCallError(str(exc)) from exc


def process_document(document_id: str) -> None:
    """The job body: fetch, parse, chunk, embed and persist a document's chunks.

    Idempotent: a document already 'ready' or 'failed' is left untouched. Any
    DocumentChunk rows left over from a previous, partially-failed attempt are
    cleared before re-embedding, so re-running this job never duplicates rows.
    No exception escapes this function: every known failure mode is classified
    and turned into a 'failed' status with an explanatory message, and any
    other unexpected error is caught, logged and also marked 'failed' rather
    than crashing the worker (NFR-011).
    """
    db = SessionLocal()
    try:
        doc = db.get(Document, uuid.UUID(document_id))
        if doc is None:
            return
        if doc.status in ("ready", "failed"):
            return

        try:
            data = load(doc.s3_key)
        except Exception as exc:  # noqa: BLE001 -- any storage failure is unrecoverable here
            logger.exception("Failed to load document %s from storage", document_id)
            _mark_failed(db, doc, f"Could not read the uploaded file: {exc}")
            return

        try:
            chunks = chunk_pdf_bytes(data)
        except CorruptedPDFError as exc:
            logger.warning("Document %s is corrupted: %s", document_id, exc)
            _mark_failed(
                db,
                doc,
                "This file could not be read as a PDF. It may be corrupted; "
                "please re-export it and upload again.",
            )
            return
        except NoExtractableTextError as exc:
            logger.warning("Document %s has no extractable text: %s", document_id, exc)
            _mark_failed(
                db,
                doc,
                "No text could be extracted from this PDF. It appears to be a scanned "
                "or image-only document, which is not currently supported.",
            )
            return

        try:
            client = _gemini_client()
        except EmbeddingConfigError as exc:
            logger.warning("Document %s: Gemini is not configured: %s", document_id, exc)
            _mark_failed(
                db,
                doc,
                "Embeddings could not be generated because the Gemini API is not "
                "configured. Please contact an administrator.",
            )
            return

        # Idempotency: drop any DocumentChunk rows a previous, partially-failed
        # attempt may have left behind before re-embedding from scratch.
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
        db.commit()

        try:
            vectors = _embed_chunks(client, chunks)
        except EmbeddingCallError as exc:
            logger.exception("Document %s: embedding call failed after retries: %s", document_id, exc)
            _mark_failed(
                db,
                doc,
                "Embeddings could not be generated because the Gemini API call failed "
                "after several attempts. Please try again later.",
            )
            return

        for chunk, vector in zip(chunks, vectors, strict=True):
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    session_id=doc.session_id,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    embedding=vector,
                )
            )

        doc.status = "ready"
        doc.error_message = None
        db.commit()
    except Exception as exc:  # noqa: BLE001 -- last-resort safety net, see NFR-011
        logger.exception("Unexpected error processing document %s: %s", document_id, exc)
        try:
            doc = db.get(Document, uuid.UUID(document_id))
            if doc is not None and doc.status not in ("ready", "failed"):
                _mark_failed(db, doc, "An unexpected error occurred while processing this document.")
        except Exception:  # noqa: BLE001 -- do not let the safety net itself crash the worker
            logger.exception("Failed to mark document %s as failed", document_id)
    finally:
        db.close()


def enqueue_document_processing(document_id: uuid.UUID) -> None:
    """Queue ``document_id`` for processing.

    Keyed by a deterministic job id derived from the document id, so calling
    this twice for the same document never double-queues it (jobs must be
    safe to run twice).
    """
    job_id = f"process-document-{document_id}"
    try:
        _queue().enqueue(process_document, str(document_id), job_id=job_id, unique=True)
    except DuplicateJobError:
        pass
