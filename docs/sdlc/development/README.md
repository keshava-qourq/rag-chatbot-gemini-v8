# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-001 · approved · source: plan:v1

Overall development plan is approved at version 1, organized into 4 sprints of 20-point capacity each, covering 5 epics: Accounts/Auth, Chat Session Management, PDF Upload & Processing, Retrieval-Augmented QA, and Chat History.

Plan status: approved, version 1. Sprints: Sprint 1 (auth + authorization + create session), Sprint 2 (session browsing/switching + validated PDF upload), Sprint 3 (background parse/chunk/embed pipeline into pgvector), Sprint 4 (grounded QA with citations + persistent chat history). No explicit decision rationale, approver identity, or approval date was provided in the input.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ No record of who approved the plan or when.
- ⚠ No execution/progress status (in-progress, done, blocked) given for any sprint or item — only the backlog plan itself was provided.

### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal is to stand up authentication, per-user authorization, and the ability to create a chat session.

Planned backlog items: EPIC-001 User Accounts & Authentication (role unassigned); US-001 Sign up with email and password (3 pts, backend-agent); US-002 Log in with email and password (3 pts, backend-agent); US-003 Log out of the application (2 pts, backend-agent); US-004 Private, isolated workspace per user (5 pts, security-agent); US-005 Create a new chat session (2 pts, backend-agent). Sprint capacity: 20 points.

**Related:** US-001, US-002, US-003, US-004, US-005

- ⚠ No evidence provided that these items were actually implemented or completed — only planned.

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal is to enable browsing/switching between chat sessions and uploading validated PDFs into a session.

Planned backlog items: US-006 View and switch between my sessions (5 pts, frontend-agent); US-007 Upload a PDF to a chat session (8 pts, backend-agent), broken into: US-007-T1 PDF upload endpoint with type/size/count validation; US-007-T2 Store accepted PDFs in S3 and persist document metadata; US-007-T3 Enqueue processing job on Redis queue after successful upload; US-007-T4 Document list endpoint with per-document status. Sprint capacity: 20 points.

**Related:** US-006, US-007

- ⚠ No evidence provided that these items or sub-tasks were actually implemented or completed — only planned.
- ⚠ No detail on validation rules (allowed file types, size/count limits) beyond the task title.

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal is to build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Planned backlog item: US-008 Parse, chunk, and embed uploaded PDFs (13 pts, backend-agent), broken into: US-008-T1 PDF text extraction and page-aware chunking in worker; US-008-T2 Integrate gemini-embedding-001 calls to embed chunks (integration-agent); US-008-T3 Persist chunk embeddings into pgvector-backed document_chunks table; US-008-T4 Status transitions and failure handling for parse/API errors. Sprint capacity: 20 points.

**Related:** US-008

- ⚠ No evidence provided that these items or sub-tasks were actually implemented or completed — only planned.
- ⚠ No specifics given on chunking strategy parameters (chunk size, overlap) or failure-handling behavior beyond task titles.

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal is to deliver grounded question answering with citations and full persistent chat history.

Planned backlog items: US-009 Ask a question scoped to the active session's documents (8 pts, backend-agent), broken into: US-009-T1 Similarity search restricted to session's ready documents; US-009-T2 Integrate gemini-2.5-flash generation grounded in retrieved chunks (integration-agent); US-009-T3 Handle no-ready-documents and no-relevant-content cases without fabricating answers; US-009-T4 Graceful error handling for Gemini failures and missing API key. US-010 View source citations for each answer (3 pts, frontend-agent). US-011 Retain and view full session chat history (3 pts, backend-agent). Sprint capacity: 20 points.

**Related:** US-009, US-010, US-011

- ⚠ No evidence provided that these items or sub-tasks were actually implemented or completed — only planned.
- ⚠ No detail on how citations are rendered or on chat history retention limits/format beyond the story titles.
<!-- sdlc:auto:end narrative -->
