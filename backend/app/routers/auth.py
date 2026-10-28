"""Auth routes: /auth/signup, /auth/login, /auth/logout.

Signup hashes passwords with passlib[bcrypt] (NFR-001), enforces minimum
password complexity server-side (NFR-002), and rejects duplicate emails
(AC-002). Login issues a JWT on correct credentials and returns a generic
invalid-credentials message otherwise, never revealing whether the email
exists (AC-004/AC-005, NFR-003). Logout revokes the current token's jti so it
is rejected by get_current_user immediately afterward (AC-007, NFR-004).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_token_payload
from app.models import RevokedToken, User
from app.schemas import AuthResponse, LoginRequest, LogoutResponse, SignupRequest, UserOut
from app.security import (
    PASSWORD_RULES,
    create_access_token,
    hash_password,
    password_errors,
    verify_password,
)

router = APIRouter(tags=["auth"])

_INVALID_CREDENTIALS = HTTPException(
    status_code=401, detail="Invalid email or password."
)


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


@router.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise _INVALID_CREDENTIALS

    token = create_access_token(str(user.id))
    return AuthResponse(access_token=token, user=UserOut(id=str(user.id), email=user.email))


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    payload: dict = Depends(get_current_token_payload),
    db: Session = Depends(get_db),
) -> LogoutResponse:
    jti = payload["jti"]
    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is None:
        db.add(RevokedToken(jti=jti))
        db.commit()
    return LogoutResponse()
