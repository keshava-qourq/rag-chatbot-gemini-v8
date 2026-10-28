# API Reference

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start endpoints -->
| Method | Path | Handler | Source | Summary |
|---|---|---|---|---|
| POST | /auth/login | login | `backend/app/routers/auth.py:60` | — |
| POST | /auth/logout | logout | `backend/app/routers/auth.py:70` | — |
| POST | /auth/signup | signup | `backend/app/routers/auth.py:32` | — |
| GET | /health | health | `backend/app/main.py:53` | Liveness probe, and the only route here that is not a stub. |
| GET | /sessions | list_sessions | `backend/app/routers/sessions.py:23` | — |
| POST | /sessions | create_session | `backend/app/routers/sessions.py:36` | — |
| GET | /sessions/{session_id} | get_session | `backend/app/routers/sessions.py:49` | — |
| GET | /sessions/{session_id}/documents | list_documents | `backend/app/routers/sessions.py:62` | — |
| POST | /sessions/{session_id}/documents | upload_document | `backend/app/routers/sessions.py:67` | — |
| GET | /sessions/{session_id}/messages | list_messages | `backend/app/routers/sessions.py:72` | — |
| POST | /sessions/{session_id}/messages | create_message | `backend/app/routers/sessions.py:77` | — |
<!-- sdlc:auto:end endpoints -->

<!-- sdlc:auto:start drift -->
_Code matches the designed API._
<!-- sdlc:auto:end drift -->

<!-- sdlc:auto:start source -->
Generated from commit `2ed7625`
<!-- sdlc:auto:end source -->
