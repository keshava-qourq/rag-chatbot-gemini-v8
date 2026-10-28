# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### PLAN-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal: stand up authentication, per-user authorization, and the ability to create a chat session.

Sprint 1, capacity 20 points. Goal as stated in plan: 'Stand up authentication, per-user authorization, and the ability to create a chat session.' The plan input does not explicitly map backlog items to this sprint number, so item-to-sprint assignment is inferred only loosely from goal wording (likely EPIC-001/US-001-US-004) and is not asserted as fact here.

- ⚠ Plan input does not explicitly state which backlog items (US-xxx) were assigned to this sprint; mapping to EPIC-001/US-001-US-004 is a plausible inference only, not a stated fact.
- ⚠ No development run data ties any delivered ticket to this sprint.

### PLAN-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session.

Sprint 2, capacity 20 points. Goal as stated in plan: 'Enable browsing/switching sessions and uploading validated PDFs into a session.' Likely relates to US-006 (session switching) and US-007 (PDF upload), but the plan input does not explicitly assign items to sprint numbers.

- ⚠ Plan input does not explicitly state which backlog items were assigned to this sprint.
- ⚠ No development run data ties any delivered ticket to this sprint.

### PLAN-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Sprint 3, capacity 20 points. Goal as stated in plan: 'Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.' Likely relates to US-008 and its tasks, but the plan input does not explicitly assign items to sprint numbers.

- ⚠ Plan input does not explicitly state which backlog items were assigned to this sprint.
- ⚠ No development run data ties any delivered ticket to this sprint.

### PLAN-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history.

Sprint 4, capacity 20 points. Goal as stated in plan: 'Deliver grounded question answering with citations and full persistent chat history.' Likely relates to US-009 through US-016, but the plan input does not explicitly assign items to sprint numbers.

- ⚠ Plan input does not explicitly state which backlog items were assigned to this sprint.
- ⚠ Only US-014 and US-015 (from this likely range) have recorded development delivery; the rest have no dev status recorded.

### EPIC-001 · approved · source: plan:EPIC-001

Epic: User Accounts & Authentication -- covers sign up, log in, log out, and per-user workspace isolation.

Epic EPIC-001 (role unassigned at epic level) decomposes into: US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent).

**Related:** US-001, US-002, US-003, US-004

- ⚠ No development run record exists for US-001, US-002, US-003, or US-004 despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.

### EPIC-002 · approved · source: plan:EPIC-002

Epic: Chat Session Management -- covers creating and switching between chat sessions.

Epic EPIC-002 (role unassigned at epic level) decomposes into: US-005 Create a new chat session (2 pts, backend-agent); US-006 View and switch between my sessions (5 pts, frontend-agent).

**Related:** US-005, US-006

- ⚠ No development run record exists for US-005 or US-006 despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.

### EPIC-003 · approved · source: plan:EPIC-003

Epic: PDF Upload & Processing -- covers uploading PDFs to a session and parsing/chunking/embedding them.

Epic EPIC-003 (role unassigned at epic level) decomposes into: US-007 Upload a PDF to a chat session (8 pts, backend-agent), with tasks US-007-T1 Implement PDF upload endpoint with type/size/count validation, US-007-T2 Store accepted PDFs in S3 and persist document metadata, US-007-T3 Enqueue processing job on Redis queue after successful upload, US-007-T4 Implement document list endpoint with per-document status (all backend-agent); and US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent), with tasks US-008-T1 Implement PDF text extraction and page-aware chunking in worker (backend-agent), US-008-T2 Integrate gemini-embedding-001 calls to embed chunks (integration-agent), US-008-T3 Persist chunk embeddings into pgvector-backed document_chunks table (backend-agent), US-008-T4 Implement status transitions and failure handling for parse/API errors (backend-agent).

**Related:** US-007, US-008

- ⚠ No development run record exists for US-007 or US-008 (or their tasks) despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.

### EPIC-004 · approved · source: plan:EPIC-004

