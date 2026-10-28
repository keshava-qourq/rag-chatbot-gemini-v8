"""Pydantic request and response models.

One pair per entity in the approved data model, plus the placeholder every
generated route returns until it has been implemented.
"""

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


class UserOut(BaseModel):
    """The `user` object nested in auth responses: `{ id, email }`."""

    id: str
    email: str


class AuthResponse(BaseModel):
    """What POST /auth/signup (and /auth/login) returns: `{ access_token, user }`."""

    access_token: str
    user: UserOut
