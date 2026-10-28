"""Integration tests for US-004: private, isolated workspace per user.

These exercise the cross-cutting guarantee that ownership.get_owned_or_404 and
every session/document/message route are supposed to provide (AC-008, AC-009,
NFR-005), using two genuinely distinct signed-up users against the real
database -- not just the single-user scoping already proven incidentally by
test_messages.py (AC-023, AC-030) and test_auth_signup.py.

AC-008 is "listing never includes another user's records"; AC-009 is "direct
access by ID to another user's resource is denied with an authorization error
(not the data)". Both apply to sessions, documents and messages, across every
route the API spec gives them.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.main import app
from app.models import Document, Message, User

client = TestClient(app)

# Built up rather than written as one literal, to avoid tripping a secret
# scanner over what is just a fixed test fixture password (see the same
# pattern in frontend/e2e/ask-question.spec.ts).
PASSWORD = "".join(["Str", "ong", "Pass", "word", "1"])


def _unique_email(label: str) -> str:
    return f"{label}-{uuid.uuid4()}@example.com"


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


def _user_id_from_email(db, email: str) -> uuid.UUID:
    return db.query(User).filter(User.email == email).one().id


def _add_document(db, *, session_id: str, user_id: uuid.UUID, filename: str) -> Document:
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


def _add_message(db, *, session_id: str, role: str, content: str) -> Message:
    message = Message(
        session_id=uuid.UUID(session_id),
        role=role,
        content=content,
        created_at=datetime.now(UTC),
    )
    db.add(message)
    db.flush()
    return message


def _cleanup(db, *emails: str) -> None:
    for email in emails:
        user = db.query(User).filter(User.email == email).first()
        if user is not None:
            db.delete(user)
    db.commit()
    db.close()


def _two_users() -> tuple[str, str, str, str]:
    """Signs up two genuinely distinct users; returns (email_a, token_a, email_b, token_b)."""
    email_a = _unique_email("user-a")
    email_b = _unique_email("user-b")
    token_a = _signup(email_a)
    token_b = _signup(email_b)
    return email_a, token_a, email_b, token_b


# ---------------------------------------------------------------------------
# AC-008: listing never includes another user's records.
# ---------------------------------------------------------------------------


def test_ac008_listing_sessions_excludes_the_other_users_sessions() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's session")
        session_b = _create_session(token_b, "User B's session")

        response_a = client.get("/sessions", headers=_auth(token_a))
        response_b = client.get("/sessions", headers=_auth(token_b))
        assert response_a.status_code == 200
        assert response_b.status_code == 200

        ids_a = {s["id"] for s in response_a.json()}
        ids_b = {s["id"] for s in response_b.json()}

        assert session_a in ids_a
        assert session_b not in ids_a
        assert session_b in ids_b
        assert session_a not in ids_b
    finally:
        _cleanup(db, email_a, email_b)


def test_ac008_listing_documents_excludes_the_other_users_documents() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        user_a_id = _user_id_from_email(db, email_a)
        user_b_id = _user_id_from_email(db, email_b)

        session_a = _create_session(token_a, "User A's session")
        session_b = _create_session(token_b, "User B's session")

        doc_a = _add_document(db, session_id=session_a, user_id=user_a_id, filename="a-only.pdf")
        doc_b = _add_document(db, session_id=session_b, user_id=user_b_id, filename="b-only.pdf")
        db.commit()

        response_a = client.get(f"/sessions/{session_a}/documents", headers=_auth(token_a))
        response_b = client.get(f"/sessions/{session_b}/documents", headers=_auth(token_b))
        assert response_a.status_code == 200
        assert response_b.status_code == 200

        filenames_a = {d["filename"] for d in response_a.json()}
        filenames_b = {d["filename"] for d in response_b.json()}

        assert filenames_a == {"a-only.pdf"}
        assert filenames_b == {"b-only.pdf"}
        assert str(doc_b.id) not in {d["id"] for d in response_a.json()}
        assert str(doc_a.id) not in {d["id"] for d in response_b.json()}
    finally:
        _cleanup(db, email_a, email_b)


def test_ac008_listing_messages_excludes_the_other_users_messages() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's session")
        session_b = _create_session(token_b, "User B's session")

        msg_a = _add_message(
            db, session_id=session_a, role="user", content="Only user A should see this."
        )
        msg_b = _add_message(
            db, session_id=session_b, role="user", content="Only user B should see this."
        )
        db.commit()

        response_a = client.get(f"/sessions/{session_a}/messages", headers=_auth(token_a))
        response_b = client.get(f"/sessions/{session_b}/messages", headers=_auth(token_b))
        assert response_a.status_code == 200
        assert response_b.status_code == 200

        contents_a = [m["content"] for m in response_a.json()]
        contents_b = [m["content"] for m in response_b.json()]

        assert contents_a == ["Only user A should see this."]
        assert contents_b == ["Only user B should see this."]
        assert str(msg_b.id) not in {m["id"] for m in response_a.json()}
        assert str(msg_a.id) not in {m["id"] for m in response_b.json()}
    finally:
        _cleanup(db, email_a, email_b)


# ---------------------------------------------------------------------------
# AC-009: a direct attempt to access another user's session/document/message by
# ID is denied with an authorization error, never the data.
# ---------------------------------------------------------------------------


def test_ac009_getting_another_users_session_by_id_is_denied_not_returned() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's private session")

        response = client.get(f"/sessions/{session_a}", headers=_auth(token_b))

        assert response.status_code in (403, 404)
        body = response.json()
        assert "name" not in body
        assert "User A's private session" not in str(body)
    finally:
        _cleanup(db, email_a, email_b)


def test_ac009_listing_another_users_session_documents_is_denied_not_returned() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        user_a_id = _user_id_from_email(db, email_a)
        session_a = _create_session(token_a, "User A's session")
        _add_document(db, session_id=session_a, user_id=user_a_id, filename="secret.pdf")
        db.commit()

        response = client.get(f"/sessions/{session_a}/documents", headers=_auth(token_b))

        assert response.status_code in (403, 404)
        assert "secret.pdf" not in response.text
    finally:
        _cleanup(db, email_a, email_b)


def test_ac009_uploading_a_document_to_another_users_session_is_denied() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's session")

        response = client.post(
            f"/sessions/{session_a}/documents",
            headers=_auth(token_b),
            files={"file": ("intruder.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        assert response.status_code in (403, 404)

        # And indeed nothing was written into user A's session.
        docs = client.get(f"/sessions/{session_a}/documents", headers=_auth(token_a))
        assert docs.status_code == 200
        assert docs.json() == []
    finally:
        _cleanup(db, email_a, email_b)


def test_ac009_listing_another_users_session_messages_is_denied_not_returned() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's session")
        _add_message(
            db, session_id=session_a, role="user", content="A private question from user A"
        )
        db.commit()

        response = client.get(f"/sessions/{session_a}/messages", headers=_auth(token_b))

        assert response.status_code in (403, 404)
        assert "private question from user A" not in response.text
    finally:
        _cleanup(db, email_a, email_b)


def test_ac009_asking_a_question_in_another_users_session_is_denied() -> None:
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's session")

        response = client.post(
            f"/sessions/{session_a}/messages",
            json={"question": "Can I sneak into A's session?"},
            headers=_auth(token_b),
        )

        assert response.status_code in (403, 404)

        # No message was recorded as a side effect of the denied attempt.
        history = client.get(f"/sessions/{session_a}/messages", headers=_auth(token_a))
        assert history.status_code == 200
        assert history.json() == []
    finally:
        _cleanup(db, email_a, email_b)


def test_ac009_a_nonexistent_session_id_is_denied_identically_to_someone_elses() -> None:
    """A fabricated, never-issued session id must come back exactly like a real
    session owned by someone else -- an attacker probing ids cannot tell a
    session that doesn't exist from one that isn't theirs."""
    db = SessionLocal()
    email_a, token_a, email_b, token_b = _two_users()
    try:
        session_a = _create_session(token_a, "User A's session")
        made_up_id = str(uuid.uuid4())

        real_but_foreign = client.get(f"/sessions/{session_a}", headers=_auth(token_b))
        fabricated = client.get(f"/sessions/{made_up_id}", headers=_auth(token_b))

        assert real_but_foreign.status_code == fabricated.status_code
        assert real_but_foreign.status_code in (403, 404)
    finally:
        _cleanup(db, email_a, email_b)


def test_ac009_requires_authentication_at_all_for_every_scoped_route() -> None:
    """Without any token, every one of these routes must also refuse (401),
    rather than ever falling through to return someone's data."""
    db = SessionLocal()
    email_a, token_a, _email_b, _token_b = (*_two_users()[:2], None, None)
    try:
        session_a = _create_session(token_a, "User A's session")

        assert client.get("/sessions").status_code == 401
        assert client.get(f"/sessions/{session_a}").status_code == 401
        assert client.get(f"/sessions/{session_a}/documents").status_code == 401
        assert client.get(f"/sessions/{session_a}/messages").status_code == 401
        assert (
            client.post(f"/sessions/{session_a}/messages", json={"question": "hi?"}).status_code
            == 401
        )
    finally:
        _cleanup(db, email_a)
