"""Background job enqueue and body for document processing.

The job fetches the uploaded PDF (app.storage.load), parses and chunks it
(app.document_processing), and classifies failure so Document.status ends up
'failed' with a clear error_message rather than the pipeline silently
continuing (AC-020). Embedding and DocumentChunk persistence are out of scope
here (US-008-3): this stage never writes DocumentChunk rows.
"""

from __future__ import annotations

import logging
import uuid

import redis
from rq import Queue
from rq.exceptions import DuplicateJobError
from sqlalchemy.orm import Session

from app.config import REDIS_URL
from app.database import SessionLocal
from app.document_processing import CorruptedPDFError, NoExtractableTextError, chunk_pdf_bytes
from app.models import Document
from app.storage import load

logger = logging.getLogger(__name__)

_redis_conn: redis.Redis | None = None


def _queue() -> Queue:
    global _redis_conn
    if _redis_conn is None:
        _redis_conn = redis.from_url(REDIS_URL)
    return Queue("documents", connection=_redis_conn)


def _mark_failed(db: Session, doc: Document, message: str) -> None:
    doc.status = "failed"
    doc.error_message = message
    db.commit()


def process_document(document_id: str) -> None:
    """The job body: fetch, parse and chunk a document's PDF.

    Idempotent: a document already 'ready' or 'failed' is left untouched, so
    running this job twice (at-least-once delivery) never reprocesses or
    duplicates work. Status stays 'processing' for the duration of parsing;
    only a classified failure here flips it to 'failed'. Writing
    DocumentChunk rows (with embeddings) is a later stage's job.
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
            chunk_pdf_bytes(data)
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

        # Chunking succeeded; embedding + persistence is US-008-3's scope.
        # Status intentionally stays 'processing' here.
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
