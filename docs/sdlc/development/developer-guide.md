# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `5346857` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a two-part generated project: a FastAPI 0.115 backend implementing auth, chat sessions, PDF document upload and RAG-based Q&A (using Gemini for embeddings and answers, with Postgres/pgvector as the target store and a SQLite fallback for local dev), and a Vite + React 19 single-page frontend whose approved screens currently render seeded sample data rather than calling the real API. The backend persists users, sessions, documents, document chunks (with vector embeddings), messages and citations via SQLAlchemy models, migrated with Alembic, and queues document processing (rq) backed by Redis. The frontend is a separate npm project with its own build, lint, test and e2e tooling.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Python 3.12
- Node.js (for Vite 6 / React 19 / Vitest 2 toolchain)
- pip
- npm
- Docker and docker-compose (optional, for local Postgres + Redis)
- PostgreSQL 16 with the pgvector extension (for real vector search; SQLite is used otherwise)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. Clone the repository
2. cd backend && pip install -r requirements.txt
3. Copy .env.example to .env and fill in values the deployment uses (e.g. DATABASE_URL, Gemini/AWS credentials) -- backend/app/database.py defaults DATABASE_URL to a local sqlite:///./app.db if unset
4. (Optional) docker-compose up -d to start local Postgres (db) and Redis (redis-queue) containers
5. cd backend && alembic upgrade head (applies migrations, including enabling the pgvector extension, when running against Postgres)
6. cd backend && uvicorn app.main:app --reload (also runs Base.metadata.create_all as a safety net on top of migrations)
7. cd frontend && npm install
8. cd frontend && npm run dev
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev server | `cd backend && uvicorn app.main:app --reload` | Runs the FastAPI app with auto-reload; serves /health and the auth/sessions routers |
| backend migrate | `cd backend && alembic upgrade head` | Applies database migrations (idempotent); also run automatically by the Docker image on container start |
| frontend dev server | `cd frontend && npm run dev` | Starts the Vite dev server for the React SPA |
| frontend build | `cd frontend && npm run build` | Bundles the frontend for deployment (does not typecheck) |
| frontend preview | `cd frontend && npm run preview` | Serves the production build locally |
| local services | `docker-compose up -d` | Starts local Postgres (db) and Redis (redis-queue) containers used by the backend |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/app` | FastAPI application: entrypoint (main.py), config, database/session setup, SQLAlchemy models, Pydantic schemas, security/auth helpers, RAG logic, document processing, job queueing, storage, and routers/ |
| `backend/app/routers` | HTTP route modules: auth.py (signup/login/logout) and sessions.py (sessions, documents, messages) |
| `backend/alembic` | Alembic migration environment and versioned schema migrations (including enabling the pgvector extension) |
| `backend/tests` | Pytest unit and integration tests (health check, models, security, storage, auth signup) |
| `backend/scripts` | Operational scripts, e.g. check_connections.py |
| `frontend/src` | React application source: screens, shared lib (API client, UI/icon vocabulary, brand tokens), app shell and routes |
| `frontend/src/screens` | One module per approved screen (Signup, Login, Sessions, SessionsSessionid) |
| `frontend/src/lib` | Shared frontend utilities: api.ts (API client/base URL), ui.tsx, icons.tsx, brand.ts, navigate.ts |
| `frontend/e2e` | Playwright end-to-end specs run against a locally served app or a deployed URL |
| `.github/workflows` | CI/CD: deploy.yml builds/pushes the backend image and deploys the frontend via AWS Amplify on push/PR to main |
| `.quorq` | Platform metadata (handoff/prepared state) used by the Quorq AI SDLC platform |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- One FastAPI router per architecture component that owns endpoints (auth.py, sessions.py), included in app/main.py
- One SQLAlchemy model per approved data-model entity in app/models.py, kept in step with the Alembic 0001 migration
- UUID primary keys via cross-dialect sqlalchemy.Uuid (not postgresql.UUID) so models work on both Postgres and the SQLite fallback
- Pydantic schemas in app/schemas.py mirror models 1:1, with `from_attributes` config and id fields stringified via field_validator
- Un-implemented routes return a typed StubResponse rather than raising, so OpenAPI stays complete and the app stays startable before handlers are written
- Resource ownership enforced via a shared get_owned_or_404 helper (app/ownership.py) scoped to get_current_user
- JWT auth with server-side logout via a RevokedToken blocklist checked by get_current_user/get_current_token_payload
- Backend runs as a non-root user in Docker, with migrations applied on container boot before uvicorn starts
- Frontend screens are generated per approved design and currently render seeded sample data; app/lib/api.ts is the seam for wiring real API calls
- Frontend build-time env vars (VITE_API_BASE_URL, VITE_API_SECRET_KEY) are inlined by Vite and provided by CI at deploy time
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `cd backend && pytest` | Runs pytest unit/integration tests (health, models, security, storage, auth signup) using pythonpath=. from pytest.ini |
| backend lint | `cd backend && ruff check .` | Lints the backend Python code |
| backend format check | `cd backend && ruff format .` | Formats backend Python code per ruff.toml |
| frontend unit tests | `cd frontend && npm test` | Runs Vitest component tests under src/ with jsdom |
| frontend lint | `cd frontend && npm run lint` | Runs ESLint across the frontend app |
| frontend typecheck | `cd frontend && npm run typecheck` | Runs tsc --noEmit (not run by npm run build) |
| frontend e2e | `cd frontend && npm run test:e2e` | Runs Playwright specs from e2e/; without E2E_BASE_URL it boots the backend (from backend/.venv) and the built frontend locally |
| frontend e2e browser install | `cd frontend && npm run test:e2e:install` | Installs the Chromium browser Playwright needs before running e2e tests |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Backend fails to parse PDF upload (multipart) requests | Ensure python-multipart is installed (it's in backend/requirements.txt); FastAPI only errors about this at request time. |
| Frontend calls to the backend are blocked by CORS | Confirm the frontend's origin is included in the backend's ALLOWED_ORIGINS configuration (app/config.py), which CORSMiddleware in app/main.py reads from the environment. |
| Document upload/RAG answers fail with a 503/502 error about Gemini | The /sessions/{id}/messages route returns 503 when Gemini isn't configured and 502 when a Gemini API call fails; check the Gemini-related environment configuration consumed by app/rag.py and app/services.py. |
| Vector search behaves oddly or is missing in a fresh Postgres database | Run `alembic upgrade head` in backend/ -- migration 0001 enables the pgvector extension; without it DocumentChunk.embedding storage falls back to limited SQLite-compatible behavior only. |
| pip install fails on the bcrypt/passlib combination | The pin bcrypt==4.0.1 in backend/requirements.txt is required for passlib[bcrypt]'s backend detection; don't upgrade bcrypt independently. |
| Playwright e2e tests can't start the backend | Playwright expects a backend/.venv with dependencies installed (see playwright.config.ts); create and populate that virtualenv, or set E2E_BASE_URL to point at an already-running deployment instead. |
<!-- sdlc:auto:end troubleshooting -->
