"""Session, document and message routes.

Sessions (GET/POST /sessions, GET /sessions/{id}) are fully implemented here,
scoped to the authenticated user via get_current_user and the shared
get_owned_or_404 helper (AC-008, AC-009, AC-010, NFR-005). Document and
message routes remain stubs; that is a later sprint's work.
"""

import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import ChatSession, User
from app.ownership import get_owned_or_404
from app.schemas import SessionCreateRequest, SessionOut, StubResponse

router = APIRouter(tags=["sessions"])


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.post("/sessions", response_model=SessionOut)
async def create_session(
    payload: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSession:
    session_obj = ChatSession(user_id=current_user.id, name=payload.name)
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSession:
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found.") from None
    return get_owned_or_404(db, ChatSession, sid, current_user.id)


@router.get("/sessions/{session_id}/documents", response_model=StubResponse)
async def list_documents(session_id: str) -> StubResponse:
    return StubResponse(endpoint="GET /sessions/{session_id}/documents")


@router.post("/sessions/{session_id}/documents", response_model=StubResponse)
async def upload_document(session_id: str, file: UploadFile = File(...)) -> StubResponse:
    return StubResponse(endpoint="POST /sessions/{session_id}/documents")


@router.get("/sessions/{session_id}/messages", response_model=StubResponse)
async def list_messages(session_id: str) -> StubResponse:
    return StubResponse(endpoint="GET /sessions/{session_id}/messages")


@router.post("/sessions/{session_id}/messages", response_model=StubResponse)
async def create_message(session_id: str) -> StubResponse:
    return StubResponse(endpoint="POST /sessions/{session_id}/messages")
