"""Integration test for AC-022's similarity-search half: when a session has
more ready chunks than TOP_K, retrieval must actually rank by similarity to
the embedded question -- returning the closest matches first and excluding
the more dissimilar ones -- not just return an arbitrary subset or insertion
order.

backend/tests/integration/test_messages.py's AC-022/AC-023 tests each use
only one chunk per relevant session (AC-023 uses two sessions with
*identical* vectors specifically to prove session-scoping, not ranking), so
nothing anywhere proves app.rag.retrieve_chunks's
`.order_by(DocumentChunk.embedding.cosine_distance(query_vector))` actually
orders by distance. This calls the real app.rag.retrieve_chunks against the
real Postgres+pgvector database, with only app.rag._gemini_client faked (same
pattern as test_messages.py) to return a known question embedding, and more
candidate chunks than TOP_K, so both the ranking and the cutoff are exercised:
the chunk identical to the question's embedding must come back first, and a
clearly worse match must be excluded once there are more candidates than
TOP_K allows through.
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.models import EMBEDDING_DIM as DIM
from app.models import ChatSession, Document, DocumentChunk, User
from app.rag import TOP_K, retrieve_chunks


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _vector(active_index: int) -> list[float]:
    values = [0.0] * DIM
    values[active_index] = 1.0
    return values


def test_ac022_retrieval_ranks_by_similarity_and_excludes_worse_matches_beyond_top_k(
    monkeypatch,
) -> None:
    db = SessionLocal()
    try:
        user = User(email=_unique_email(), password_hash="not-a-real-hash")
        db.add(user)
        db.flush()

        session = ChatSession(user_id=user.id, name="Ranking session")
        db.add(session)
        db.flush()

        document = Document(
            session_id=session.id,
            user_id=user.id,
            filename="ranking.pdf",
            s3_key=f"sessions/{session.id}/ranking.pdf",
            size_bytes=1024,
            status="ready",
            page_count=TOP_K + 2,
        )
        db.add(document)
        db.flush()

        question_vector = _vector(0)

        # An exact match to the question's embedding...
        exact_chunk = DocumentChunk(
            document_id=document.id,
            session_id=session.id,
            chunk_index=0,
            page_number=1,
            content="EXACT MATCH chunk.",
            embedding=question_vector,
        )
        db.add(exact_chunk)

        # ...TOP_K other, moderately-related chunks, each a little further
        # from the question than the exact match but still candidates...
        moderate_chunks = []
        for i in range(TOP_K):
            vec = [0.0] * DIM
            vec[0] = 0.9
            vec[i + 1] = 0.1
            chunk = DocumentChunk(
                document_id=document.id,
                session_id=session.id,
                chunk_index=i + 1,
                page_number=i + 2,
                content=f"MODERATE MATCH chunk {i}.",
                embedding=vec,
            )
            moderate_chunks.append(chunk)
        db.add_all(moderate_chunks)

        # ...and one clearly dissimilar chunk, which with TOP_K + 1 better
        # candidates already present must be excluded from the results.
        worst_chunk = DocumentChunk(
            document_id=document.id,
            session_id=session.id,
            chunk_index=TOP_K + 1,
            page_number=TOP_K + 2,
            content="WORST MATCH chunk, totally unrelated.",
            embedding=_vector(DIM - 1),
        )
        db.add(worst_chunk)
        db.commit()

        class _Models:
            def embed_content(self, *, model, contents, config=None):
                return SimpleNamespace(embeddings=[SimpleNamespace(values=question_vector)])

        fake_client = SimpleNamespace(models=_Models())
        monkeypatch.setattr("app.rag._gemini_client", lambda: fake_client)

        results = retrieve_chunks(db, session.id, "How long is the warranty?")

        assert len(results) == TOP_K
        result_ids = [rc.chunk.id for rc in results]

        # The exact match must be ranked first.
        assert result_ids[0] == exact_chunk.id

        # The clearly worst match must not have made the cut.
        assert worst_chunk.id not in result_ids
    finally:
        db.delete(user)
        db.commit()
        db.close()
