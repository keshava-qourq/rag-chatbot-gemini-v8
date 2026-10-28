# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-001 · approved · source: plan:v1

Development plan version 1 is approved, organized into 4 sprints of 20-point capacity each, aligned to 5 epics: Accounts & Authentication, Chat Session Management, PDF Upload & Processing, Retrieval-Augmented QA, and Chat History.

Plan status: approved, version 1. Sprint breakdown: Sprint 1 - stand up authentication, per-user authorization, and chat session creation (capacity 20); Sprint 2 - enable browsing/switching sessions and uploading validated PDFs into a session (capacity 20); Sprint 3 - build background pipeline to parse, chunk, and embed uploaded PDFs into pgvector (capacity 20); Sprint 4 - deliver grounded QA with citations and full persistent chat history (capacity 20). Backlog includes 5 epics (EPIC-001..EPIC-005, unassigned role/points as containers) and 11 stories (US-001..US-011) with assigned points and roles, plus implementation tasks under US-007 (T1-T4), US-008 (T1-T4), and US-009 (T1-T4).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal: stand up authentication, per-user authorization, and the ability to create a chat session.

Capacity 20 points. Scope aligns to EPIC-001 (User Accounts & Authentication: US-001 sign up, US-002 log in, US-003 log out, US-004 private isolated workspace per user, role security-agent) and the start of EPIC-002 (US-005 create a new chat session).

**Related:** US-001, US-002, US-003, US-004, US-005

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session.

Capacity 20 points. Scope covers US-006 (view and switch between sessions, frontend-agent) and US-007 (upload a PDF to a chat session, backend-agent) with sub-tasks for upload endpoint validation (US-007-T1), S3 storage and metadata persistence (US-007-T2), Redis queue enqueue on upload (US-007-T3), and document list endpoint with per-document status (US-007-T4).

**Related:** US-006, US-007

- ⚠ No ticket delivery status reported for US-006 or US-007 despite the dev run being marked completed.

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Capacity 20 points. Scope covers US-008 (parse, chunk, embed uploaded PDFs, backend-agent) with sub-tasks: PDF text extraction and page-aware chunking in worker (US-008-T1), gemini-embedding-001 integration to embed chunks (US-008-T2, integration-agent), persisting chunk embeddings into a pgvector-backed document_chunks table (US-008-T3), and status transitions/failure handling for parse or API errors (US-008-T4).

**Related:** US-008

- ⚠ No ticket delivery status reported for US-008 or its sub-tasks despite the dev run being marked completed.

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history.

Capacity 20 points. Scope covers US-009 (ask a question scoped to active session's documents, backend-agent) with sub-tasks for similarity search restricted to ready documents (US-009-T1), gemini-2.5-flash grounded generation (US-009-T2, integration-agent), handling no-ready-documents/no-relevant-content cases without fabricating answers (US-009-T3), and graceful error handling for Gemini failures/missing API key (US-009-T4); plus US-010 (view source citations, frontend-agent) and US-011 (retain and view full session chat history, backend-agent).

**Related:** US-009, US-010, US-011

- ⚠ No ticket delivery status reported for US-009, US-010, or US-011 or any US-009 sub-tasks despite the dev run being marked completed.

### DEV-2026-US-001 · approved · source: dev:TICKET-US-001

Sign up with email and password was delivered.

Ticket US-001 (Sign up with email and password) status=delivered, commit=db9dfe5a569f9c98da06cf00d17326b58ed70f99.

**Related:** US-001

### DEV-2026-US-002 · approved · source: dev:TICKET-US-002

Log in with email and password was delivered.

Ticket US-002 (Log in with email and password) status=delivered, commit=db9dfe5a569f9c98da06cf00d17326b58ed70f99.

**Related:** US-002

### DEV-2026-US-003 · approved · source: dev:TICKET-US-003

Log out of the application was delivered.

Ticket US-003 (Log out of the application) status=delivered, commit=db9dfe5a569f9c98da06cf00d17326b58ed70f99.

**Related:** US-003

### DEV-2026-US-004 · approved · source: dev:TICKET-US-004

Private, isolated workspace per user was delivered.

Ticket US-004 (Private, isolated workspace per user) status=delivered, commit=db9dfe5a569f9c98da06cf00d17326b58ed70f99. Role security-agent per plan.

**Related:** US-004

### DEV-2026-US-005 · approved · source: dev:TICKET-US-005

Create a new chat session was delivered.

Ticket US-005 (Create a new chat session) status=delivered, commit=db9dfe5a569f9c98da06cf00d17326b58ed70f99.

**Related:** US-005

### DEV-GAP-COMPLETION · draft · source: dev:run-status

The development run is reported as 'completed' but ticket-level evidence only covers 5 of the 11 planned stories.

Dev run status field states 'completed', yet only US-001 through US-005 have individual ticket records with delivered status and commit hashes. No ticket records were provided for US-006 (view/switch sessions), US-007 (upload PDF, incl. T1-T4 sub-tasks), US-008 (parse/chunk/embed, incl. T1-T4 sub-tasks), US-009 (RAG QA, incl. T1-T4 sub-tasks), US-010 (citations), or US-011 (chat history). This is a discrepancy between the overall run status and the per-ticket evidence available.

**Related:** US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ Confirm whether US-006 through US-011 and their sub-tasks were actually implemented, or whether the 'completed' run status is premature/inaccurate.
- ⚠ No commit references available for Sprints 2-4 scope.
<!-- sdlc:auto:end narrative -->
