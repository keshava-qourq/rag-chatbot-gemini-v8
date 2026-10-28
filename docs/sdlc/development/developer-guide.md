# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `eba9349` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a RAG (retrieval-augmented generation) chatbot: users sign up, create chat sessions, upload PDF documents, and ask questions answered by Gemini (gemini-2.5-flash) using chunks embedded with gemini-embedding-001. It is a two-app repository: a React 19 + Vite SPA frontend (currently wired to seeded sample data, generated against an approved design) and a FastAPI 0.115 backend with SQLAlchemy models, Alembic migrations, JWT auth with a server-side revocation list, S3-style document storage, and an RQ worker (sharing the same Docker image as the API) for background document processing against a Postgres+pgvector database (falling back to local SQLite when no DATABASE_URL is set).
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Node.js (for the frontend, Vite 6 / React 19 toolchain)
- Python 3.12
- pip
- Docker and Docker Compose (for Postgres + Redis locally, and for building the backend image)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. Clone the repository and copy .env.example to .env, filling in any required values (see ENVIRONMENT.md).
2. cd backend && pip install -r requirements.txt
3. (optional, for Postgres/pgvector + RQ queue instead of the SQLite fallback) docker-compose up -d from the repo root to start the db and redis-queue services
4. cd backend && uvicorn app.main:app --reload  # creates/updates the SQLite schema via Base.metadata.create_all on first run; run 'alembic upgrade head' when using Postgres
5. cd frontend && npm install
6. cd frontend && npm run dev
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev | `cd backend && uvicorn app.main:app --reload` | Runs the FastAPI app locally with autoreload; serves /health and the auth/sessions routes. |
| frontend dev | `cd frontend && npm run dev` | Starts the Vite dev server for the React SPA. |
| frontend build | `cd frontend && npm run build` | Bundles the frontend for deployment (does not typecheck). |
| frontend preview | `cd frontend && npm run preview` | Serves the production build locally. |
| docker compose | `docker-compose up` | Starts local Postgres 16 and Redis 7 containers used by the backend/worker. |
| backend container | `docker build -t rag-chatbot-backend ./backend && docker run -p 8000:8000 rag-chatbot-backend` | Builds and runs the backend image; scripts/start.sh runs alembic upgrade then starts uvicorn and the RQ worker together. |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/app` | FastAPI application code: entrypoint (main.py), config, database session setup, SQLAlchemy models, Pydantic schemas, routers, auth/security, RAG retrieval+generation, document processing, job queue, and storage helpers. |
| `backend/alembic` | Alembic migration environment and versioned schema migrations (including enabling the pgvector extension). |
| `backend/tests` | Pytest unit and integration tests for auth, sessions, documents, messages, isolation, and the worker entrypoint. |
| `backend/scripts` | Helper scripts, including start.sh which runs migrations then launches uvicorn and the RQ worker, and a connection-check script. |
| `frontend/src` | React application source: screens, shared lib (API client, auth, UI/icon components, brand tokens), and app shell/routing. |
| `frontend/e2e` | Playwright end-to-end specs covering signup, auth, document upload, polling, citations, and session isolation. |
| `.github/workflows` | CI/CD: deploy.yml builds/pushes the backend image, builds the frontend, and deploys both via AWS (ECR/Amplify) using OIDC. |
| `.quorq` | Platform metadata (handoff/prepared state) used by the Quorq AI SDLC platform, not application code. |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- One FastAPI router per resource/architecture component (auth.py, sessions.py), registered in main.py.
- Pydantic response models use from_attributes=True and stringify UUID fields via field_validator, since models use SQLAlchemy Uuid primary/foreign keys.
- Routes enforce ownership via a shared get_owned_or_404 helper and get_current_user dependency; unauthenticated/invalid tokens are handled by get_current_token_payload and a revoked-token table (logout).
- Models use cross-dialect sqlalchemy.Uuid (not postgresql.UUID) and pgvector's Vector type so the same schema works against both SQLite (local/dev) and Postgres (production).
- Alembic migrations (backend/alembic/versions) are the source of truth for schema; Base.metadata.create_all in main.py is only a safety net for fresh local/SQLite setups.
- Backend tests are split into tests/ (unit) and tests/integration/ (API/integration), run via pytest with pythonpath=. (pytest.ini).
- Frontend component tests live beside the components/screens they cover (e.g. Login.test.tsx); Playwright e2e specs live in frontend/e2e.
- Frontend API calls go through a single apiFetch wrapper (src/lib/api.ts) that attaches the bearer token and clears/redirects on 401.
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `cd backend && pytest` | Runs unit and integration tests (auth, sessions, documents, messages, isolation, worker). |
| backend lint | `cd backend && ruff check .` | Lints the backend Python code. |
| backend format | `cd backend && ruff format .` | Formats backend Python code. |
| frontend unit tests | `cd frontend && npm test` | Runs Vitest component tests. |
| frontend lint | `cd frontend && npm run lint` | Runs ESLint over the frontend app. |
| frontend e2e | `cd frontend && npm run test:e2e` | Runs Playwright acceptance tests; builds/serves the backend and frontend locally unless E2E_BASE_URL is set. |
| frontend e2e browser install | `cd frontend && npm run test:e2e:install` | Installs the Chromium browser Playwright needs before running e2e tests. |
| frontend typecheck | `cd frontend && npm run typecheck` | Runs tsc --noEmit (not enforced by build or lint gates). |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Document upload fails or FastAPI complains about multipart parsing at request time. | Ensure python-multipart is installed (it's in backend/requirements.txt); re-run pip install -r requirements.txt. |
| Backend works locally with no database server configured. | This is expected: DATABASE_URL defaults to a local sqlite:///./app.db file (app/database.py). Set DATABASE_URL to a Postgres connection string to use the real pgvector-backed schema, and run alembic migrations against it. |
| Asking a question returns a 503 'Gemini API is not configured' or 502 'Gemini API call failed'. | Check that the Gemini-related environment variables required by app/config.py and app/rag.py are set; a 502 indicates the configured Gemini call itself failed (e.g. bad key, network) rather than missing config. |
| Frontend requests are blocked by CORS. | Confirm the frontend origin is included in ALLOWED_ORIGINS consumed by app/config.py; the Vite dev server origin is the local default. |
| Signup/login works locally but passlib/bcrypt errors appear. | Keep bcrypt pinned to 4.0.1 as in requirements.txt; newer bcrypt releases are incompatible with the pinned passlib backend detection used here. |
| Document stays in 'processing' status indefinitely. | Document processing runs via an RQ worker on the 'documents' queue (app/jobs.py); ensure Redis (redis-queue service in docker-compose.yml) is running and that the worker process (started alongside uvicorn by backend/scripts/start.sh in the Docker image) is active. |
<!-- sdlc:auto:end troubleshooting -->
