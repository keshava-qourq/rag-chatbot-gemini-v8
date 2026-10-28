# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### PLAN-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 planned to stand up authentication, per-user authorization, and chat-session creation.

Sprint 1 goal: 'Stand up authentication, per-user authorization, and the ability to create a chat session.' Capacity: 20 points. Goal text thematically aligns with EPIC-001 (User Accounts & Authentication) and US-005 (create chat session), but the plan input does not explicitly assign stories to this sprint.

**Related:** US-001, US-002, US-003, US-004

- ⚠ No explicit item-to-sprint assignment given in input; alignment with EPIC-001/US-005 is inferred from goal wording only.
- ⚠ No development run confirmation of completion for this sprint's likely scope.

### PLAN-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 planned to enable session browsing/switching and validated PDF uploads.

Sprint 2 goal: 'Enable browsing/switching sessions and uploading validated PDFs into a session.' Capacity: 20 points. Thematically aligns with US-006 (view/switch sessions) and US-007 (upload PDF to session), inferred from goal wording.

**Related:** US-006, US-007

- ⚠ No explicit item-to-sprint assignment given in input.
- ⚠ No development run confirmation of completion for this sprint's likely scope.

### PLAN-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 planned to build the background PDF parsing, chunking, and embedding pipeline.

Sprint 3 goal: 'Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.' Capacity: 20 points. Thematically aligns with US-008 and its subtasks (T1-T4), inferred from goal wording.

**Related:** US-008

- ⚠ No explicit item-to-sprint assignment given in input.
- ⚠ No development run confirmation of completion for this sprint's likely scope.

### PLAN-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 planned to deliver grounded question answering with citations and full persistent chat history.

Sprint 4 goal: 'Deliver grounded question answering with citations and full persistent chat history.' Capacity: 20 points. Thematically aligns with US-009, US-010, US-011, inferred from goal wording.

**Related:** US-009, US-010, US-011

- ⚠ No explicit item-to-sprint assignment given in input.
- ⚠ Items US-012 through US-016 appear in the backlog after this sprint's listed goal but are not explicitly assigned to any sprint.
- ⚠ No development run confirmation of completion for this sprint's likely scope.

### EPIC-001 · approved · source: plan:EPIC-001

Epic covering user account creation, authentication, and per-user workspace isolation.

Child stories: US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent). No task-level breakdown provided for this epic's stories.

**Related:** US-001, US-002, US-003, US-004

- ⚠ No development run status recorded for US-001 through US-004 in this input.

### EPIC-002 · approved · source: plan:EPIC-002

Epic covering chat session creation and session browsing/switching.

Child stories: US-005 Create a new chat session (2 pts, backend-agent); US-006 View and switch between my sessions (5 pts, frontend-agent). No task-level breakdown provided for this epic's stories.

**Related:** US-005, US-006

- ⚠ No development run status recorded for US-005 or US-006 in this input.

### EPIC-003 · approved · source: plan:EPIC-003

Epic covering PDF upload and the background parse/chunk/embed processing pipeline.

US-007 Upload a PDF to a chat session (8 pts, backend-agent), with tasks: US-007-T1 Implement PDF upload endpoint with type/size/count validation; US-007-T2 Store accepted PDFs in S3 and persist document metadata; US-007-T3 Enqueue processing job on Redis queue after successful upload; US-007-T4 Implement document list endpoint with per-document status (all backend-agent). US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent), with tasks: US-008-T1 Implement PDF text extraction and page-aware chunking in worker (backend-agent); US-008-T2 Integrate gemini-embedding-001 calls to embed chunks (integration-agent); US-008-T3 Persist chunk embeddings into pgvector-backed document_chunks table (backend-agent); US-008-T4 Implement status transitions and failure handling for parse/API errors (backend-agent).

**Related:** US-007, US-008

- ⚠ No development run status recorded for US-007, US-008, or their subtasks in this input.

### EPIC-004 · approved · source: plan:EPIC-004

Epic covering retrieval-augmented question answering with citations, scoped to a session's ready documents.

US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent), with tasks: US-009-T1 Implement similarity search restricted to session's ready documents (backend-agent); US-009-T2 Integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent); US-009-T3 Handle no-ready-documents and no-relevant-content cases without fabricating answers (backend-agent); US-009-T4 Implement graceful error handling for Gemini failures and missing API key (backend-agent). US-010 View source citations for each answer (3 pts, frontend-agent).

**Related:** US-009, US-010

- ⚠ No development run status recorded for US-009, US-010, or US-009's subtasks in this input.

### EPIC-005 · approved · source: plan:EPIC-005

Epic covering retention and viewing of full session chat history.

Child story: US-011 Retain and view full session chat history (3 pts, backend-agent). No task-level breakdown provided.

**Related:** US-011

- ⚠ No development run status recorded for US-011 in this input.

### US-012 · approved · source: dev:US-012

Frontend upload form was wired to the real backend upload endpoint.

Ticket US-012 'Wire Upload PDF form to the real upload endpoint' delivered under commit 7d3b348345db46aba521525eb73b92839a81e617 (frontend-agent, planned 3 pts). Relates to US-007 (PDF upload endpoint).

**Related:** US-012, US-007

### US-013 · approved · source: dev:US-013

Real backend error messages are now surfaced in the UI for rejected uploads.

Ticket US-013 'Show real backend errors for rejected uploads' delivered under commit 7d3b348345db46aba521525eb73b92839a81e617 (frontend-agent, planned 2 pts). Relates to US-007 (upload validation).

**Related:** US-013, US-007

### US-014 · draft · source: plan:US-014

Planned story to refresh the Documents list so it reflects real processing status.

Plan item US-014 'Refresh Documents list to reflect real processing status' (3 pts, frontend-agent). No ticket-level delivery record found in the development run input.

**Related:** US-014, US-007, US-008

- ⚠ Not listed in the development run's delivered tickets; completion status unconfirmed.

### US-015 · draft · source: plan:US-015

Planned story to run the RQ 'documents' worker alongside the API in the deployed container.

Plan item US-015 'Run the RQ worker for the 'documents' queue alongside the API in the deployed container' (3 pts, devops-agent). No ticket-level delivery record found in the development run input.

**Related:** US-015

- ⚠ Not listed in the development run's delivered tickets; completion status unconfirmed.

### US-016 · draft · source: plan:US-016

Planned story for end-to-end verification that uploaded PDFs are processed and surfaced correctly.

Plan item US-016 'End-to-end verification that uploaded PDFs are processed and surfaced correctly' (2 pts, qa-agent). No ticket-level delivery record found in the development run input.

**Related:** US-016

- ⚠ Not listed in the development run's delivered tickets; completion status unconfirmed.

### DEV-RUN-STATUS · approved · source: dev:run-status

The development run is recorded as 'completed', but only two of sixteen planned stories have ticket-level delivery evidence.

Development run status field reads 'completed'. The only ticket-level records provided are US-012 and US-013, both delivered under commit 7d3b348345db46aba521525eb73b92839a81e617. No ticket-level records were given for US-001 through US-011, US-014, US-015, or US-016.

**Related:** US-012, US-013

- ⚠ Discrepancy: overall run status is 'completed' but 14 of 16 planned stories (US-001–US-011, US-014–US-016) have no ticket-level delivery record in this input -- needs human verification of whether this is an incomplete report or an actual scope gap.
<!-- sdlc:auto:end narrative -->
