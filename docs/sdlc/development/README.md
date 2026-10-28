# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-V2 · approved · source: plan:v2

Development plan version 2 was approved, organized into 4 sprints of capacity 20 each, progressing from auth/session foundation through upload, background processing, and grounded QA with history.

Plan status: approved, version 2. Sprint 1 goal: stand up authentication, per-user authorization, and ability to create a chat session. Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session. Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector. Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history. No explicit approver or approval date was provided in the input.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012, US-013, US-014, US-015, US-016

- ⚠ No approver name or approval date recorded for plan v2.
- ⚠ No explicit mapping in the input of which sprint each individual story (e.g. US-012-US-016) was executed in; sprint-to-item assignment above is inferred only where sprint goal text clearly matches the epic/story content.

### DEV-EPIC-001 · draft · source: plan:EPIC-001

User Accounts & Authentication epic, planned for Sprint 1, covering signup, login, logout, and per-user workspace isolation.

Items: US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent). Sprint 1 goal explicitly targets 'authentication, per-user authorization, and the ability to create a chat session,' which aligns with this epic plus US-005.

**Related:** US-001, US-002, US-003, US-004

- ⚠ No ticket-level delivery status, commit, or completion date provided for US-001 through US-004 despite the overall run being marked 'completed'.

### DEV-EPIC-002 · draft · source: plan:EPIC-002

Chat Session Management epic, enabling users to create sessions and browse/switch between them.

Items: US-005 Create a new chat session (2 pts, backend-agent); US-006 View and switch between my sessions (5 pts, frontend-agent). Partially aligns with Sprint 1 (session creation) and Sprint 2 (browsing/switching) goals.

**Related:** US-005, US-006

- ⚠ No ticket-level delivery status or commit provided for US-005 or US-006.

### DEV-EPIC-003 · draft · source: plan:EPIC-003

PDF Upload & Processing epic covering validated upload of PDFs into a session and the background pipeline that parses, chunks, and embeds them into pgvector.

US-007 Upload a PDF to a chat session (8 pts, backend-agent), broken into: T1 upload endpoint with type/size/count validation; T2 store accepted PDFs in S3 and persist document metadata; T3 enqueue processing job on Redis queue after successful upload; T4 document list endpoint with per-document status. US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent), broken into: T1 PDF text extraction and page-aware chunking in worker; T2 integrate gemini-embedding-001 calls to embed chunks (integration-agent); T3 persist chunk embeddings into pgvector-backed document_chunks table; T4 status transitions and failure handling for parse/API errors. Maps to Sprint 2 (upload) and Sprint 3 (pipeline) goals.

**Related:** US-007, US-008

- ⚠ No ticket-level delivery status or commit provided for US-007, US-008, or any of their sub-tasks.

### DEV-EPIC-004 · draft · source: plan:EPIC-004

Retrieval-Augmented Question Answering epic: answering questions grounded in a session's documents, with citations.

US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent), broken into: T1 similarity search restricted to session's ready documents; T2 integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent); T3 handle no-ready-documents and no-relevant-content cases without fabricating answers; T4 graceful error handling for Gemini failures and missing API key. US-010 View source citations for each answer (3 pts, frontend-agent). Maps to Sprint 4 goal 'grounded question answering with citations.'

**Related:** US-009, US-010

- ⚠ No ticket-level delivery status or commit provided for US-009, US-010, or US-009's sub-tasks.

### DEV-EPIC-005 · draft · source: plan:EPIC-005

Chat History epic: retaining and displaying full session chat history.

US-011 Retain and view full session chat history (3 pts, backend-agent). Maps to Sprint 4 goal 'full persistent chat history.'

**Related:** US-011

- ⚠ No ticket-level delivery status or commit provided for US-011.

### DEV-INTEGRATION-FRONTEND-DEVOPS-QA · draft · source: plan:US-012,US-013,US-014,US-015,US-016

Closing-out stories wiring the frontend upload flow to real backend behavior, running the background worker in production, and end-to-end QA verification.

US-012 Wire Upload PDF form to the real upload endpoint (3 pts, frontend-agent); US-013 Show real backend errors for rejected uploads (2 pts, frontend-agent); US-014 Refresh Documents list to reflect real processing status (3 pts, frontend-agent); US-015 Run the RQ worker for the 'documents' queue alongside the API in the deployed container (3 pts, devops-agent); US-016 End-to-end verification that uploaded PDFs are processed and surfaced correctly (2 pts, qa-agent) -- status=delivered, commit=3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf.

**Related:** US-012, US-013, US-014, US-015, US-016

- ⚠ No ticket-level delivery status or commit provided for US-012, US-013, US-014, or US-015, even though US-016 (which functionally depends on their completion for E2E verification to pass) is marked delivered -- this is a discrepancy worth confirming.

### DEV-RUN-STATUS · approved · source: dev:US-016

The development run is recorded as 'completed' at the run level, but the only ticket with explicit status/commit evidence in the input is US-016.

Ticket US-016 (End-to-end verification that uploaded PDFs are processed and surfaced correctly): status=delivered, commit=3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf.

**Related:** US-016

- ⚠ Run-level status 'completed' is not individually corroborated for the other 24 plan items (epics, stories, and tasks); only US-016 has a ticket record with status and commit. Recommend confirming whether the remaining items were in fact completed or if ticket records are simply missing from this input.
<!-- sdlc:auto:end narrative -->
