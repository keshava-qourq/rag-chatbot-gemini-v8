# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `24ac353` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a RAG-based chatbot: a FastAPI backend provides auth, session and PDF-document endpoints backed by SQLAlchemy models (users, chat sessions, documents, document chunks with pgvector embeddings, messages, citations) with Gemini embeddings/answers and S3-style storage, while a Vite + React 19 SPA provides the approved screens (Signup, Login, Sessions, Session detail). The backend defaults to a local SQLite database so it runs with no external services, with Alembic migrations and a Postgres+pgvector target for production; the frontend currently renders seeded sample data and is not yet wired to the real API (the `src/lib/api.ts` client exists as the integration seam). Message endpoints are still stubs; auth, session, and document-upload endpoints are fully implemented.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Node.js (for Vite 6 / React 19 frontend tooling)
- Python 3.12
- pip
- Docker and docker-compose (optional, for local Postgres + Redis)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. Clone the repository
2. cd backend && pip install -r requirements.txt
3. (optional) docker-compose up -d to start Postgres and Redis locally; otherwise the backend falls back to a local SQLite file (app.db) with no DATABASE_URL set
4. cd backend && uvicorn app.main:app --reload  (creates the SQLite schema automatically via create_all; run `alembic upgrade head` first if targeting Postgres)
5. cd frontend && npm install
6. cd frontend && npm run dev
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev | `uvicorn app.main:app --reload` | Run the FastAPI backend locally with auto-reload (from backend/) |
| frontend dev | `npm run dev` | Run the Vite dev server for the React SPA (from frontend/) |
| frontend build | `npm run build` | Bundle the frontend for deployment (does not typecheck) |
| frontend preview | `npm run preview` | Serve the built frontend bundle locally |
| local infra | `docker-compose up` | Start Postgres 16 and Redis (job queue) containers defined in docker-compose.yml |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/app` | FastAPI application: entrypoint (main.py), config, database engine/session, models, schemas, security (JWT/bcrypt), deps, jobs (queue), storage, ownership helper, and routers/ |
| `backend/app/routers` | Route modules: auth.py (signup/login/logout) and sessions.py (sessions, documents, message stubs) |
| `backend/alembic` | Alembic migration environment and versioned schema migrations (including enabling the pgvector extension) |
| `backend/tests` | Pytest unit/integration tests for health, models, security, storage, and auth signup |
| `backend/scripts` | Operational scripts, e.g. check_connections.py |
| `frontend/src` | React SPA source: screens/, lib/ (api client, UI components, icons, brand tokens), App.tsx route table, main.tsx entry |
| `frontend/src/screens` | One module per approved screen (Signup, Login, Sessions, SessionsSessionid) |
| `frontend/e2e` | Playwright end-to-end specs run against a locally served backend+frontend or a deployed E2E_BASE_URL |
| `.github/workflows` | CI/CD: deploy.yml builds/pushes the backend Docker image and deploys the frontend to AWS Amplify via OIDC |
| `.quorq` | Platform metadata (handoff/prepared state) used by the Quorq AI SDLC platform, not application code |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- One FastAPI router per architecture component that owns endpoints (auth, sessions); unimplemented routes return a typed StubResponse rather than being absent
- SQLAlchemy models use cross-dialect sqlalchemy.Uuid (not postgresql.UUID) so the same models work against both SQLite (local/e2e) and Postgres
- Pydantic schemas use from_attributes/model_config to serialize ORM objects directly, with UUID fields stringified via field_validator
- Resource ownership enforced via a shared get_owned_or_404 helper (app/ownership.py) scoped to the authenticated user
- Authentication is JWT-based (python-jose) with bcrypt password hashing (passlib, pinned bcrypt==4.0.1); logout revokes tokens by storing their jti in a RevokedToken table
- Alembic migrations (backend/alembic/versions) are the source of truth for schema; Base.metadata.create_all in main.py is only a safety net for fresh/local/SQLite setups
- Frontend screens are generated from an approved design and currently render seeded sample data; frontend/src/lib/api.ts is the designated integration seam for wiring real API calls
- Backend container runs migrations then the server in one process (`alembic upgrade head && uvicorn ...`) rather than as a separate deploy step
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `pytest` | Run backend unit/integration tests (from backend/, pytest.ini sets pythonpath) |
| backend lint | `ruff check .` | Lint the backend Python code |
| backend format check | `ruff format .` | Format/check backend Python code style |
| frontend unit tests | `npm run test` | Run Vitest component tests under src/ |
| frontend lint | `npm run lint` | Run ESLint over the frontend app (CI gate) |
| frontend typecheck | `npm run typecheck` | Run tsc --noEmit (not run by npm run build) |
| frontend e2e | `npm run test:e2e` | Run Playwright acceptance tests from e2e/, booting backend+frontend locally unless E2E_BASE_URL is set |
| install e2e browser | `npm run test:e2e:install` | Fetch the Chromium browser Playwright needs |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Document upload route fails at request time complaining multipart parsing is unavailable | Ensure python-multipart (listed in backend/requirements.txt) is installed via pip install -r requirements.txt; FastAPI only errors on this at runtime, not at import |
| passlib/bcrypt password hashing raises an AttributeError about bcrypt.__about__ or fails its self-test | Keep bcrypt pinned to 4.0.1 as in requirements.txt; newer bcrypt releases break passlib's backend detection |
| Frontend fetch calls to the backend are blocked by the browser (CORS) | Ensure the frontend origin is included in the backend's ALLOWED_ORIGINS (app/config.py), which defaults to the Vite dev server locally |
| Vector/embedding features don't behave like production (pgvector) when running locally | The default DATABASE_URL is sqlite:///./app.db for easy local runs; point DATABASE_URL at a real Postgres instance (e.g. via docker-compose's db service) and run `alembic upgrade head` to get the actual pgvector extension and vector search |
| Playwright e2e tests fail to start the backend | The webServer config expects a backend/.venv with dependencies installed and runs `uvicorn app.main:app` on 127.0.0.1:8000; create that venv and install backend/requirements.txt before running npm run test:e2e |
<!-- sdlc:auto:end troubleshooting -->
