"""Integration tests for POST /auth/signup against the real database."""

import uuid

from fastapi.testclient import TestClient

import app.main  # noqa: F401 -- creates the schema before this runs
from app.database import SessionLocal
from app.main import app
from app.models import User
from app.security import verify_password

client = TestClient(app)


def _unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


def test_ac001_valid_signup_creates_account_and_signs_in() -> None:
    email = _unique_email()
    password = "StrongPass1"

    response = client.post("/auth/signup", json={"email": email, "password": password})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email"] == email
    assert "id" in body["user"]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one()
        assert user.password_hash != password
        assert verify_password(password, user.password_hash)
    finally:
        db.delete(user)
        db.commit()
        db.close()


def test_ac002_duplicate_email_is_rejected_with_no_duplicate_row() -> None:
    email = _unique_email()
    password = "StrongPass1"

    first = client.post("/auth/signup", json={"email": email, "password": password})
    assert first.status_code == 200

    second = client.post("/auth/signup", json={"email": email, "password": password})

    assert second.status_code == 409
    assert "already exists" in second.json()["detail"].lower()

    db = SessionLocal()
    try:
        count = db.query(User).filter(User.email == email).count()
        assert count == 1
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


def test_ac003_weak_password_is_rejected_with_explanation() -> None:
    email = _unique_email()

    response = client.post("/auth/signup", json={"email": email, "password": "weak"})

    assert response.status_code == 422
    detail = response.json()["detail"].lower()
    assert "password" in detail

    db = SessionLocal()
    try:
        assert db.query(User).filter(User.email == email).count() == 0
    finally:
        db.close()
