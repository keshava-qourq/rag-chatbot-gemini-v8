"""Background job enqueue for document processing.

The worker that actually parses a PDF, chunks and embeds it is a later
ticket's scope (US-008). This module only owns the queue connection and a
minimal, idempotent enqueue call keyed by document id, so the upload route
never does heavy work inline (NFR-016).
"""

from __future__ import annotations

import uuid

import redis
from rq import Queue
from rq.exceptions import DuplicateJobError

from app.config import REDIS_URL

_redis_conn: redis.Redis | None = None


def _queue() -> Queue:
    global _redis_conn
    if _redis_conn is None:
        _redis_conn = redis.from_url(REDIS_URL)
    return Queue("documents", connection=_redis_conn)


def process_document(document_id: str) -> None:
    """The job body. Intentionally a no-op placeholder here.

    PDF parsing, chunking and embedding are US-008's scope; this function
    exists only so there is something importable for rq to run, and it must
    stay safe to run twice once it does real work.
    """


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
