"""Auth routes: /auth/signup, /auth/login, /auth/logout.

Stubs only. Password hashing (passlib), JWT issuance and verification
(python-jose) and account uniqueness are the development sprint's work --
see app.config for where JWT_SECRET_KEY is already read.
"""

from fastapi import APIRouter

from app.schemas import StubResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/signup", response_model=StubResponse)
async def signup() -> StubResponse:
    return StubResponse(endpoint="POST /auth/signup")


@router.post("/auth/login", response_model=StubResponse)
async def login() -> StubResponse:
    return StubResponse(endpoint="POST /auth/login")


@router.post("/auth/logout", response_model=StubResponse)
async def logout() -> StubResponse:
    return StubResponse(endpoint="POST /auth/logout")
