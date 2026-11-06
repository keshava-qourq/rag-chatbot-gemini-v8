# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal: stand up authentication, per-user authorization, and the ability to create a chat session (capacity 20).

Planned items: EPIC-001 User Accounts & Authentication (epic, unassigned); US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent).

**Related:** EPIC-001, US-001, US-002, US-003, US-004

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session (capacity 20).

Planned items: EPIC-002 Chat Session Management (epic, unassigned); US-005 Create a new chat session (2 pts, backend-agent); US-006 View and switch between sessions (5 pts, frontend-agent); US-007 Upload a PDF to a chat session (8 pts, backend-agent) with tasks: US-007-T1 upload endpoint with type/size/count validation, US-007-T2 store PDFs in S3 and persist metadata, US-007-T3 enqueue processing job on Redis, US-007-T4 document list endpoint with status (all backend-agent, unestimated subtasks).

**Related:** EPIC-002, US-005, US-006, US-007

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector (capacity 20).

Planned items: US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent) with tasks: US-008-T1 text extraction and page-aware chunking in worker (backend-agent), US-008-T2 integrate gemini-embedding-001 calls (integration-agent), US-008-T3 persist chunk embeddings into pgvector-backed document_chunks table (backend-agent), US-008-T4 implement status transitions and failure handling for parse/API errors (backend-agent).

**Related:** EPIC-003, US-008

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history (capacity 20).

Planned items: EPIC-004 Retrieval-Augmented Question Answering (epic, unassigned); US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent) with tasks: US-009-T1 similarity search restricted to session's ready documents, US-009-T2 integrate gemini-2.5-flash generation (integration-agent), US-009-T3 handle no-ready-documents/no-relevant-content cases, US-009-T4 graceful error handling for Gemini failures/missing API key (backend-agent); US-010 View source citations for each answer (3 pts, frontend-agent); EPIC-005 Chat History (epic, unassigned); US-011 Retain and view full session chat history (3 pts, backend-agent).

**Related:** EPIC-004, EPIC-005, US-009, US-010, US-011

### DEV-FIXES · approved · source: plan:v2 backlog

Plan v2 added five follow-up items to fix the upload-to-processing path after it was found not to work end-to-end; not mapped to a specific numbered sprint in the plan input.

- US-012 Wire Upload PDF form to the real upload endpoint (3 pts, frontend-agent).
- US-013 Show real backend errors for rejected uploads (2 pts, frontend-agent).
- US-014 Refresh Documents list to reflect real processing status (3 pts, frontend-agent).
- US-015 Run the RQ worker for the 'documents' queue alongside the API in the deployed container (3 pts, devops-agent).
- US-016 End-to-end verification that uploaded PDFs are processed and surfaced correctly (2 pts, qa-agent).

**Related:** EPIC-003, US-012, US-013, US-014, US-015, US-016

### DEV-RUN-US-016 · approved · source: dev:US-016

Development run completed; the end-to-end upload verification ticket was delivered.

Ticket US-016 (End-to-end verification that uploaded PDFs are processed and surfaced correctly) has status 'delivered', commit 3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf. Overall development run status: completed.

**Related:** US-016, EPIC-003
<!-- sdlc:auto:end narrative -->
