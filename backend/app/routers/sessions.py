"""Session, document and message routes.

Sessions (GET/POST /sessions, GET /sessions/{id}) and documents
(GET/POST /sessions/{id}/documents) are scoped to the authenticated user via
get_current_user and the shared get_owned_or_404 helper (AC-008, AC-009,
AC-010, NFR-005). Message routes retrieve chunks via app.rag and call
gemini-2.5-flash to answer, persisting the Q/A pair and per-chunk citations
(AC-022, AC-024, AC-025, AC-026).
"""

import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import MAX_DOCUMENTS_PER_SESSION, MAX_PDF_SIZE_BYTES
from app.database import get_db
from app.deps import get_current_user
from app.jobs import enqueue_document_processing
from app.models import ChatSession, Citation, Document, Message, User
from app.ownership import get_owned_or_404
from app.rag import (
    NOT_FOUND_ANSWER,
    GenerationCallError,
    GenerationConfigError,
    NoReadyDocumentsError,
    generate_answer,
    retrieve_chunks,
)
from app.schemas import (
    CitationOut,
    DocumentOut,
    MessageCreateRequest,
    MessageOut,
    SessionCreateRequest,
    SessionOut,
)
from app.storage import make_key, save

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])


def _parse_session_id(session_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found.") from None


def _to_message_out(message: Message) -> MessageOut:
    citations = [
        CitationOut(
            id=citation.id,
            document_id=citation.document_id,
            filename=citation.document.filename,
            page_number=citation.page_number,
            snippet=citation.snippet,
        )
        for citation in message.citations
    ]
    return MessageOut(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        citations=citations,
        created_at=message.created_at,
    )


def _gemini_unavailable(session_id: uuid.UUID, step: str) -> HTTPException:
    logger.error("Session %s: Gemini is not configured for %s.", session_id, step)
    return HTTPException(
        status_code=503,
        detail="The answer could not be generated because the Gemini API is not configured.",
    )


def _gemini_call_failed(session_id: uuid.UUID, step: str, exc: Exception) -> HTTPException:
    logger.error("Session %s: Gemini %s call failed: %s", session_id, step, exc)
    return HTTPException(
        status_code=502,
        detail="The answer could not be generated because the Gemini API call failed. "
        "Please try again later.",
    )


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


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
async def list_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageOut]:
    sid = _parse_session_id(session_id)
    get_owned_or_404(db, ChatSession, sid, current_user.id)
    messages = (
        db.query(Message).filter(Message.session_id == sid).order_by(Message.created_at.asc()).all()
    )
    return [_to_message_out(message) for message in messages]


@router.post("/sessions/{session_id}/messages", response_model=MessageOut)
async def create_message(
    session_id: str,
    payload: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageOut:
    sid = _parse_session_id(session_id)
    get_owned_or_404(db, ChatSession, sid, current_user.id)

    question = payload.question

    try:
        chunks = retrieve_chunks(db, sid, question)
    except NoReadyDocumentsError:
        raise HTTPException(
            status_code=422,
            detail="This session has no ready documents available to answer from yet.",
        ) from None
    except GenerationConfigError:
        raise _gemini_unavailable(sid, "retrieval") from None
    except GenerationCallError as exc:
        raise _gemini_call_failed(sid, "retrieval", exc) from None

    try:
        answer = generate_answer(question, chunks)
    except GenerationConfigError:
        raise _gemini_unavailable(sid, "generation") from None
    except GenerationCallError as exc:
        raise _gemini_call_failed(sid, "generation", exc) from None

    user_message = Message(session_id=sid, role="user", content=question)
    db.add(user_message)

    assistant_message = Message(session_id=sid, role="assistant", content=answer)
    db.add(assistant_message)
    db.flush()

    # Only attach citations when an answer was actually grounded in the
    # retrieved chunks -- not when the model reported it could not find one
    # (AC-025): a "not found" answer should carry no sources.
    if answer.strip() != NOT_FOUND_ANSWER:
        for rc in chunks:
            db.add(
                Citation(
                    message_id=assistant_message.id,
                    document_id=rc.document.id,
                    chunk_id=rc.chunk.id,
                    page_number=rc.chunk.page_number,
                    snippet=rc.chunk.content[:280],
                )
            )

    db.commit()
    db.refresh(assistant_message)

    return _to_message_out(assistant_message)
