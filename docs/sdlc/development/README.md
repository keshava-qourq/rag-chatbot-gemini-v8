# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### PLAN-001 · approved · source: plan

Development plan version 1 was approved, organized into 4 sprints covering authentication, session management, PDF upload/processing, and grounded Q&A with history.

Plan status: approved, version 1. Sprint 1 goal: stand up authentication, per-user authorization, and the ability to create a chat session (capacity 20). Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session (capacity 20). Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector (capacity 20). Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history (capacity 20).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ Input lists sprints and backlog items separately with no explicit field mapping which item belongs to which sprint; mapping used in epic-level entries below is inferred from goal text and epic grouping, not stated directly.

### EPIC-001 · approved · source: plan:EPIC-001

User Accounts & Authentication epic covering signup, login, logout, and per-user workspace isolation.

US-001 Sign up with email and password (3 pts, backend-agent). US-002 Log in with email and password (3 pts, backend-agent). US-003 Log out of the application (2 pts, backend-agent). US-004 Private, isolated workspace per user (5 pts, security-agent). Maps to Sprint 1 goal of standing up authentication and per-user authorization.

**Related:** US-001, US-002, US-003, US-004

- ⚠ No development-run ticket status reported for US-001, US-002, US-003, or US-004 despite the dev run being marked 'completed' -- unclear whether these were implemented.

### EPIC-002 · approved · source: plan:EPIC-002

Chat Session Management epic covering creating sessions and browsing/switching between them.

US-005 Create a new chat session (2 pts, backend-agent). US-006 View and switch between my sessions (5 pts, frontend-agent). Maps to Sprint 1 (session creation) and Sprint 2 (browsing/switching) goals.

**Related:** US-005, US-006

- ⚠ No development-run ticket status reported for US-005 or US-006 despite the dev run being marked 'completed' -- unclear whether these were implemented.

### EPIC-003 · approved · source: plan:EPIC-003

PDF Upload & Processing epic covering upload with validation and the background parse/chunk/embed pipeline into pgvector.

US-007 Upload a PDF to a chat session (8 pts, backend-agent), broken into: T1 upload endpoint with type/size/count validation; T2 store accepted PDFs in S3 and persist document metadata; T3 enqueue processing job on Redis queue after successful upload; T4 document list endpoint with per-document status. US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent), broken into: T1 PDF text extraction and page-aware chunking in worker; T2 integrate gemini-embedding-001 calls to embed chunks (integration-agent); T3 persist chunk embeddings into pgvector-backed document_chunks table; T4 status transitions and failure handling for parse/API errors. Maps to Sprint 2 (upload) and Sprint 3 (parse/chunk/embed pipeline) goals.

**Related:** US-007, US-007-T1, US-007-T2, US-007-T3, US-007-T4, US-008, US-008-T1, US-008-T2, US-008-T3, US-008-T4

- ⚠ No development-run ticket status reported for US-007, US-008, or any of their sub-tasks (T1-T4 each) despite the dev run being marked 'completed' -- unclear whether the upload flow or embedding pipeline were implemented.

### EPIC-004 · approved · source: plan:EPIC-004

Retrieval-Augmented Question Answering epic covering grounded Q&A scoped to a session's documents and source citations.

US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent), broken into: T1 similarity search restricted to session's ready documents; T2 integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent); T3 handle no-ready-documents and no-relevant-content cases without fabricating answers; T4 graceful error handling for Gemini failures and missing API key. US-010 View source citations for each answer (3 pts, frontend-agent). Maps to Sprint 4 goal of grounded Q&A with citations.

**Related:** US-009, US-009-T1, US-009-T2, US-009-T3, US-009-T4, US-010

- ⚠ US-010 (citations) was recorded in the dev run as skipped with no commit -- reason not stated in input.
- ⚠ No individual task-level (T1-T4) status reported for US-009 beyond the overall story being marked delivered.

### EPIC-005 · approved · source: plan:EPIC-005

Chat History epic covering retention and viewing of full session chat history.

US-011 Retain and view full session chat history (3 pts, backend-agent). Maps to Sprint 4 goal of delivering full persistent chat history.

**Related:** US-011

- ⚠ US-011 (persistent chat history) was recorded in the dev run as skipped with no commit -- reason not stated in input. This directly affects the project's stated goal of 'having chat history and sessions'.

### DEV-RUN-2026 · draft · source: dev

The development run for this phase is marked 'completed', but ticket-level status was only reported for 3 of the 11 planned stories.

Development run status: completed. Reported tickets: US-009 (delivered, commit 76095423754242aa36718432d1bc08e7ddbde4fe), US-010 (skipped, no commit), US-011 (skipped, no commit). No ticket entries were provided for US-001 through US-008, which make up the authentication, session management, and PDF upload/processing epics.

**Related:** US-009, US-010, US-011, US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008

- ⚠ Discrepancy: the run is marked 'completed' but 8 of 11 planned stories (US-001-US-008) have no reported ticket status -- unclear if they were built, not attempted, or simply omitted from this input.
- ⚠ No task-level (Txx) ticket statuses were reported for any story.

### DEV-US-009 · approved · source: dev:US-009

Grounded question-answering scoped to a session's documents was delivered.

Ticket US-009 'Ask a question scoped to the active session's documents' status=delivered, commit=76095423754242aa36718432d1bc08e7ddbde4fe.

**Related:** US-009, US-009-T1, US-009-T2, US-009-T3, US-009-T4, EPIC-004

- ⚠ Only story-level delivery is confirmed; individual sub-task (T1-T4) completion was not separately reported.

### DEV-US-010 · draft · source: dev:US-010

The source-citations feature for answers was not delivered in this run.

Ticket US-010 'View source citations for each answer' status=skipped, commit=(none).

**Related:** US-010, EPIC-004, US-009

- ⚠ Reason for skipping not provided in input.
- ⚠ Citation display functionality should not be assumed to exist in the built application.

### DEV-US-011 · draft · source: dev:US-011

Retention and viewing of full session chat history was not delivered in this run.

Ticket US-011 'Retain and view full session chat history' status=skipped, commit=(none).

**Related:** US-011, EPIC-005

- ⚠ Reason for skipping not provided in input.
- ⚠ Persistent chat history should not be assumed to exist in the built application, despite being a core part of the project description.
<!-- sdlc:auto:end narrative -->
