# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN · approved · source: plan:Rag_chatbot_gemini_v8

Development plan approved at version 2, organized into 4 sprints covering authentication, session management, PDF upload/processing, and grounded Q&A with chat history.

Plan status: approved, version 2. Backlog organized into 5 epics: EPIC-001 User Accounts & Authentication, EPIC-002 Chat Session Management, EPIC-003 PDF Upload & Processing, EPIC-004 Retrieval-Augmented Question Answering, EPIC-005 Chat History -- plus follow-on frontend integration stories (US-012, US-013, US-014), a devops story (US-015), and a QA verification story (US-016) that appear in the backlog without an explicit epic parent.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012, US-013, US-014, US-015, US-016

- ⚠ No explicit mapping provided between backlog items and the sprint in which each was actually completed.

### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal: stand up authentication, per-user authorization, and the ability to create a chat session.

Capacity: 20 points. Goal as stated in plan: 'Stand up authentication, per-user authorization, and the ability to create a chat session.'

- ⚠ No explicit list of which backlog items (e.g. US-001..US-005) were assigned to or completed in this sprint was given.

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session.

Capacity: 20 points. Goal as stated in plan: 'Enable browsing/switching sessions and uploading validated PDFs into a session.'

- ⚠ No explicit list of which backlog items were assigned to or completed in this sprint was given.

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Capacity: 20 points. Goal as stated in plan: 'Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.'

- ⚠ No explicit list of which backlog items were assigned to or completed in this sprint was given.

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history.

Capacity: 20 points. Goal as stated in plan: 'Deliver grounded question answering with citations and full persistent chat history.'

- ⚠ No explicit list of which backlog items were assigned to or completed in this sprint was given.

### EPIC-001 · approved · source: plan:EPIC-001

Epic covering user signup, login, logout, and per-user data isolation.

Child stories: US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent). Total 13 points, aligned with Sprint 1's authentication/authorization goal.

**Related:** US-001, US-002, US-003, US-004

- ⚠ No per-ticket completion/delivery status given for US-001 through US-004; only the overall dev run is marked 'completed'.

### EPIC-002 · approved · source: plan:EPIC-002

Epic covering chat session creation and session browsing/switching.

Child stories: US-005 Create a new chat session (2 pts, backend-agent); US-006 View and switch between my sessions (5 pts, frontend-agent). Aligns with Sprint 1 (session creation) and Sprint 2 (browsing/switching) goals.

**Related:** US-005, US-006

- ⚠ No per-ticket completion/delivery status given for US-005 or US-006.

### EPIC-003 · approved · source: plan:EPIC-003

Epic covering PDF upload handling and the background parse/chunk/embed pipeline.

US-007 Upload a PDF to a chat session (8 pts, backend-agent), broken into: T1 upload endpoint with type/size/count validation; T2 store accepted PDFs in S3 and persist document metadata; T3 enqueue processing job on Redis queue after successful upload; T4 document list endpoint with per-document status. US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent), broken into: T1 PDF text extraction and page-aware chunking in worker; T2 integrate gemini-embedding-001 to embed chunks (integration-agent); T3 persist chunk embeddings into pgvector-backed document_chunks table; T4 status transitions and failure handling for parse/API errors. Aligns with Sprint 2 (upload) and Sprint 3 (embedding pipeline) goals.

**Related:** US-007, US-008

- ⚠ Task-level (T1-T4) completion status not reported individually; only the aggregate dev run status of 'completed' is available.

### EPIC-004 · approved · source: plan:EPIC-004

Epic covering grounded question answering scoped to session documents, plus citation display.

US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent), broken into: T1 similarity search restricted to session's ready documents; T2 integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent); T3 handle no-ready-documents and no-relevant-content cases without fabricating answers; T4 graceful error handling for Gemini failures and missing API key. US-010 View source citations for each answer (3 pts, frontend-agent). Aligns with Sprint 4 goal.

**Related:** US-009, US-010

- ⚠ Task-level completion status not reported individually for US-009's sub-tasks or for US-010.

### EPIC-005 · approved · source: plan:EPIC-005

Epic covering persistent, viewable chat history for a session.

Child story: US-011 Retain and view full session chat history (3 pts, backend-agent). Aligns with Sprint 4 goal of delivering full persistent chat history.

**Related:** US-011

- ⚠ No per-ticket completion/delivery status given for US-011.

### US-012 · approved · source: plan:US-012

Wire the Upload PDF form in the UI to the real backend upload endpoint.

3 points, frontend-agent. Listed in the backlog without an explicit epic parent; functionally connects the frontend upload form to the upload endpoint delivered under US-007 (EPIC-003).

**Related:** US-007

- ⚠ Epic grouping not explicit in input (inferred from functional relationship to US-007).
- ⚠ No individual completion/delivery status reported for this ticket.

### US-013 · approved · source: plan:US-013

Show real backend error messages to the user when an upload is rejected.

2 points, frontend-agent. Listed without an explicit epic parent; relates functionally to the upload validation implemented under US-007-T1.

**Related:** US-007

- ⚠ Epic grouping not explicit in input (inferred).
- ⚠ No individual completion/delivery status reported for this ticket.

### US-014 · approved · source: plan:US-014

Refresh the Documents list in the UI to reflect real processing status from the backend.

3 points, frontend-agent. Listed without an explicit epic parent; relates functionally to the document list/status endpoint (US-007-T4) and processing status transitions (US-008-T4).

**Related:** US-007, US-008

- ⚠ Epic grouping not explicit in input (inferred).
- ⚠ No individual completion/delivery status reported for this ticket.

### US-015 · approved · source: plan:US-015

Run the RQ worker for the 'documents' queue alongside the API in the deployed container.

3 points, devops-agent. Ensures the background worker that processes jobs enqueued by US-007-T3 and executes the parsing/embedding pipeline from US-008 actually runs in the deployed environment.

**Related:** US-007, US-008

- ⚠ This is a deployment/runtime configuration concern; no confirmation of actual deployed execution is available in this development-phase input (belongs to deployment phase evidence).

### US-016 · approved · source: development:US-016

End-to-end verification that uploaded PDFs are processed and surfaced correctly in the UI.

2 points, qa-agent. Per development run data: status=delivered, commit=3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf. This is the only ticket in this input with an explicit per-ticket status and commit reference.

**Related:** US-007, US-008, US-014

### DEV-RUN-STATUS · approved · source: development:run

The development run for this phase is reported as 'completed' overall, but only one ticket (US-016) has explicit per-ticket status and commit evidence in the provided input.

Development run status: completed. Only ticket explicitly detailed: US-016 (End-to-end verification that uploaded PDFs are processed and surfaced correctly) - status=delivered, commit=3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012, US-013, US-014, US-015, US-016

- ⚠ Discrepancy: the run is marked 'completed' at the aggregate level, but no explicit status or commit evidence was provided for US-001 through US-015 individually -- their actual implementation/delivery state cannot be confirmed from this input.
<!-- sdlc:auto:end narrative -->
