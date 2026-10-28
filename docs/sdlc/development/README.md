# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-V1 · approved · source: plan

Development plan version 1 was approved, organizing the project into 5 epics (Accounts & Auth, Chat Session Management, PDF Upload & Processing, Retrieval-Augmented QA, Chat History) covering all 11 known user stories plus supporting engineering tasks.

Plan status: approved, version 1. Epics: EPIC-001 User Accounts & Authentication (US-001 sign up, US-002 log in, US-003 log out, US-004 private per-user workspace); EPIC-002 Chat Session Management (US-005 create session, US-006 view/switch sessions); EPIC-003 PDF Upload & Processing (US-007 upload PDF with tasks for upload endpoint validation, S3 storage + metadata persistence, Redis enqueue, document list endpoint; US-008 parse/chunk/embed with tasks for text extraction/chunking, gemini-embedding-001 integration, pgvector persistence, status/failure handling); EPIC-004 Retrieval-Augmented Question Answering (US-009 scoped question answering with tasks for similarity search, gemini-2.5-flash grounded generation, no-ready-document/no-relevant-content handling, Gemini failure/missing-key handling; US-010 source citations); EPIC-005 Chat History (US-011 retain/view full session chat history). Role assignments given per item (backend-agent, frontend-agent, security-agent, integration-agent).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ Plan input does not state which backlog items/tasks are assigned to which sprint -- only per-sprint goals and capacities are given, so sprint-to-item mapping below is inferred thematically, not confirmed.
- ⚠ Epics themselves carry no story points or assigned role in the input.

### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal was to stand up authentication, per-user authorization, and the ability to create a chat session, with a capacity of 20 points.

Sprint 1 (goal: 'Stand up authentication, per-user authorization, and the ability to create a chat session.', capacity=20). Thematically this aligns with EPIC-001 (US-001 sign up, US-002 log in, US-003 log out, US-004 private workspace) and the first part of EPIC-002 (US-005 create session), based on goal wording -- the plan input does not explicitly list which tickets were pulled into this sprint.

**Related:** US-001, US-002, US-003, US-004

- ⚠ No explicit item-to-sprint assignment was provided; association above is inferred from the sprint goal text only.

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal was to enable browsing/switching sessions and uploading validated PDFs into a session, with a capacity of 20 points.

Sprint 2 (goal: 'Enable browsing/switching sessions and uploading validated PDFs into a session.', capacity=20). Thematically aligns with EPIC-002 (US-006 view/switch sessions) and the upload portion of EPIC-003 (US-007 upload a PDF, including its sub-tasks for endpoint validation, S3 storage, queue enqueue, and document list endpoint) -- no explicit item-to-sprint list was given.

**Related:** US-005, US-006, US-007

- ⚠ No explicit item-to-sprint assignment was provided; association above is inferred from the sprint goal text only.

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal was to build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector, with a capacity of 20 points.

Sprint 3 (goal: 'Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.', capacity=20). Thematically aligns with US-008 and its sub-tasks (text extraction/chunking, gemini-embedding-001 integration, pgvector persistence, status/failure handling) -- no explicit item-to-sprint list was given.

**Related:** US-008

- ⚠ No explicit item-to-sprint assignment was provided; association above is inferred from the sprint goal text only.

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal was to deliver grounded question answering with citations and full persistent chat history, with a capacity of 20 points.

Sprint 4 (goal: 'Deliver grounded question answering with citations and full persistent chat history.', capacity=20). Thematically aligns with EPIC-004 (US-009 scoped QA with its sub-tasks for similarity search, gemini-2.5-flash integration, empty/no-match handling, Gemini error handling; US-010 citations) and EPIC-005 (US-011 chat history) -- no explicit item-to-sprint list was given.

**Related:** US-009, US-010, US-011

- ⚠ No explicit item-to-sprint assignment was provided; association above is inferred from the sprint goal text only.

### DEV-TICKET-US-008 · approved · source: dev:TICKET US-008

Ticket US-008 ('Parse, chunk, and embed uploaded PDFs') was delivered, implementing the background pipeline that extracts text, chunks it page-aware, embeds chunks via gemini-embedding-001, and persists embeddings to a pgvector-backed document_chunks table.

Ticket US-008 status=delivered, commit=c67d81dedef9e5ad74b55735a0e25c081241819a. This story's planned sub-tasks (per the plan input) were: US-008-T1 PDF text extraction and page-aware chunking in worker; US-008-T2 integrate gemini-embedding-001 calls to embed chunks; US-008-T3 persist chunk embeddings into pgvector-backed document_chunks table; US-008-T4 implement status transitions and failure handling for parse/API errors. The development run input does not separately confirm completion of each sub-task -- only the parent ticket is marked delivered with a single commit.

**Related:** US-008, US-007, EPIC-003

- ⚠ No per-sub-task (US-008-T1..T4) completion confirmation was given, only the parent ticket's delivered status and commit.
- ⚠ No test or review evidence was included in this phase's input for this ticket.

### DEV-UNDELIVERED-ITEMS · draft · source: dev

Development run status is reported as 'completed' at the phase level, but ticket-level delivery evidence was supplied only for US-008 -- the other 10 planned stories have no recorded ticket status, commit, or delivery confirmation in this input.

Development run status: completed. Only one ticket record was provided (US-008). No ticket entries were given for US-001 (sign up), US-002 (log in), US-003 (log out), US-004 (private workspace), US-005 (create session), US-006 (view/switch sessions), US-007 (upload PDF), US-009 (ask question), US-010 (view citations), or US-011 (chat history), despite these being part of the approved plan.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-009, US-010, US-011

- ⚠ Discrepancy: phase-level run status says 'completed' but 10 of 11 planned stories have no ticket-level delivery record in the input -- flagging for confirmation rather than assuming they were delivered or skipped.
- ⚠ No commit references, review notes, or task-level status exist for these items in this phase's input.
<!-- sdlc:auto:end narrative -->
