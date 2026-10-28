"""Pydantic request and response models.

One pair per entity in the approved data model, plus the placeholder every
generated route returns until it has been implemented.
"""

from datetime import datetime

from pydantic import BaseModel, field_validator

_EMAIL_RE = __import__("re").compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class StubResponse(BaseModel):
    """What a generated route returns until someone implements it.

    A stub that returns a typed body rather than raising keeps the service
    startable and its OpenAPI document complete, so the frontend can be built
    against the agreed shape while the handlers are still being written.
    """

    endpoint: str
    status: str = "not_implemented"
    detail: str = "Scaffolded from the approved API spec; no behaviour yet."


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
