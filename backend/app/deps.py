"""The single place that decodes/validates JWTs and checks revocation.

Every protected route depends on `get_current_user`, never decodes a token
itself. Fails closed: any missing, malformed, expired, invalid-signature or
revoked token is a 401, forcing re-authentication (AC-006, NFR-004).
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RevokedToken, User
from app.security import TokenError, decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=401,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def _verified_payload(credentials: HTTPAuthorizationCredentials | None, db: Session) -> dict:
    if credentials is None or not credentials.credentials:
        raise _UNAUTHORIZED
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError:
        raise _UNAUTHORIZED from None

    jti = payload.get("jti")
    subject = payload.get("sub")
    if not jti or not subject:
        raise _UNAUTHORIZED

    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None:
        raise _UNAUTHORIZED

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = _verified_payload(credentials, db)
    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise _UNAUTHORIZED from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _UNAUTHORIZED

    return user


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """Same validation as get_current_user, but returns the raw claims (for logout)."""
    return _verified_payload(credentials, db)
