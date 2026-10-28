# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-001 · approved · source: plan

Approved plan v1 organizes the project into 5 epics and 4 sprints of capacity 20 each, covering auth, session management, PDF upload/processing, retrieval-augmented QA, and chat history.

Sprint 1 goal: stand up authentication, per-user authorization, and chat session creation (maps to US-001, US-002, US-003, US-004, US-005). Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs (US-006, US-007). Sprint 3 goal: build background pipeline to parse, chunk, and embed PDFs into pgvector (US-008). Sprint 4 goal: deliver grounded QA with citations and persistent chat history (US-009, US-010, US-011). Epics: EPIC-001 User Accounts & Authentication, EPIC-002 Chat Session Management, EPIC-003 PDF Upload & Processing, EPIC-004 Retrieval-Augmented Question Answering, EPIC-005 Chat History.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

### DEV-RUN-2026 · draft · source: dev:run-status

Development run is marked 'completed' but only 2 of the 11 planned stories have recorded ticket status.

Run status field states 'completed'. Only two tickets were reported with outcomes: US-006 (delivered, commit 65402495f65f12c5ac3a1bca760dbb186874d04e) and US-007 (delivered, commit 02bd1f2a3ca016bb68dc219b620a90cd64104ead). No ticket entries were provided for US-001, US-002, US-003, US-004, US-005, US-008, US-009, US-010, or US-011.

**Related:** US-006, US-007

- ⚠ Discrepancy: run status says 'completed' but 9 of 11 planned stories (US-001-005, US-008-011) have no ticket outcome recorded -- unclear if they were actually implemented, skipped, or simply not reported.

### US-001 · draft · source: plan:US-001

Planned story: sign up with email and password.

Plan item US-001, 3 points, assigned role backend-agent, part of EPIC-001 (User Accounts & Authentication), scheduled under Sprint 1 goal (auth/authorization/session creation).

**Related:** EPIC-001

- ⚠ No development ticket status reported for this story despite the development run being marked completed.

### US-002 · draft · source: plan:US-002

Planned story: log in with email and password.

Plan item US-002, 3 points, assigned role backend-agent, part of EPIC-001, scheduled under Sprint 1.

**Related:** EPIC-001

- ⚠ No development ticket status reported for this story despite the development run being marked completed.

### US-003 · draft · source: plan:US-003

Planned story: log out of the application.

Plan item US-003, 2 points, assigned role backend-agent, part of EPIC-001, scheduled under Sprint 1.

**Related:** EPIC-001

- ⚠ No development ticket status reported for this story despite the development run being marked completed.

### US-004 · draft · source: plan:US-004

Planned story: private, isolated workspace per user.

Plan item US-004, 5 points, assigned role security-agent, part of EPIC-001, scheduled under Sprint 1.

**Related:** EPIC-001

- ⚠ No development ticket status reported for this story despite the development run being marked completed.

### US-005 · draft · source: plan:US-005

Planned story: create a new chat session.

Plan item US-005, 2 points, assigned role backend-agent, part of EPIC-002 (Chat Session Management), scheduled under Sprint 1.

**Related:** EPIC-002

- ⚠ No development ticket status reported for this story despite the development run being marked completed.

### US-006 · approved · source: dev:US-006

Delivered story: view and switch between chat sessions.

Plan item US-006, 5 points, assigned role frontend-agent, part of EPIC-002, scheduled under Sprint 2. Development run reports status=delivered, commit=65402495f65f12c5ac3a1bca760dbb186874d04e.

**Related:** EPIC-002

### US-007 · approved · source: dev:US-007

Delivered story: upload a PDF to a chat session, including validation, storage, and processing enqueue.

Plan item US-007, 8 points, assigned role backend-agent, part of EPIC-003 (PDF Upload & Processing), scheduled under Sprint 2. Subtasks per plan: US-007-T1 implement upload endpoint with type/size/count validation; US-007-T2 store accepted PDFs in S3 and persist metadata; US-007-T3 enqueue processing job on Redis queue after successful upload; US-007-T4 implement document list endpoint with per-document status. Development run reports status=delivered, commit=02bd1f2a3ca016bb68dc219b620a90cd64104ead.

**Related:** EPIC-003, US-007-T1, US-007-T2, US-007-T3, US-007-T4

- ⚠ Delivery status covers the parent story only; no individual confirmation per subtask (T1-T4) was reported.

### US-008 · draft · source: plan:US-008

Planned story: parse, chunk, and embed uploaded PDFs.

Plan item US-008, 13 points, assigned role backend-agent, part of EPIC-003, scheduled under Sprint 3. Subtasks per plan: US-008-T1 PDF text extraction and page-aware chunking in worker; US-008-T2 integrate gemini-embedding-001 calls to embed chunks (role integration-agent); US-008-T3 persist chunk embeddings into pgvector-backed document_chunks table; US-008-T4 implement status transitions and failure handling for parse/API errors.

**Related:** EPIC-003, US-008-T1, US-008-T2, US-008-T3, US-008-T4

- ⚠ No development ticket status reported for this story or its subtasks despite the development run being marked completed.

### US-009 · draft · source: plan:US-009

Planned story: ask a question scoped to the active session's documents.

Plan item US-009, 8 points, assigned role backend-agent, part of EPIC-004 (Retrieval-Augmented Question Answering), scheduled under Sprint 4. Subtasks per plan: US-009-T1 similarity search restricted to session's ready documents; US-009-T2 integrate gemini-2.5-flash generation grounded in retrieved chunks (role integration-agent); US-009-T3 handle no-ready-documents and no-relevant-content cases without fabricating answers; US-009-T4 implement graceful error handling for Gemini failures and missing API key.

**Related:** EPIC-004, US-009-T1, US-009-T2, US-009-T3, US-009-T4

- ⚠ No development ticket status reported for this story or its subtasks despite the development run being marked completed.

### US-010 · draft · source: plan:US-010

Planned story: view source citations for each answer.

Plan item US-010, 3 points, assigned role frontend-agent, part of EPIC-004, scheduled under Sprint 4.

**Related:** EPIC-004, US-009

- ⚠ No development ticket status reported for this story despite the development run being marked completed.

### US-011 · draft · source: plan:US-011

Planned story: retain and view full session chat history.

Plan item US-011, 3 points, assigned role backend-agent, part of EPIC-005 (Chat History), scheduled under Sprint 4.

**Related:** EPIC-005

- ⚠ No development ticket status reported for this story despite the development run being marked completed.
<!-- sdlc:auto:end narrative -->
