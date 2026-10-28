"""Unit tests for password hashing, complexity rules and JWT issuance."""

from jose import jwt

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.security import (
    create_access_token,
    hash_password,
    password_errors,
    verify_password,
)


def test_nfr001_password_hash_is_not_plaintext_and_verifies() -> None:
    password = "StrongPass1"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_nfr002_password_errors_flags_each_missing_rule() -> None:
    assert password_errors("StrongPass1") == []
    assert password_errors("short1A") != []
    assert password_errors("alllowercase1") != []
    assert password_errors("ALLUPPERCASE1") != []
    assert password_errors("NoDigitsHere") != []


def test_create_access_token_is_signed_and_decodable() -> None:
    token = create_access_token("user-id-123")

    decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["sub"] == "user-id-123"
    assert "exp" in decoded
