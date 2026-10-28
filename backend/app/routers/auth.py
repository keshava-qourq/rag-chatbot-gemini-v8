"""Auth routes: /auth/signup, /auth/login, /auth/logout.

Signup hashes passwords with passlib[bcrypt] (NFR-001), enforces minimum
password complexity server-side (NFR-002), and rejects duplicate emails
(AC-002). Login/logout remain stubs: out of scope for this ticket.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import AuthResponse, SignupRequest, StubResponse, UserOut
from app.security import (
    PASSWORD_RULES,
    create_access_token,
    hash_password,
    password_errors,
)

router = APIRouter(tags=["auth"])


@router.post("/auth/signup", response_model=AuthResponse)
async def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    errors = password_errors(payload.password)
    if errors:
        raise HTTPException(
            status_code=422,
            detail=f"Password does not meet complexity requirements: {PASSWORD_RULES}",
        )

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="An account with this email already exists."
        ) from None
    db.refresh(user)

    token = create_access_token(str(user.id))
    return AuthResponse(access_token=token, user=UserOut(id=str(user.id), email=user.email))


@router.post("/auth/login", response_model=StubResponse)
async def login() -> StubResponse:
    return StubResponse(endpoint="POST /auth/login")


@router.post("/auth/logout", response_model=StubResponse)
async def logout() -> StubResponse:
    return StubResponse(endpoint="POST /auth/logout")
