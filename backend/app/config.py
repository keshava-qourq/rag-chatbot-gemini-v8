"""Centralised reads of the environment variables the deployment platform guarantees.

The platform always injects `ALLOWED_ORIGINS`, `SECRET_KEY`, `JWT_SECRET_KEY` and
`MEDIA_ROOT` into the running container; every one of them has a working local
default here so the app still boots on a bare clone. Read these constants rather
than calling `os.getenv` again elsewhere, so there is exactly one place that
knows what the platform promises.

`SECRET_KEY` is the shared bearer the generated frontend sends on every request.
It is public -- never sign anything with it, only compare it. `JWT_SECRET_KEY`
is private: it is the only thing that signs issued tokens, and it must never be
logged or echoed back to a client.
"""

import os
from pathlib import Path

# The frontend's origin(s), comma separated, for CORS (see app.main). Falls back to
# the Vite dev server so a bare `npm run dev` + `uvicorn` pair works together.
ALLOWED_ORIGINS: list[str] = [
    origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()
] or ["http://localhost:5173", "http://127.0.0.1:5173"]

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-not-for-production")

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-not-for-production")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# A writable directory that survives redeploys; backs document storage (app.storage)
# when S3_BUCKET is unset, which is every local run and the test suite.
MEDIA_ROOT: Path = Path(os.getenv("MEDIA_ROOT", "./media")).resolve()
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Set in every real deployment; unset in local dev, where app.storage falls back to
# MEDIA_ROOT instead of a bucket.
S3_BUCKET: str = os.getenv("S3_BUCKET", "")
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

# The Gemini API is not one of this project's provisioned services (see
# ENVIRONMENT.md), so there is no guarantee this is set yet. Code that calls
# Gemini must treat an empty key as "cannot run" and fail clearly, and tests must
# fake the call rather than reach the real API.
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# Redis-backed job queue (app.jobs) for document processing (US-007/US-008).
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# NFR-006: per-PDF upload size cap, ~20MB, enforced at the upload route.
MAX_PDF_SIZE_BYTES: int = 20 * 1024 * 1024

# NFR-007: maximum number of documents a single session may hold.
MAX_DOCUMENTS_PER_SESSION: int = 20
