"""Session, document and message routes.

Stubs only. Resolving the session/document, checking it belongs to the JWT
subject (AC-009, NFR-005), upload validation, queuing with RQ, retrieval and
the Gemini calls are the development sprint's work, one ticket at a time.
"""

from fastapi import APIRouter, File, UploadFile

from app.schemas import StubResponse

router = APIRouter(tags=["sessions"])


@router.get("/sessions", response_model=StubResponse)
async def list_sessions() -> StubResponse:
    return StubResponse(endpoint="GET /sessions")


@router.post("/sessions", response_model=StubResponse)
async def create_session() -> StubResponse:
    return StubResponse(endpoint="POST /sessions")


@router.get("/sessions/{session_id}", response_model=StubResponse)
async def get_session(session_id: str) -> StubResponse:
    return StubResponse(endpoint="GET /sessions/{session_id}")


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
