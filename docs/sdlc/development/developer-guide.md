# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `c22f5ab` · model `auto`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
Rag_chatbot_gemini_v8 is a generated two-app project for a RAG chatbot (document upload, Gemini-based Q&A, chat history/sessions). The frontend is a Vite + React 19 SPA with all approved screens built and rendering seeded sample data (not yet wired to the API). The backend is a FastAPI 0.115 service scaffolded from an approved architecture but with no endpoints implemented beyond a health check; it uses SQLAlchemy over SQLite by default (swappable to Postgres via DATABASE_URL), and the docker-compose file provisions Postgres and Redis for when the real architecture is built out.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Node.js (for Vite 6 / React 19 frontend tooling)
- Python 3.12
- pip
- Docker and Docker Compose (optional, for Postgres/Redis via docker-compose.yml)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. Copy .env.example to .env and set values for variables the code reads (DATABASE_URL, ALLOWED_ORIGINS, VITE_API_BASE_URL, VITE_API_SECRET_KEY)
2. cd backend && pip install -r requirements.txt
3. uvicorn app.main:app --reload   # starts the API on http://localhost:8000, creating SQLite tables on startup
4. cd frontend && npm install
5. npm run dev   # starts the Vite dev server
6. (optional) docker-compose up   # starts Postgres on 5432 and Redis on 6379 for a closer-to-production setup
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| backend dev | `uvicorn app.main:app --reload` | Run the FastAPI app locally with autoreload; serves /health and the OpenAPI docs |
| frontend dev | `npm run dev` | Start the Vite dev server for the React SPA |
| frontend build | `npm run build` | Bundle the frontend with Vite (does not typecheck) |
| frontend preview | `npm run preview` | Serve the production build locally |
| compose up | `docker-compose up` | Start Postgres 16 and Redis 7 containers defined in docker-compose.yml |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/app` | FastAPI application: main.py (app + /health), database.py (engine/session), models.py (SQLAlchemy Base, currently empty), schemas.py (Pydantic StubResponse), routers/ (one router per architecture component, currently empty), services.py (configured_services helper) |
| `backend/tests` | pytest tests, including test_health.py |
| `frontend/src` | React SPA source: main.tsx entry, lib/ (api client, icons, navigate, ui helpers), index.css, test-setup.ts |
| `frontend/e2e` | Playwright acceptance tests (example.spec.ts) |
| `.quorq` | Quorq platform metadata (handoff.json) |
| `docker-compose.yml` | Defines Postgres (db) and Redis (redis-queue) services for local infrastructure |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- Backend routes are generated as typed stubs (StubResponse) per endpoint in the approved API spec before real behavior is implemented
- One FastAPI router per architecture component that owns endpoints, under backend/app/routers/
- SQLAlchemy models all inherit from the shared Base in database.py; models.py is imported in main.py before create_all so tables register
- Backend defaults to SQLite (sqlite:///./app.db) and switches to another database purely via the DATABASE_URL env var, no code changes needed
- CORS allowed origins are read from ALLOWED_ORIGINS (comma-separated) with localhost:5173 as the dev fallback
- Frontend API access goes through the shared apiFetch helper in src/lib/api.ts, which bakes in API_BASE_URL and an optional bearer token from VITE_API_SECRET_KEY
- Frontend screens currently render seeded sample data and are not yet wired to backend endpoints
- Frontend uses Tailwind CSS (via @tailwindcss/vite) and Prettier/ESLint for formatting and linting
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| backend tests | `pytest` | Run backend unit tests (pytest.ini sets pythonpath to repo root, testpaths=tests) |
| backend lint | `ruff check .` | Lint the backend Python code |
| backend format | `ruff format .` | Auto-format backend Python code |
| frontend tests | `npm test` | Run Vitest component tests under src/ |
| frontend typecheck | `npm run typecheck` | Run tsc --noEmit to catch type errors not caught by the build |
| frontend lint | `npm run lint` | Run ESLint over the whole frontend app |
| frontend e2e install | `npm run test:e2e:install` | Install the Chromium browser needed by Playwright |
| frontend e2e | `npm run test:e2e` | Run Playwright acceptance tests from e2e/; without E2E_BASE_URL it boots the backend (from backend/.venv) and the built frontend itself |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Frontend requests to the backend are blocked by CORS | Set ALLOWED_ORIGINS in the backend environment to include the frontend's origin, or run the frontend on the default dev origins (http://localhost:5173 / http://127.0.0.1:5173) that main.py allows by default |
| `npm run build` succeeds but the app later fails type-related checks | Run `npm run typecheck` (tsc --noEmit) separately, since build does not typecheck |
| Playwright e2e tests fail to start the backend | Ensure a Python virtualenv with the backend's dependencies installed exists at backend/.venv, since playwright.config.ts launches `backend/.venv/bin/python -m uvicorn app.main:app` directly |
| Backend tests or app fail to import `app` | Run pytest from the backend/ directory so pytest.ini's `pythonpath = .` resolves the app package correctly |
| Database changes aren't reflected | There are no migrations; tables are created from models.py via Base.metadata.create_all on startup, so delete app.db (SQLite) or adjust DATABASE_URL to reset state |
<!-- sdlc:auto:end troubleshooting -->
