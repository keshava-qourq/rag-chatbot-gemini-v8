"""Session, document and message routes.

Sessions (GET/POST /sessions, GET /sessions/{id}) and documents
(GET/POST /sessions/{id}/documents) are fully implemented here, scoped to the
authenticated user via get_current_user and the shared get_owned_or_404
helper (AC-008, AC-009, AC-010, NFR-005). Message routes remain stubs; that
is a later sprint's work.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import MAX_DOCUMENTS_PER_SESSION, MAX_PDF_SIZE_BYTES
from app.database import get_db
from app.deps import get_current_user
from app.jobs import enqueue_document_processing
from app.models import ChatSession, Document, User
from app.ownership import get_owned_or_404
from app.schemas import DocumentOut, SessionCreateRequest, SessionOut, StubResponse
from app.storage import make_key, save

router = APIRouter(tags=["sessions"])


def _parse_session_id(session_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found.") from None


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
    sid = _parse_session_id(session_id)
    return get_owned_or_404(db, ChatSession, sid, current_user.id)


@router.get("/sessions/{session_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Document]:
    sid = _parse_session_id(session_id)
    get_owned_or_404(db, ChatSession, sid, current_user.id)
    return (
        db.query(Document)
        .filter(Document.session_id == sid)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.post("/sessions/{session_id}/documents", response_model=DocumentOut)
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    sid = _parse_session_id(session_id)
    get_owned_or_404(db, ChatSession, sid, current_user.id)

    filename = file.filename or ""
    content_type_is_pdf = file.content_type == "application/pdf"
    extension_is_pdf = filename.lower().endswith(".pdf")
    if not (content_type_is_pdf and extension_is_pdf):
        raise HTTPException(
            status_code=422,
            detail="Only PDF files are supported.",
        )

    data = await file.read()
    if len(data) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail="PDF files must be no larger than approximately 20MB.",
        )

    existing_count = db.query(Document).filter(Document.session_id == sid).count()
    if existing_count >= MAX_DOCUMENTS_PER_SESSION:
        raise HTTPException(
            status_code=422,
            detail=(
                f"This session already holds the maximum of {MAX_DOCUMENTS_PER_SESSION} documents."
            ),
        )

    key = make_key(str(sid), filename)
    save(key, data, content_type="application/pdf")

    document = Document(
        session_id=sid,
        user_id=current_user.id,
        filename=filename,
        s3_key=key,
        size_bytes=len(data),
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    enqueue_document_processing(document.id)

    return document


@router.get("/sessions/{session_id}/messages", response_model=StubResponse)
async def list_messages(session_id: str) -> StubResponse:
    return StubResponse(endpoint="GET /sessions/{session_id}/messages")


@router.post("/sessions/{session_id}/messages", response_model=StubResponse)
async def create_message(session_id: str) -> StubResponse:
    return StubResponse(endpoint="POST /sessions/{session_id}/messages")
