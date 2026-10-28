"""Integration tests for POST /auth/login and session invalidation against the
real database, covering AC-004/AC-005/AC-006 (and NFR-003/NFR-004 where they
can be exercised here).

Follows the TestClient-against-real-Postgres pattern in test_auth_signup.py.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from jose import jwt

import app.main  # noqa: F401 -- creates the schema before this runs
from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.database import SessionLocal
from app.main import app
from app.models import User

client = TestClient(app)

PASSWORD = "Str0ngPass!"


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def _signup(email: str, password: str = PASSWORD) -> None:
    response = client.post("/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 200


def _cleanup(email: str) -> None:
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


def test_ac004_correct_credentials_return_token_that_works_on_a_protected_route() -> None:
    email = _unique_email()
    _signup(email)
    try:
        response = client.post("/auth/login", json={"email": email, "password": PASSWORD})

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["user"]["email"] == email
        assert "id" in body["user"]

        protected = client.get(
            "/sessions", headers={"Authorization": f"Bearer {body['access_token']}"}
        )
        assert protected.status_code == 200
    finally:
        _cleanup(email)


def test_ac005_wrong_password_and_unknown_email_return_identical_generic_401() -> None:
    email = _unique_email()
    _signup(email)
    try:
        wrong_password = client.post("/auth/login", json={"email": email, "password": "WrongPass1"})
        unknown_email = client.post(
            "/auth/login",
            json={"email": _unique_email(), "password": "WrongPass1"},
        )

        assert wrong_password.status_code == 401
        assert unknown_email.status_code == 401
        assert wrong_password.json()["detail"] == unknown_email.json()["detail"]
        detail = wrong_password.json()["detail"].lower()
        assert "invalid" in detail
        assert email not in detail
    finally:
        _cleanup(email)


def test_ac006_expired_token_is_rejected_on_a_protected_route() -> None:
    now = datetime.now(UTC)
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "iat": now - timedelta(minutes=120),
        "exp": now - timedelta(minutes=60),
        "jti": uuid.uuid4().hex,
    }
    expired_token = jwt.encode(expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    response = client.get("/sessions", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401


def test_ac006_malformed_token_is_rejected_on_a_protected_route() -> None:
    response = client.get("/sessions", headers={"Authorization": "Bearer not-a-real-jwt"})

    assert response.status_code == 401


def test_ac006_revoked_token_is_rejected_immediately_on_a_protected_route() -> None:
    """NFR-004: logging out immediately invalidates the session's token."""
    email = _unique_email()
    _signup(email)
    try:
        login = client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        before_logout = client.get("/sessions", headers=headers)
        assert before_logout.status_code == 200

        logout = client.post("/auth/logout", headers=headers)
        assert logout.status_code == 200

        after_logout = client.get("/sessions", headers=headers)
        assert after_logout.status_code == 401
    finally:
        _cleanup(email)


def test_ac006_missing_token_is_rejected_on_a_protected_route() -> None:
    response = client.get("/sessions")

    assert response.status_code == 401
