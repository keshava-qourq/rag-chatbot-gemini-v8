"""Retrieval-augmented generation: chunk retrieval + gemini-2.5-flash answer.

Used only by app.routers.sessions's POST /sessions/{id}/messages route.
Keeps retrieval (embed the question, nearest-neighbour search over this
session's *ready* document chunks) and generation (the gemini-2.5-flash call,
grounded strictly in those chunks) in one small, independently testable
module, separate from the route's HTTP/persistence concerns.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import GEMINI_API_KEY
from app.jobs import EMBEDDING_MODEL
from app.models import EMBEDDING_DIM, Document, DocumentChunk

logger = logging.getLogger(__name__)

GENERATION_MODEL = "gemini-2.5-flash"

# How many of the most similar chunks to pass as context.
TOP_K = 5

# Returned verbatim (and matched verbatim by the route to decide whether to
# attach citations) when the retrieved content does not contain the answer.
NOT_FOUND_ANSWER = "I could not find the answer to that in the attached documents."


class NoReadyDocumentsError(Exception):
    """Raised when the session has no document with status == 'ready'."""


class GenerationConfigError(Exception):
    """Raised when Gemini is not configured (missing API key)."""


class GenerationCallError(Exception):
    """Raised when a Gemini call (embedding the question, or generating the
    answer) keeps failing after retries."""


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    document: Document


def _gemini_client():
    """A configured google-genai client, or raise GenerationConfigError.

    No retry here: a missing/empty API key is a configuration problem, not a
    transient failure, so it must fail immediately (NFR-011).
    """
    if not GEMINI_API_KEY:
        raise GenerationConfigError("GEMINI_API_KEY is not configured.")
    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def _embed_question(client, question: str) -> list[float]:
    from google.genai import types as genai_types

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=genai_types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    return list(response.embeddings[0].values)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def _generate_answer(client, question: str, context: str) -> str:
    prompt = (
        "You are a helpful assistant that answers questions using ONLY the context "
        "below, extracted from the user's own uploaded documents. Do not use any "
        "outside knowledge. If the context does not contain the answer, respond "
        f'with exactly this sentence and nothing else: "{NOT_FOUND_ANSWER}"\n\n'
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    response = client.models.generate_content(model=GENERATION_MODEL, contents=prompt)
    text = (getattr(response, "text", None) or "").strip()
    return text or NOT_FOUND_ANSWER


def retrieve_chunks(db: Session, session_id: uuid.UUID, question: str) -> list[RetrievedChunk]:
    """Embed ``question`` and return the top matching chunks from this
    session's ready documents, most similar first.

    Raises NoReadyDocumentsError if the session has no ready document (in
    which case the embedding/generation models are never called).
    Raises GenerationConfigError/GenerationCallError if the question itself
    cannot be embedded.
    """
    has_ready = (
        db.query(Document)
        .filter(Document.session_id == session_id, Document.status == "ready")
        .first()
    )
    if has_ready is None:
        raise NoReadyDocumentsError("This session has no ready documents yet.")

    client = _gemini_client()
    try:
        query_vector = _embed_question(client, question)
    except Exception as exc:  # noqa: BLE001 -- tenacity already exhausted retries
        logger.exception("Failed to embed question for session %s", session_id)
        raise GenerationCallError(str(exc)) from exc

    rows = (
        db.query(DocumentChunk, Document)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(Document.session_id == session_id, Document.status == "ready")
        .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
        .limit(TOP_K)
        .all()
    )
    return [RetrievedChunk(chunk=chunk, document=document) for chunk, document in rows]


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    """Call gemini-2.5-flash with ``chunks`` as context and return its answer.

    Raises GenerationConfigError/GenerationCallError on failure; never
    fabricates an answer (NFR-011/NFR-012).
    """
    client = _gemini_client()
    context = "\n\n".join(
        f"[Source: {rc.document.filename}, page {rc.chunk.page_number}]\n{rc.chunk.content}"
        for rc in chunks
    )
    try:
        return _generate_answer(client, question, context)
    except Exception as exc:  # noqa: BLE001 -- tenacity already exhausted retries
        logger.exception("Gemini generation call failed")
        raise GenerationCallError(str(exc)) from exc
