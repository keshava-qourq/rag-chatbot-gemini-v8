# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `ccd2edd` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a two-part generated application: a FastAPI backend that lets authenticated users create chat sessions, upload PDF documents, and ask questions answered by Gemini (gemini-2.5-flash) grounded in embeddings (gemini-embedding-001) stored via pgvector, and a Vite + React 19 SPA frontend with screens for signup/login, session listing, and a per-session chat view. The backend persists users, sessions, documents, chunks, messages and citations through SQLAlchemy models (cross-dialect UUID/Vector types so the same models work on SQLite or Postgres), uses Alembic for schema migrations, JWT auth with a server-side revocation list for logout, S3-style document storage, and an RQ/Redis job queue for background document processing. The frontend currently ships as an approved, generated UI wired against seeded sample data via `src/lib/api.ts`, pointing at the backend's REST endpoints.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Python 3.12 (matches backend/Dockerfile base image)
- Node.js and npm (for the Vite/React 19 frontend)
- pip
- Docker and Docker Compose (for the optional Postgres + Redis services in docker-compose.yml)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. cp .env.example .env and fill in required values (see ENVIRONMENT.md / backend/app/config.py for what's read)
2. cd backend && pip install -r requirements.txt
3. (optional, for Postgres/Redis instead of the SQLite/no-queue defaults) from the repo root: docker compose up -d
4. (optional, when using a real database) cd backend && alembic upgrade head -- otherwise app.main's create_all builds the schema automatically on first run against the default SQLite app.db
5. cd backend && uvicorn app.main:app --reload
6. In a separate shell: cd frontend && npm install
7. cd frontend && npm run dev
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev | `cd backend && uvicorn app.main:app --reload` | Runs the FastAPI app with auto-reload; serves /health, /auth/*, and /sessions/* routes. |
| backend infra | `docker compose up -d` | Starts Postgres 16 (db) and Redis 7 (redis-queue) containers defined in docker-compose.yml. |
| frontend dev | `cd frontend && npm run dev` | Starts the Vite dev server for the React SPA. |
| frontend build | `cd frontend && npm run build` | Bundles the frontend for deployment (vite build); does not typecheck. |
| frontend preview | `cd frontend && npm run preview` | Serves the production build locally for manual checking or e2e tests. |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/` | FastAPI service: app code, Alembic migrations, tests, and scripts. |
| `backend/app/` | Application package: config, database, models, schemas, routers, security, RAG logic, storage, jobs. |
| `backend/app/routers/` | FastAPI routers (auth.py, sessions.py) implementing the API spec's endpoints. |
| `backend/alembic/` | Alembic migration environment and versioned schema migrations (including enabling the pgvector extension). |
| `backend/tests/` | Pytest unit and integration tests (backend/tests/integration/ for auth, sessions, messages, isolation). |
| `backend/scripts/` | Operational scripts, e.g. check_connections.py. |
| `frontend/` | Vite + React 19 SPA: approved screens, component library, and e2e tests. |
| `frontend/src/` | App source: screens, lib (api client, auth, UI/icon vocabulary, brand tokens), entrypoints. |
| `frontend/src/screens/` | One module per approved screen (Signup, Login, Sessions, SessionsSessionid) with colocated tests. |
| `frontend/e2e/` | Playwright acceptance test specs run against a locally served app or a deployed URL. |
| `.github/workflows/` | CI/CD: deploy.yml builds/pushes the backend image and deploys the frontend via AWS Amplify. |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- One FastAPI router per architecture component that owns endpoints (auth.py, sessions.py), registered in app/main.py.
- Pydantic request/response schemas are paired per entity in app/schemas.py, with UUID fields stringified via field_validator.
- SQLAlchemy models use dialect-agnostic sqlalchemy.Uuid and pgvector.sqlalchemy.Vector so the same models run against SQLite (dev/e2e default) or Postgres (production).
- Ownership checks for session-scoped resources go through the shared app/ownership.get_owned_or_404 helper.
- JWT auth: access tokens created in app/security.py; logout inserts the token's jti into RevokedToken, checked by app/deps.get_current_user.
- Backend tests are split into tests/ (unit, e.g. test_models.py, test_security.py) and tests/integration/ (endpoint-level flows).
- Frontend component tests live beside the component/screen they cover (e.g. Login.tsx + Login.test.tsx); Playwright e2e specs live separately in frontend/e2e/.
- Frontend API access is centralized in src/lib/api.ts (apiFetch), which attaches the bearer token and clears it on a 401 with an existing token.
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `cd backend && pytest` | Runs unit and integration tests (pytest.ini sets pythonpath=. and testpaths=tests). |
| backend lint | `cd backend && ruff check .` | Lints the backend Python code per backend/ruff.toml. |
| backend format | `cd backend && ruff format .` | Formats the backend Python code. |
| frontend unit tests | `cd frontend && npm test` | Runs Vitest component tests under src/ (passes with no tests found). |
| frontend typecheck | `cd frontend && npm run typecheck` | Runs tsc --noEmit; not enforced by npm run build. |
| frontend lint | `cd frontend && npm run lint` | Runs ESLint over the frontend app; used as a development gate. |
| frontend e2e | `cd frontend && npm run test:e2e:install && npm run test:e2e` | Installs the Chromium browser then runs Playwright specs from frontend/e2e/, auto-booting the backend (via backend/.venv) and the built frontend unless E2E_BASE_URL is set. |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Document upload route fails with a multipart parsing error | Ensure python-multipart is installed (it's in backend/requirements.txt); FastAPI only errors at request time if it's missing. |
| Frontend requests are blocked by CORS | Set the backend's allowed origins (ALLOWED_ORIGINS, read in app/config.py) to include the frontend's dev/deployed origin; the Vite dev server origin is the local default. |
| No database server available locally | Leave DATABASE_URL unset; app/database.py falls back to a local SQLite file (app.db) and app/main.py's create_all builds the schema automatically. |
| Asking a question returns a 503 'Gemini API is not configured' error | Provide the Gemini API credentials/config the backend expects (see app/rag.py and app/services.py / .env.example) before calling the message endpoints. |
| bcrypt-related errors during signup/login password hashing | Ensure bcrypt==4.0.1 is installed exactly as pinned in backend/requirements.txt; newer bcrypt releases break passlib's backend detection. |
| Playwright e2e suite can't start the backend | Create backend/.venv and install backend/requirements.txt into it first, since playwright.config.ts launches uvicorn from backend/.venv/bin/python. |
<!-- sdlc:auto:end troubleshooting -->
