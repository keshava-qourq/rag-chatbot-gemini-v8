# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-001 · approved · source: plan:v1

Development plan version 1 was approved, organizing work into 4 sprints (capacity 20 each) across 5 epics: Auth, Session Management, PDF Upload & Processing, RAG QA, and Chat History.

Sprint 1 goal: stand up authentication, per-user authorization, and session creation (covers EPIC-001 User Accounts & Authentication: US-001 Sign up [3pt, backend-agent], US-002 Log in [3pt, backend-agent], US-003 Log out [2pt, backend-agent], US-004 Private isolated workspace per user [5pt, security-agent]). Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session (covers EPIC-002 Chat Session Management: US-005 Create new chat session [2pt, backend-agent], US-006 View/switch sessions [5pt, frontend-agent]; and part of EPIC-003: US-007 Upload a PDF [8pt, backend-agent] with tasks US-007-T1 upload endpoint validation, US-007-T2 S3 storage + metadata, US-007-T3 enqueue Redis processing job, US-007-T4 document list endpoint with status). Sprint 3 goal: build the background pipeline that parses, chunks, and embeds PDFs into pgvector (US-008 Parse/chunk/embed [13pt, backend-agent] with tasks US-008-T1 extraction/chunking, US-008-T2 gemini-embedding-001 integration [integration-agent], US-008-T3 persist to pgvector document_chunks table, US-008-T4 status transitions/failure handling). Sprint 4 goal: deliver grounded QA with citations and full persistent chat history (EPIC-004 Retrieval-Augmented QA: US-009 Ask a question scoped to session [8pt, backend-agent] with tasks US-009-T1 similarity search, US-009-T2 gemini-2.5-flash integration [integration-agent], US-009-T3 handling no-ready/no-relevant cases, US-009-T4 Gemini failure/missing-key handling; US-010 View source citations [3pt, frontend-agent]; and EPIC-005 Chat History: US-011 Retain/view full chat history [3pt, backend-agent]).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ Epics (EPIC-001 through EPIC-005) have no assigned role/owner recorded in the plan.
- ⚠ Plan does not state who approved version 1 or on what date.

### DEV-US-009 · approved · source: dev:US-009

Ticket US-009 (Ask a question scoped to the active session's documents) is recorded as delivered, implementing similarity search restricted to the session's ready documents, gemini-2.5-flash grounded generation, safe handling of no-ready-document/no-relevant-content cases, and graceful handling of Gemini failures or a missing API key.

Delivered via commit 0886b2162d958978b854135663937aadf5774199. Scope per plan tasks: US-009-T1 similarity search restricted to session's ready documents; US-009-T2 integration of gemini-2.5-flash generation grounded in retrieved chunks; US-009-T3 handling of no-ready-documents and no-relevant-content cases without fabricating answers; US-009-T4 graceful error handling for Gemini failures and missing API key.

**Related:** US-009, US-009-T1, US-009-T2, US-009-T3, US-009-T4

- ⚠ The commit hash recorded for US-009 (0886b2162d958978b854135663937aadf5774199) is identical to the commit hash recorded for US-011 -- flagged as a possible data discrepancy since they are different tickets.
- ⚠ No per-task (T1-T4) delivery confirmation was provided, only story-level status.

### DEV-US-010 · approved · source: dev:US-010

Ticket US-010 (View source citations for each answer) is recorded as delivered.

Delivered via commit 415b05be93a78ebf614d1f184a3271e7ede83bad. Per the plan, this story belongs to EPIC-004 Retrieval-Augmented Question Answering, role frontend-agent, 3 points. No further implementation detail was provided beyond delivery status.

**Related:** US-010

- ⚠ No implementation detail (e.g. which UI elements display citations) was provided beyond the delivered status and commit.

### DEV-US-011 · approved · source: dev:US-011

Ticket US-011 (Retain and view full session chat history) is recorded as delivered.

Delivered via commit 0886b2162d958978b854135663937aadf5774199, under EPIC-005 Chat History, role backend-agent, 3 points. No further implementation detail was provided beyond delivery status.

**Related:** US-011

- ⚠ The commit hash recorded for US-011 is identical to the one recorded for US-009 -- flagged as a possible data discrepancy since they are different tickets and this may indicate a reporting error or a combined commit covering both.

### DEV-PENDING-001 · draft · source: plan:v1

Eight stories spanning authentication, session management, and PDF upload/processing/embedding are defined in the approved plan but have no corresponding ticket delivery record in the development run output.

Planned scope per sprints 1-3: US-001 Sign up (3pt), US-002 Log in (3pt), US-003 Log out (2pt), US-004 Private isolated workspace (5pt, security-agent); US-005 Create chat session (2pt), US-006 View/switch sessions (5pt, frontend-agent); US-007 Upload a PDF (8pt) with tasks for upload validation, S3 storage/metadata, Redis enqueue, and document list endpoint; US-008 Parse/chunk/embed (13pt) with tasks for extraction/chunking, gemini-embedding-001 integration, pgvector persistence, and status/failure handling. None of these appear in the development run's ticket status list.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008

- ⚠ Development run status is reported as 'completed', but only 3 of 11 planned stories (US-009, US-010, US-011) have ticket delivery records -- status for US-001 through US-008 is unknown/unreported, which is inconsistent with a 'completed' run.
- ⚠ Cannot confirm whether these 8 stories were built, partially built, or not started.
<!-- sdlc:auto:end narrative -->
