"""Pydantic request and response models.

One pair per entity in the approved data model. Every route the API spec
declares is fully implemented (see app.routers), so there is no generated
placeholder schema left here -- each response model below backs a real route.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _as_str(value: object) -> str:
    """Stringify a UUID id field before validation; pass other values through."""
    return str(value) if isinstance(value, uuid.UUID) else value


class SignupRequest(BaseModel):
    """POST /auth/signup request body: `{ email, password }`."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _valid_email(cls, value: str) -> str:
        value = value.strip()
        if not _EMAIL_RE.match(value):
            raise ValueError("Enter a valid email address.")
        return value.lower()


class LoginRequest(BaseModel):
    """POST /auth/login request body: `{ email, password }`."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserOut(BaseModel):
    """The `user` object nested in auth responses: `{ id, email }`."""

    id: str
    email: str


class AuthResponse(BaseModel):
    """What POST /auth/signup and POST /auth/login return: `{ access_token, user }`."""

    access_token: str
    user: UserOut


class LogoutResponse(BaseModel):
    """What POST /auth/logout returns: `{ status: 'ok' }`."""

    status: str = "ok"


class SessionCreateRequest(BaseModel):
    """POST /sessions request body: `{ name? }`."""

    name: str | None = None


class SessionOut(BaseModel):
    """What GET/POST /sessions and GET /sessions/{id} return: `{ id, name, created_at }`."""

    id: str
    name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        return _as_str(value)


class DocumentOut(BaseModel):
    """What GET/POST /sessions/{id}/documents return, one per document."""

    id: str
    filename: str
    status: str
    size_bytes: int
    page_count: int | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        return _as_str(value)


class MessageCreateRequest(BaseModel):
    """POST /sessions/{session_id}/messages request body: `{ question }`."""

    question: str

    @field_validator("question")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be empty.")
        return value


class CitationOut(BaseModel):
    """One citation attached to an assistant message."""

    id: str
    document_id: str
    filename: str
    page_number: int | None = None
    snippet: str | None = None

    model_config = {"from_attributes": True}

    @field_validator("id", "document_id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        return _as_str(value)


class MessageOut(BaseModel):
    """What GET/POST /sessions/{id}/messages return, one per message."""

    id: str
    session_id: str
    role: str
    content: str
    citations: list[CitationOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", "session_id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        return _as_str(value)
