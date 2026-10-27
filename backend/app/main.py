"""Application entrypoint.

Generated from the approved architecture: one router per component that owns
endpoints, one route per endpoint the API spec declares. Every generated route
is a stub that returns a typed placeholder, so the service starts, serves its
OpenAPI document and passes its tests before a single handler is implemented.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 -- imported so the tables register before create_all
from app.config import ALLOWED_ORIGINS
from app.database import Base, engine
from app.routers import auth, sessions
from app.services import configured_services

_DESCRIPTION = (
    "Build a rag chatbot where user can upload there own documents and ask queries "
    "about them use gemini-2.5-flash for answers and gemini-embedding-001 for "
    "embeddings and have chat history and sessions"
)

app = FastAPI(
    title="Rag_chatbot_gemini_v8",
    description=_DESCRIPTION,
    version="0.1.0",
)

# The SPA runs on a different origin than the API, so the browser refuses its calls
# unless that origin is allowed here. ALLOWED_ORIGINS (app.config) is read from the
# environment the platform injects, with the Vite dev server as the local default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sessions.router)

# backend/alembic is the source of truth for schema changes once there is real data
# to keep -- see its 0001 migration, which also enables the `vector` extension.
# create_all is a safety net on top of that, not a replacement for it: it is
# idempotent (skips tables that already exist), so a clone that has never run a
# migration -- a fresh local dev setup, the frontend's e2e suite -- still boots
# with a working schema.
Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health() -> dict[str, object]:
    """Liveness probe, and the only route here that is not a stub."""
    return {"status": "ok", "services": configured_services()}
