# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### PLAN-DEV-V1 · approved · source: plan:v1

Development plan version 1, approved, organized into 4 sprints of capacity 20 each, covering authentication, session management, PDF upload/processing, and retrieval-augmented QA with history.

Sprint 1: Stand up authentication, per-user authorization, and the ability to create a chat session (capacity 20) -- covers EPIC-001 (US-001 sign up, US-002 log in, US-003 log out, US-004 private isolated workspace) and start of EPIC-002 (US-005 create session). Sprint 2: Enable browsing/switching sessions and uploading validated PDFs into a session (capacity 20) -- covers US-006 (view/switch sessions, frontend-agent) and US-007 upload PDF (backend-agent, 8 points) with sub-tasks US-007-T1 (upload endpoint with validation), US-007-T2 (S3 storage + metadata), US-007-T3 (enqueue processing job on Redis), US-007-T4 (document list endpoint with status). Sprint 3: Build background pipeline to parse, chunk, and embed uploaded PDFs into pgvector (capacity 20) -- covers US-008 (13 points) with sub-tasks US-008-T1 (text extraction/chunking), US-008-T2 (gemini-embedding-001 integration, integration-agent), US-008-T3 (persist embeddings to pgvector document_chunks table), US-008-T4 (status transitions/failure handling). Sprint 4: Deliver grounded QA with citations and full persistent chat history (capacity 20) -- covers US-009 (8 points) with sub-tasks US-009-T1 (similarity search scoped to ready documents), US-009-T2 (gemini-2.5-flash grounded generation, integration-agent), US-009-T3 (handle no-ready-document/no-relevant-content cases without fabrication), US-009-T4 (graceful error handling for Gemini failures/missing API key); US-010 (view citations, 3 points, frontend-agent); US-011 (retain/view full chat history, 3 points, backend-agent, EPIC-005).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

### DEV-US-001 · approved · source: dev:US-001

Sign-up with email and password implemented and delivered.

Ticket US-001 (story, 3 points, backend-agent, part of EPIC-001 and Sprint 1) marked delivered, commit 3de38602a0d9e1ddf4eb2c5d1cada4524e5aef0c.

**Related:** US-001, EPIC-001

### DEV-US-002 · approved · source: dev:US-002

Log in with email and password implemented and delivered.

Ticket US-002 (story, 3 points, backend-agent, part of EPIC-001 and Sprint 1) marked delivered, commit e1e23ce9567967b5c332765149f46993587296b7.

**Related:** US-002, EPIC-001

- ⚠ Commit hash for US-002 is 41 characters, one longer than a standard 40-character SHA-1 hash -- possible transcription issue in the source input.

### DEV-US-003 · approved · source: dev:US-003

Log out functionality implemented and delivered.

Ticket US-003 (story, 2 points, backend-agent, part of EPIC-001 and Sprint 1) marked delivered, commit e4419670761d0e50f2426dc9d386f7566b86c554.

**Related:** US-003, EPIC-001

### DEV-US-004 · approved · source: dev:US-004

Private, isolated per-user workspace implemented and delivered.

Ticket US-004 (story, 5 points, security-agent, part of EPIC-001 and Sprint 1) marked delivered, commit e4419670761d0e50f2426dc9d386f7566b86c554 (same commit hash as US-003 -- these two tickets appear to have shipped in the same commit).

**Related:** US-004, EPIC-001

- ⚠ US-003 and US-004 share the identical commit hash; confirm whether this is a single combined commit or a data entry duplication.

### DEV-US-005 · approved · source: dev:US-005

Create a new chat session implemented and delivered.

