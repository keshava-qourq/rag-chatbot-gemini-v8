# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `4810935` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a two-part generated application: a FastAPI backend that lets users sign up, create chat sessions, upload PDF documents, and ask questions answered via Gemini (gemini-2.5-flash) over embeddings (gemini-embedding-001) stored with pgvector, and a React 19 + Vite single-page frontend with screens for signup/login, sessions, and a per-session chat/document view. The backend uses SQLAlchemy models with Alembic migrations against Postgres (falling back to a local SQLite file when no DATABASE_URL is set), JWT-based auth with a server-side revocation table, S3-style document storage, and an RQ/Redis-backed job queue for document processing. The frontend currently ships with its approved screens and an api.ts client wired to call this backend, authenticating via a bearer token stored client-side.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Python 3.12
- Node.js (for Vite 6 / React 19, Node 20+ recommended)
- pip
- Docker and Docker Compose (optional, for local Postgres + Redis)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. Copy .env.example to .env and fill in required values (e.g. database URL, allowed origins, Gemini credentials) as referenced by the backend config.
2. cd backend && pip install -r requirements.txt
3. (Optional, for Postgres) docker-compose up -d to start the db and redis-queue services, then set DATABASE_URL to point at Postgres and run: alembic upgrade head
4. Start the backend: uvicorn app.main:app --reload  (with no DATABASE_URL set it uses a local sqlite:///./app.db and auto-creates tables)
5. cd frontend && npm install
6. Start the frontend: npm run dev
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev | `uvicorn app.main:app --reload` | Runs the FastAPI backend with auto-reload; creates DB tables on boot via Base.metadata.create_all. |
| backend migrate | `alembic upgrade head` | Applies schema migrations (including enabling the pgvector extension) to the configured database; also run automatically on container boot. |
| frontend dev | `npm run dev` | Starts the Vite dev server for the React SPA. |
| frontend build | `npm run build` | Bundles the frontend for deployment (does not typecheck). |
| frontend preview | `npm run preview` | Serves the production build locally. |
| docker compose up | `docker-compose up -d` | Starts local Postgres 16 and Redis 7 containers used by the backend and its job queue. |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/app` | FastAPI application: main entrypoint, config, DB session, models, schemas, routers (auth, sessions), RAG logic, job enqueueing, storage, security, and ownership helpers. |
| `backend/alembic` | Alembic migration environment and versioned schema migrations, including enabling the pgvector extension. |
| `backend/tests` | Pytest unit and integration tests for health, models, security, storage, auth, uploads, isolation, and messages. |
| `backend/scripts` | Operational scripts, e.g. check_connections.py for verifying external connectivity. |
| `frontend/src` | React application source: screens, shared lib (api client, auth, UI/icon vocabulary, brand tokens), and app shell/routing. |
| `frontend/e2e` | Playwright end-to-end specs for signup, upload, Q&A, citations/history, and session isolation. |
| `.github/workflows` | CI/CD: deploy.yml builds/pushes the backend image to ECR and deploys the frontend build to AWS Amplify via OIDC. |
| `.quorq` | Platform metadata (handoff/prepared state) used by the Quorq AI SDLC platform, not part of the app runtime. |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- One FastAPI router per architecture component that owns endpoints (auth.py, sessions.py), included in app/main.py.
- Pydantic schemas use `from_attributes = True` and stringify UUID primary/foreign keys for JSON responses.
- SQLAlchemy models use cross-dialect `Uuid` and `pgvector.sqlalchemy.Vector` types so the same models work on both Postgres and the SQLite dev fallback.
- Per-user data isolation enforced via a shared `get_owned_or_404` ownership helper used across session/document routes.
- Backend JWT auth includes a server-side revocation list (RevokedToken keyed by jti) so logout has a real effect on stateless tokens.
- Frontend component tests live beside the components/screens they cover (e.g. Login.tsx / Login.test.tsx); Playwright e2e specs live separately under frontend/e2e.
- Frontend API calls go through a single `apiFetch` wrapper (src/lib/api.ts) that attaches the bearer token and clears/redirects on 401.
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `cd backend && pytest` | Runs backend unit and integration tests (pytest.ini sets pythonpath and testpaths). |
| backend lint | `cd backend && ruff check .` | Lints the backend Python code. |
| backend format | `cd backend && ruff format .` | Formats backend Python code with ruff. |
| frontend unit tests | `cd frontend && npm test` | Runs Vitest component tests under src/. |
| frontend lint | `cd frontend && npm run lint` | Runs ESLint over the frontend app (used as a CI gate). |
| frontend typecheck | `cd frontend && npm run typecheck` | Runs tsc --noEmit; not enforced by the build itself. |
| frontend e2e install | `cd frontend && npm run test:e2e:install` | Installs the Chromium browser Playwright needs. |
| frontend e2e | `cd frontend && npm run test:e2e` | Runs Playwright e2e specs; without E2E_BASE_URL it boots the backend (from backend/.venv) and builds/serves the frontend locally. |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Backend starts but document upload returns an error about multipart parsing. | Ensure python-multipart is installed (it's in requirements.txt); FastAPI only raises this at request time for UploadFile routes. |
| Frontend requests are blocked by CORS. | Set the backend's allowed origins (ALLOWED_ORIGINS, read in app/config.py) to include the frontend's dev/deployed origin; CORSMiddleware in app/main.py uses this list. |
| Asking a question returns a 503 'Gemini API is not configured' error. | Supply the Gemini API credentials the backend's generation/retrieval code (app/rag.py) expects in your environment before calling the messages endpoints. |
| No Postgres available locally but you want to run the full stack. | The backend defaults to a local SQLite file (sqlite:///./app.db) when DATABASE_URL is unset, so it runs without a database server; for real pgvector search, run `docker-compose up -d` and point DATABASE_URL at the Postgres service, then `alembic upgrade head`. |
| Playwright e2e tests fail to start the backend. | The webServer config expects backend dependencies installed into backend/.venv; create that venv and `pip install -r requirements.txt` there before running `npm run test:e2e`, or set E2E_BASE_URL to point at an already-running deployment. |
<!-- sdlc:auto:end troubleshooting -->