Epic: Retrieval-Augmented Question Answering -- covers grounded Q&A scoped to a session's documents, with citations.

Epic EPIC-004 (role unassigned at epic level) decomposes into: US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent), with tasks US-009-T1 Implement similarity search restricted to session's ready documents (backend-agent), US-009-T2 Integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent), US-009-T3 Handle no-ready-documents and no-relevant-content cases without fabricating answers (backend-agent), US-009-T4 Implement graceful error handling for Gemini failures and missing API key (backend-agent); and US-010 View source citations for each answer (3 pts, frontend-agent).

**Related:** US-009, US-010

- ⚠ No development run record exists for US-009 or US-010 (or US-009's tasks) despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.

### EPIC-005 · approved · source: plan:EPIC-005

Epic: Chat History -- covers retaining and viewing full session chat history.

Epic EPIC-005 (role unassigned at epic level) decomposes into: US-011 Retain and view full session chat history (3 pts, backend-agent).

**Related:** US-011

- ⚠ No development run record exists for US-011 despite the dev run being marked completed; delivery status for this epic's story is unconfirmed.

### BACKLOG-FRONTEND-DEVOPS-QA · approved · source: plan:backlog

Backlog items without a listed parent epic: frontend wiring for uploads/errors/status, devops worker deployment, and end-to-end QA verification.

Planned items: US-012 Wire Upload PDF form to the real upload endpoint (3 pts, frontend-agent); US-013 Show real backend errors for rejected uploads (2 pts, frontend-agent); US-014 Refresh Documents list to reflect real processing status (3 pts, frontend-agent); US-015 Run the RQ worker for the 'documents' queue alongside the API in the deployed container (3 pts, devops-agent); US-016 End-to-end verification that uploaded PDFs are processed and surfaced correctly (2 pts, qa-agent). Of these, US-014 and US-015 have confirmed development delivery records (see DEV-US-014, DEV-US-015); US-012, US-013, and US-016 do not.

**Related:** US-012, US-013, US-014, US-015, US-016

- ⚠ No development run record exists for US-012, US-013, or US-016 despite the overall dev run being marked 'completed' -- this is a discrepancy between claimed phase status and recorded ticket-level evidence and should be reconciled.

### DEV-US-014 · approved · source: dev:TICKET-US-014

US-014 (Refresh Documents list to reflect real processing status) was delivered.

Ticket US-014: 'Refresh Documents list to reflect real processing status' -- status=delivered, commit=ec68726419d27c48befdb4bc13ca3122a8b9963c. Planned as a 3-point frontend-agent story.

**Related:** US-014

### DEV-US-015 · approved · source: dev:TICKET-US-015

US-015 (Run the RQ worker for the 'documents' queue alongside the API in the deployed container) was delivered.

Ticket US-015: 'Run the RQ worker for the 'documents' queue alongside the API in the deployed container' -- status=delivered, commit=ec68726419d27c48befdb4bc13ca3122a8b9963c (same commit as US-014). Planned as a 3-point devops-agent story.

**Related:** US-015

- ⚠ US-014 and US-015 share the identical commit hash, which may indicate they were delivered together in one commit/PR; this is noted but not confirmed as intentional or erroneous by the input.

### DEV-RUN-STATUS · approved · source: development run status

The development run for this phase is marked 'completed', but only 2 of the 16 planned stories have recorded ticket-level delivery evidence.

Development run status: completed. Only two tickets appear in the run output: US-014 and US-015, both delivered via commit ec68726419d27c48befdb4bc13ca3122a8b9963c. No ticket records were provided for US-001 through US-013 or US-016, all of which appear in the approved plan.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012, US-013, US-016

- ⚠ Discrepancy: run status says 'completed' but 14 of 16 planned stories (US-001-US-013, US-016) have no delivery ticket in the input -- unclear whether they were delivered without being logged, descoped, or still pending. Needs reconciliation with the planning/dev team.
- ⚠ No commit, PR, or code artifact references were provided for US-001 through US-013 or US-016.
<!-- sdlc:auto:end narrative -->