Ticket US-005 (story, 2 points, backend-agent, part of EPIC-002, planned within Sprint 1's goal of enabling session creation) marked delivered, commit e4419670761d0e50f2426dc9d386f7566b86c554 (same commit hash as US-003/US-004).

**Related:** US-005, EPIC-002

- ⚠ Commit hash is identical across US-003, US-004, and US-005; confirm whether these were genuinely a single combined commit.

### DEV-US-006 · draft · source: plan:Sprint 2

View and switch between chat sessions -- planned for Sprint 2, no delivery ticket reported.

Story US-006 (5 points, frontend-agent) is part of EPIC-002 and planned in Sprint 2 (goal: enable browsing/switching sessions and uploading validated PDFs). No ticket/commit status was included in the development run input for this story.

**Related:** US-006, EPIC-002

- ⚠ Development run status is 'completed' but no ticket entry exists for US-006 in the input; actual delivery status is unknown.

### DEV-US-007 · draft · source: plan:Sprint 2

Upload a PDF to a chat session -- planned for Sprint 2 with four sub-tasks, no delivery ticket reported.

Story US-007 (8 points, backend-agent) is part of EPIC-003 and planned in Sprint 2. Sub-tasks: US-007-T1 (upload endpoint with type/size/count validation), US-007-T2 (store accepted PDFs in S3, persist metadata), US-007-T3 (enqueue processing job on Redis queue), US-007-T4 (document list endpoint with per-document status). No ticket/commit status reported for the story or any of its sub-tasks.

**Related:** US-007, EPIC-003

- ⚠ Development run status is 'completed' but no ticket entry exists for US-007 or its sub-tasks (T1-T4); actual delivery status is unknown.

### DEV-US-008 · draft · source: plan:Sprint 3

Parse, chunk, and embed uploaded PDFs -- planned for Sprint 3 with four sub-tasks, no delivery ticket reported.

Story US-008 (13 points, backend-agent) is part of EPIC-003 and planned in Sprint 3. Sub-tasks: US-008-T1 (text extraction and page-aware chunking), US-008-T2 (integrate gemini-embedding-001 to embed chunks, integration-agent), US-008-T3 (persist embeddings into pgvector-backed document_chunks table), US-008-T4 (status transitions and failure handling for parse/API errors). No ticket/commit status reported for the story or any of its sub-tasks.

**Related:** US-008, EPIC-003

- ⚠ Development run status is 'completed' but no ticket entry exists for US-008 or its sub-tasks (T1-T4); actual delivery status, including whether gemini-embedding-001 integration works, is unknown.

### DEV-US-009 · draft · source: plan:Sprint 4

Ask a question scoped to the active session's documents -- planned for Sprint 4 with four sub-tasks, no delivery ticket reported.

Story US-009 (8 points, backend-agent) is part of EPIC-004 and planned in Sprint 4. Sub-tasks: US-009-T1 (similarity search restricted to session's ready documents), US-009-T2 (integrate gemini-2.5-flash generation grounded in retrieved chunks, integration-agent), US-009-T3 (handle no-ready-documents and no-relevant-content cases without fabricating answers), US-009-T4 (graceful error handling for Gemini failures and missing API key). No ticket/commit status reported for the story or any of its sub-tasks.

**Related:** US-009, EPIC-004

- ⚠ Development run status is 'completed' but no ticket entry exists for US-009 or its sub-tasks (T1-T4); actual delivery status, including whether gemini-2.5-flash grounding works, is unknown.

### DEV-US-010 · draft · source: plan:Sprint 4

View source citations for each answer -- planned for Sprint 4, no delivery ticket reported.

Story US-010 (3 points, frontend-agent) is part of EPIC-004 and planned in Sprint 4. No ticket/commit status was included in the development run input for this story.

**Related:** US-010, EPIC-004

- ⚠ Development run status is 'completed' but no ticket entry exists for US-010 in the input; actual delivery status is unknown.

### DEV-US-011 · draft · source: plan:Sprint 4

Retain and view full session chat history -- planned for Sprint 4, no delivery ticket reported.

Story US-011 (3 points, backend-agent) is part of EPIC-005 and planned in Sprint 4. No ticket/commit status was included in the development run input for this story.

**Related:** US-011, EPIC-005

- ⚠ Development run status is 'completed' but no ticket entry exists for US-011 in the input; actual delivery status is unknown.
<!-- sdlc:auto:end narrative -->
