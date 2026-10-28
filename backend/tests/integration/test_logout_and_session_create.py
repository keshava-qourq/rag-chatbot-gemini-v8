"""Integration tests for US-005-2: POST /auth/logout (AC-007) and
POST /sessions (AC-010) against the real database.

AC-007 is proven here directly (not just incidentally, as in
test_auth_login.py's NFR-004 case): logging out must cause every subsequent
request bearing that same token to be rejected with 401.

AC-010 is proven for both the "no name given" and "name given" cases: the
created session is owned by the caller, and starts with zero documents and
zero messages.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.main import app
from app.models import User

client = TestClient(app)

PASSWORD = "StrongPassword1"


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _signup(email: str) -> str:
    response = client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _cleanup(email: str) -> None:
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# AC-007 / NFR-004: logout invalidates the session's token immediately.
# ---------------------------------------------------------------------------


def test_ac007_logout_returns_ok_and_subsequent_request_with_same_token_is_401() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        before = client.get("/sessions", headers=_auth(token))
        assert before.status_code == 200

        logout = client.post("/auth/logout", headers=_auth(token))
        assert logout.status_code == 200
        assert logout.json()["status"] == "ok"

        after = client.get("/sessions", headers=_auth(token))
        assert after.status_code == 401
    finally:
        _cleanup(email)


def test_ac007_logout_without_a_token_is_rejected() -> None:
    response = client.post("/auth/logout")

    assert response.status_code == 401


def test_ac007_logout_is_idempotent_and_token_stays_revoked() -> None:
    """Calling logout twice with the same token must not error, and the token
    must remain rejected either way."""
    email = _unique_email()
    token = _signup(email)
    try:
        first = client.post("/auth/logout", headers=_auth(token))
        assert first.status_code == 200

        second = client.post("/auth/logout", headers=_auth(token))
        assert second.status_code == 401

        after = client.get("/sessions", headers=_auth(token))
        assert after.status_code == 401
    finally:
        _cleanup(email)


def test_ac007_logout_only_revokes_the_callers_own_token_not_other_sessions() -> None:
    """Logging out on one token must not affect a different, still-valid
    token belonging to the same account (e.g. a second device/login)."""
    email = _unique_email()
    _signup(email)
    try:
        login_two = client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert login_two.status_code == 200
        token_two = login_two.json()["access_token"]

        login_three = client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert login_three.status_code == 200
        token_three = login_three.json()["access_token"]

        logout = client.post("/auth/logout", headers=_auth(token_two))
        assert logout.status_code == 200

        revoked_check = client.get("/sessions", headers=_auth(token_two))
        assert revoked_check.status_code == 401

        still_valid_check = client.get("/sessions", headers=_auth(token_three))
        assert still_valid_check.status_code == 200
    finally:
        _cleanup(email)


# ---------------------------------------------------------------------------
# AC-010: creating a session returns a caller-owned session with an empty
# documents list and empty message history.
# ---------------------------------------------------------------------------


def test_ac010_creating_a_session_with_a_name_is_empty_and_owned_by_caller() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        response = client.post(
            "/sessions", json={"name": "My research session"}, headers=_auth(token)
        )

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "My research session"
        assert "id" in body
        assert "created_at" in body

        # Owned by the caller: it shows up in that caller's own listing.
        listing = client.get("/sessions", headers=_auth(token))
        assert listing.status_code == 200
        assert body["id"] in {s["id"] for s in listing.json()}

        # Empty documents list.
        documents = client.get(f"/sessions/{body['id']}/documents", headers=_auth(token))
        assert documents.status_code == 200
        assert documents.json() == []

        # Empty message history.
        messages = client.get(f"/sessions/{body['id']}/messages", headers=_auth(token))
        assert messages.status_code == 200
        assert messages.json() == []
    finally:
        _cleanup(email)


def test_ac010_creating_a_session_without_a_name_is_empty_and_owned_by_caller() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        response = client.post("/sessions", json={}, headers=_auth(token))

        assert response.status_code == 200
        body = response.json()
        assert body["name"] is None
        assert "id" in body

        documents = client.get(f"/sessions/{body['id']}/documents", headers=_auth(token))
        assert documents.status_code == 200
        assert documents.json() == []

        messages = client.get(f"/sessions/{body['id']}/messages", headers=_auth(token))
        assert messages.status_code == 200
        assert messages.json() == []
    finally:
        _cleanup(email)


def test_ac010_two_users_creating_sessions_each_only_own_their_own() -> None:
    email_a = _unique_email()
    email_b = _unique_email()
    token_a = _signup(email_a)
    token_b = _signup(email_b)
    try:
        session_a = client.post("/sessions", json={"name": "A"}, headers=_auth(token_a))
        session_b = client.post("/sessions", json={"name": "B"}, headers=_auth(token_b))
        assert session_a.status_code == 200
        assert session_b.status_code == 200

        listing_a = client.get("/sessions", headers=_auth(token_a))
        listing_b = client.get("/sessions", headers=_auth(token_b))

        ids_a = {s["id"] for s in listing_a.json()}
        ids_b = {s["id"] for s in listing_b.json()}

        assert session_a.json()["id"] in ids_a
        assert session_a.json()["id"] not in ids_b
        assert session_b.json()["id"] in ids_b
        assert session_b.json()["id"] not in ids_a
    finally:
        _cleanup(email_a)
        _cleanup(email_b)


def test_ac010_creating_a_session_requires_authentication() -> None:
    response = client.post("/sessions", json={"name": "No auth"})

    assert response.status_code == 401
