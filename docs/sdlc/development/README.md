# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-001 · approved · source: plan:v1

Development plan version 1 is approved, organized into 4 sprints of capacity 20 each, covering 5 epics and all 11 known user stories.

Plan status: approved, version 1. Sprint breakdown: Sprint 1 -- 'Stand up authentication, per-user authorization, and the ability to create a chat session' (capacity 20); Sprint 2 -- 'Enable browsing/switching sessions and uploading validated PDFs into a session' (capacity 20); Sprint 3 -- 'Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector' (capacity 20); Sprint 4 -- 'Deliver grounded question answering with citations and full persistent chat history' (capacity 20).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ No explicit sprint-to-story assignment table was given; sprint-to-story mapping below is inferred from sprint goal text matching story content, not an authoritative field in the input.

### EPIC-001 · approved · source: plan:EPIC-001

User Accounts & Authentication epic: sign up, log in, log out, and per-user isolated workspace. Mapped to Sprint 1's authentication/authorization goal.

Stories: US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent). No sub-tasks were listed for these stories in the input, and no epic-level point total or owning role was provided.

**Related:** US-001, US-002, US-003, US-004

- ⚠ Epic has no assigned role or point total in the input.
- ⚠ No implementation tasks (T1, T2, ...) were broken out for US-001–US-004, unlike later epics -- unclear if this is intentional or missing.
- ⚠ No delivery/ticket status reported for US-001, US-002, US-003, or US-004.

### EPIC-002 · approved · source: plan:EPIC-002

Chat Session Management epic: create and switch between chat sessions. Spans Sprint 1 (session creation) and Sprint 2 (browsing/switching).

Stories: US-005 Create a new chat session (2 pts, backend-agent); US-006 View and switch between my sessions (5 pts, frontend-agent). No sub-tasks were listed for either story, and no epic-level point total or owning role was provided.

**Related:** US-005, US-006

- ⚠ Epic has no assigned role or point total in the input.
- ⚠ No implementation tasks were broken out for US-005/US-006.
- ⚠ No delivery/ticket status reported for US-005 or US-006.

### EPIC-003 · approved · source: plan:EPIC-003

PDF Upload & Processing epic: validated PDF upload into a session (Sprint 2) and the background parse/chunk/embed pipeline into pgvector (Sprint 3).

US-007 Upload a PDF to a chat session (8 pts, backend-agent) breaks into: T1 upload endpoint with type/size/count validation; T2 store accepted PDFs in S3 and persist document metadata; T3 enqueue processing job on Redis queue after successful upload; T4 document list endpoint with per-document status. US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent) breaks into: T1 PDF text extraction and page-aware chunking in worker; T2 integrate gemini-embedding-001 to embed chunks (integration-agent); T3 persist chunk embeddings into pgvector-backed document_chunks table; T4 status transitions and failure handling for parse/API errors. Per the development run report, US-008 is the only story in this epic (and in the whole plan) confirmed delivered, via commit 0d869fb8851066b8d0646d321b110f2c669942d5.

**Related:** US-007, US-008

- ⚠ No delivery/ticket status reported for US-007 or any of its sub-tasks (T1–T4), despite US-008 (which logically depends on uploads existing) being marked delivered -- potential sequencing discrepancy worth flagging to the team.
- ⚠ Epic has no assigned role or point total in the input.

### EPIC-004 · approved · source: plan:EPIC-004

Retrieval-Augmented Question Answering epic: scoped similarity search, Gemini-grounded generation, and citation display. Mapped to Sprint 4.

US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent) breaks into: T1 similarity search restricted to session's ready documents; T2 integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent); T3 handle no-ready-documents and no-relevant-content cases without fabricating answers; T4 graceful error handling for Gemini failures and missing API key. US-010 View source citations for each answer (3 pts, frontend-agent) has no sub-tasks listed.

**Related:** US-009, US-010

- ⚠ No delivery/ticket status reported for US-009, US-010, or US-009's sub-tasks.
- ⚠ Epic has no assigned role or point total in the input.

### EPIC-005 · approved · source: plan:EPIC-005

Chat History epic: retain and view full session chat history. Mapped to Sprint 4.

Story: US-011 Retain and view full session chat history (3 pts, backend-agent). No sub-tasks were listed, and no epic-level point total or owning role was provided.

**Related:** US-011

- ⚠ No delivery/ticket status reported for US-011.
- ⚠ Epic has no assigned role or point total in the input.

### DEV-RUN-STATUS · draft · source: dev:run-status

The development run is reported as 'completed' overall, but only one ticket result (US-008) was included in the input.

Development run status: completed. Only ticket reported: US-008 'Parse, chunk, and embed uploaded PDFs' -- status=delivered, commit=0d869fb8851066b8d0646d321b110f2c669942d5.

**Related:** US-008

- ⚠ Discrepancy: run status is 'completed' but delivery evidence (ticket status + commit) was only supplied for US-008; no ticket records were given for US-001 through US-007, US-009, US-010, or US-011, so their completion cannot be confirmed from this input.
- ⚠ No date/timestamp was provided for the run or for the US-008 delivery.
<!-- sdlc:auto:end narrative -->
