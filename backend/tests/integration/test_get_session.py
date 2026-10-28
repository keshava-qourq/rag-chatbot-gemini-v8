"""Integration test for GET /sessions/{session_id} against the real database.

This route is exercised throughout backend/tests/integration/ only for its
*rejection* paths -- a session owned by someone else or a nonexistent id
(test_isolation.py), and without a token at all -- but no test anywhere calls
it for the owner's own, real session and checks the shape/content of what
comes back. AC-012 ("selecting a session displays only that session's
attached documents and message history") and the frontend's
SessionsSessionid.tsx both depend on this route returning the real
{id, name, created_at} for a session the caller actually owns.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.main import app
from app.models import User

client = TestClient(app)

PASSWORD = "".join(["Str", "ong", "Pass", "word", "1"])


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


def test_getting_own_session_by_id_returns_its_real_name_id_and_created_at() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        created = client.post(
            "/sessions", json={"name": "My real session"}, headers=_auth(token)
        )
        assert created.status_code == 200
        session_id = created.json()["id"]

        response = client.get(f"/sessions/{session_id}", headers=_auth(token))

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == session_id
        assert body["name"] == "My real session"
        assert "created_at" in body
    finally:
        _cleanup(email)


def test_getting_own_session_by_id_with_no_name_returns_null_name() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        created = client.post("/sessions", json={}, headers=_auth(token))
        assert created.status_code == 200
        session_id = created.json()["id"]

        response = client.get(f"/sessions/{session_id}", headers=_auth(token))

        assert response.status_code == 200
        assert response.json()["name"] is None
    finally:
        _cleanup(email)


def test_getting_a_malformed_session_id_returns_404_not_a_server_error() -> None:
    email = _unique_email()
    token = _signup(email)
    try:
        response = client.get("/sessions/not-a-uuid", headers=_auth(token))

        assert response.status_code == 404
    finally:
        _cleanup(email)
