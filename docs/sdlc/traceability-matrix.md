# Traceability Matrix

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start legend -->
Built from recorded links, not written by a model: requirement key → plan item (`source_stable_key`) → development ticket (`stable_key`) → the ticket's test steps → the last live deployment that started after the work finished. **AC tests** counts the story's acceptance criteria that have a test case, and those whose test cases all passed in the latest finished E2E run.
<!-- sdlc:auto:end legend -->

<!-- sdlc:auto:start matrix -->
| Requirement | Epic | Title | Plan items | Sprint | Design | Code | Commits | Ticket | Tests | AC tests | Deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| US-001 | EPIC-001 | Sign up with email and password | US-001 | 1 | POST /auth/signup, api_backend, postgres, users | backend/app/routers/auth.py, backend/app/schemas.py, backend/app/security.py, backend/requirements.txt, backend/tests/integration/test_auth_signup.py +1 more | db9dfe5 | delivered | not run | 0/3 tested · 0/3 passing | 7d484e0112f6 |
| US-002 | EPIC-001 | Log in with email and password | US-002 | 1 | POST /auth/login, api_backend, postgres, users | backend/alembic/versions/0002_revoked_tokens.py, backend/app/deps.py, backend/app/models.py, backend/app/routers/auth.py, backend/app/schemas.py +1 more | db9dfe5 | delivered | not run | 0/3 tested · 0/3 passing | 7d484e0112f6 |
| US-003 | EPIC-001 | Log out of the application | US-003 | 1 | POST /auth/logout, api_backend, users | — | db9dfe5 | delivered | not run | 0/1 tested · 0/1 passing | 7d484e0112f6 |
| US-004 | EPIC-001 | Private, isolated workspace per user | US-004 | 1 | api_backend, documents, messages, postgres, sessions, users | backend/app/ownership.py, backend/app/routers/sessions.py, backend/app/schemas.py | db9dfe5 | delivered | not run | 0/2 tested · 0/2 passing | 7d484e0112f6 |
| US-005 | EPIC-002 | Create a new chat session | US-005 | 1 | POST /sessions, api_backend, postgres, sessions | — | db9dfe5 | delivered | not run | 0/1 tested · 0/1 passing | 7d484e0112f6 |
| US-006 | EPIC-002 | View and switch between my sessions | US-006 | 2 | GET /sessions, GET /sessions/{session_id}, api_backend, sessions, web_app | frontend/e2e/session-isolation.spec.ts | 6540249 | delivered | not run | 0/2 tested · 0/2 passing | 7d484e0112f6 |
| US-007 | EPIC-003 | Upload a PDF to a chat session | US-007, US-007-T1, US-007-T2, US-007-T3, US-007-T4 | 2 | GET /sessions/{session_id}/documents, POST /sessions/{session_id}/documents, api_backend, documents, postgres, redis, s3 | backend/app/config.py, backend/app/jobs.py, backend/app/routers/sessions.py, backend/app/schemas.py | 02bd1f2 | delivered | not run | 0/4 tested · 0/4 passing | 7d484e0112f6 |
| US-008 | EPIC-003 | Parse, chunk, and embed uploaded PDFs | US-008, US-008-T1, US-008-T2, US-008-T3, US-008-T4 | 3 | document_chunks, documents, gemini, postgres, redis, worker | backend/app/document_processing.py, backend/app/jobs.py | c67d81d, 0d869fb | delivered | not run | 0/5 tested · 0/5 passing | 7d484e0112f6 |
| US-009 | EPIC-004 | Ask a question scoped to the active session's documents | US-009, US-009-T1, US-009-T2, US-009-T3, US-009-T4 | 4 | POST /sessions/{session_id}/messages, api_backend, document_chunks, documents, gemini, messages, postgres | backend/app/rag.py, backend/app/routers/sessions.py, backend/app/schemas.py, backend/tests/integration/test_messages.py, frontend/e2e/ask-question.spec.ts | 0886b21, 7609542 | delivered | succeeded | 0/5 tested · 0/5 passing | 7d484e0112f6 |
| US-010 | EPIC-004 | View source citations for each answer | US-010 | 4 | POST /sessions/{session_id}/messages, api_backend, citations, messages, web_app | frontend/e2e/citations-and-history.spec.ts, frontend/src/screens/Sessions.tsx, frontend/src/screens/SessionsSessionid.test.tsx, frontend/src/screens/SessionsSessionid.tsx | 415b05b | delivered | not run | 0/2 tested · 0/2 passing | 7d484e0112f6 |
| US-011 | EPIC-005 | Retain and view full session chat history | US-011 | 4 | GET /sessions/{session_id}/messages, api_backend, citations, messages, postgres | — | 0886b21 | delivered | not run | 0/2 tested · 0/2 passing | 7d484e0112f6 |
<!-- sdlc:auto:end matrix -->
