# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `2ed7625` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a generated two-part application: a Vite + React 19 SPA (frontend/) that implements the approved screens for uploading documents and chatting over them, currently running on seeded sample data, and a FastAPI 0.115 backend (backend/) that implements auth (signup/login/logout with JWT and bcrypt) and session CRUD against a SQLAlchemy data model, while document upload and messaging routes are typed stubs awaiting implementation. The architecture targets PostgreSQL 16 with pgvector for embeddings (gemini-embedding-001) and gemini-2.5-flash for answers, with Redis (via rq) for background work and S3 (via boto3) for file storage, but the backend defaults to a local SQLite database so it runs without any infrastructure. Alembic manages schema migrations (run automatically on container boot), and a GitHub Actions workflow deploys the backend image and the built frontend bundle to AWS.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Node.js (for npm/Vite/React 19, see frontend/package.json)
- Python 3.12 (per backend/Dockerfile)
- pip
- Docker and Docker Compose (optional, for local Postgres + Redis via docker-compose.yml)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. Clone the repository
2. cd backend && pip install -r requirements.txt
3. (optional) docker-compose up -d  # starts Postgres on 5432 and Redis on 6379, defined in docker-compose.yml
4. (optional) set DATABASE_URL to point at Postgres instead of the SQLite default (backend/app/database.py falls back to sqlite:///./app.db)
5. cd backend && uvicorn app.main:app --reload  # starts the API on http://localhost:8000
6. cd frontend && npm install
7. cd frontend && npm run dev  # starts the SPA (talks to VITE_API_BASE_URL, default http://localhost:8000)
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev | `uvicorn app.main:app --reload` | Run the FastAPI backend with autoreload from backend/; creates tables via create_all and serves /health, /auth/*, /sessions* |
| frontend dev | `npm run dev` | Run the Vite dev server for the React SPA from frontend/ |
| frontend build | `npm run build` | Bundle the frontend with Vite (does not typecheck) |
| frontend preview | `npm run preview` | Serve the built frontend bundle locally |
| infra up | `docker-compose up -d` | Start local Postgres 16 and Redis 7 containers defined in docker-compose.yml |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/` | FastAPI service: app code, Alembic migrations, tests, scripts, Dockerfile |
| `backend/app/` | Application package: config, database, models, schemas, security, deps, ownership helpers, and routers/ |
| `backend/app/routers/` | One router per API resource: auth.py (signup/login/logout) and sessions.py (sessions, documents, messages) |
| `backend/alembic/` | Schema migrations; 0001 creates the initial schema (and enables the pgvector extension), 0002 adds revoked_tokens |
| `backend/tests/` | Pytest unit and integration tests (health, models, security, storage, auth signup) |
| `backend/scripts/` | Operational scripts, e.g. check_connections.py |
| `frontend/` | Vite + React 19 SPA: approved screens, config, and e2e tests |
| `frontend/src/` | App source: screens/, lib/ (api client, ui/icon vocabulary, brand tokens), App.tsx route table, main.tsx entry |
| `frontend/src/screens/` | One module per approved screen (Signup, Login, Sessions, SessionsSessionid) |
| `frontend/e2e/` | Playwright end-to-end specs, run against a locally built app or a deployed URL via E2E_BASE_URL |
| `.github/workflows/` | CI/CD: deploy.yml builds/pushes the backend image and deploys the frontend to AWS Amplify via OIDC |
| `.quorq/` | Quorq platform metadata (handoff/prepared state), not application code |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- One FastAPI router per architecture component that owns endpoints (auth.py, sessions.py), registered in app/main.py
- Unimplemented routes return a typed StubResponse ({endpoint, status, detail}) rather than failing, keeping OpenAPI complete before handlers exist
- SQLAlchemy models use the cross-dialect sqlalchemy.Uuid (not postgresql.UUID) so the same models work against both SQLite (local/dev) and Postgres
- Ownership-scoped lookups go through app.ownership.get_owned_or_404 rather than ad hoc filtering
- Passwords hashed with passlib[bcrypt] (pinned bcrypt==4.0.1); JWTs issued via python-jose with revocation tracked in a revoked_tokens table keyed by jti
- Pydantic schemas in app/schemas.py mirror the SQLAlchemy models, one request/response pair per entity
- Frontend: one module per approved screen under src/screens/, shared component/icon vocabulary in src/lib/ui.tsx and src/lib/icons.tsx, brand tokens in src/lib/brand.ts and index.css
- Frontend API access is centralized in src/lib/api.ts (apiFetch), reading VITE_API_BASE_URL/VITE_API_SECRET_KEY at build time; screens currently render seeded data rather than calling it
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `pytest` | Run backend unit/integration tests from backend/ (pytest.ini sets pythonpath=.) |
| backend lint | `ruff check .` | Lint the backend with Ruff |
| backend format | `ruff format .` | Format the backend with Ruff |
| frontend unit tests | `npm test` | Run Vitest component tests under src/ |
| frontend lint | `npm run lint` | Run ESLint over the frontend app (gate the platform runs during development) |
| frontend typecheck | `npm run typecheck` | Run tsc --noEmit (not run by npm run build) |
| frontend e2e install | `npm run test:e2e:install` | Install the Chromium browser Playwright needs |
| frontend e2e | `npm run test:e2e` | Run Playwright specs from e2e/; without E2E_BASE_URL it boots the backend (via backend/.venv) and builds/serves the frontend locally |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Frontend requests are blocked by CORS | Ensure the backend's ALLOWED_ORIGINS (app/config.py) includes the frontend's origin; the Vite dev server origin is the local default. |
| pip install fails or bcrypt behaves oddly on signup/login | Use the pinned bcrypt==4.0.1 in backend/requirements.txt; newer bcrypt breaks passlib's backend detection. |
| `pytest` fails with ModuleNotFoundError: app | Run pytest from backend/ (pytest.ini sets pythonpath=.) rather than from the repo root. |
| Document upload route errors about multipart parsing | Ensure python-multipart is installed (it's in backend/requirements.txt); FastAPI only errors at request time if it's missing. |
| Vector/embedding features don't behave like production | The backend defaults to SQLite (DATABASE_URL unset); real pgvector similarity search requires pointing DATABASE_URL at Postgres with the `vector` extension, enabled by the Alembic 0001 migration. |
| Playwright e2e run fails to start the backend | Install backend dependencies into backend/.venv first, since playwright.config.ts invokes `.venv/bin/python -m uvicorn` directly. |
<!-- sdlc:auto:end troubleshooting -->
