"""Password hashing, complexity rules and JWT issuance/verification.

NFR-001: passwords are stored only as bcrypt hashes (passlib[bcrypt]).
NFR-002: minimum password complexity is enforced server-side, independent of
whatever the frontend also checks.

Tokens carry a `jti` (JWT ID) so logout (US-002/US-003) can revoke a single
issued token server-side without needing a distributed session store --
see app.models.RevokedToken and app.deps.get_current_user.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_MIN_LENGTH = 8

# Shown to the client verbatim when a password is rejected, so AC-003's
# "explanation of the rules" is one source of truth, not duplicated prose.
PASSWORD_RULES = (
    f"Password must be at least {PASSWORD_MIN_LENGTH} characters long and include "
    "at least one uppercase letter, one lowercase letter, and one digit."
)


class TokenError(Exception):
    """Raised by decode_access_token for any invalid, expired or malformed token."""


def password_errors(password: str) -> list[str]:
    """Every complexity rule ``password`` fails; empty when it passes all of them."""
    errors: list[str] = []
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"at least {PASSWORD_MIN_LENGTH} characters")
    if not re.search(r"[A-Z]", password):
        errors.append("an uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("a lowercase letter")
    if not re.search(r"\d", password):
        errors.append("a digit")
    return errors


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    """A signed JWT for ``subject`` (the user id), expiring per JWT_EXPIRE_MINUTES.

    Each token gets a unique ``jti`` so it can be individually revoked on logout.
    """
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify ``token``'s signature and expiry.

    Raises TokenError on any invalid, malformed or expired token. Does not
    check revocation -- that requires a database lookup, done by app.deps.
    """
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise TokenError(str(exc)) from exc
