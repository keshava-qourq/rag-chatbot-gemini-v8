# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-SPRINT-1 · approved · source: development:plan Sprint 1

Sprint 1 goal: stand up authentication, per-user authorization, and chat session creation.

Capacity: 20 points. Plan version 2, status approved.

**Related:** EPIC-001

### DEV-SPRINT-2 · approved · source: development:plan Sprint 2

Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session.

Capacity: 20 points. Plan version 2, status approved.

**Related:** EPIC-002, EPIC-003

### DEV-SPRINT-3 · approved · source: development:plan Sprint 3

Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Capacity: 20 points. Plan version 2, status approved.

**Related:** EPIC-003

### DEV-SPRINT-4 · approved · source: development:plan Sprint 4

Sprint 4 goal: deliver grounded question answering with citations and full persistent chat history.

Capacity: 20 points. Plan version 2, status approved.

**Related:** EPIC-004, EPIC-005

### DEV-BACKLOG-001 · approved · source: development:plan backlog

Full backlog of epics, stories, and tasks with points and assigned agent roles (plan v2, approved); per-item sprint assignment was not specified in the plan input.

- EPIC-001 User Accounts & Authentication (unassigned): US-001 Sign up (3, backend-agent); US-002 Log in (3, backend-agent); US-003 Log out (2, backend-agent); US-004 Private isolated workspace (5, security-agent).
- EPIC-002 Chat Session Management (unassigned): US-005 Create session (2, backend-agent); US-006 View/switch sessions (5, frontend-agent).
- EPIC-003 PDF Upload & Processing (unassigned): US-007 Upload PDF (8, backend-agent) with tasks T1 upload endpoint validation, T2 S3 storage + metadata, T3 enqueue Redis job, T4 document list endpoint; US-008 Parse/chunk/embed (13, backend-agent) with tasks T1 extraction/chunking, T2 gemini-embedding-001 integration (integration-agent), T3 persist to pgvector, T4 status/failure handling; US-012 Wire upload form to real endpoint (3, frontend-agent); US-013 Show real backend upload errors (2, frontend-agent); US-014 Refresh documents list with real status (3, frontend-agent); US-015 Run RQ worker alongside API in container (3, devops-agent); US-016 End-to-end upload verification (2, qa-agent).
- EPIC-004 Retrieval-Augmented QA (unassigned): US-009 Ask scoped question (8, backend-agent) with tasks T1 similarity search, T2 gemini-2.5-flash integration (integration-agent), T3 no-ready/no-relevant handling, T4 Gemini error handling; US-010 View citations (3, frontend-agent).
- EPIC-005 Chat History (unassigned): US-011 Retain/view full chat history (3, backend-agent).

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012, US-013, US-014, US-015, US-016

### DEV-TICKET-US-016 · approved · source: dev:TICKET US-016

End-to-end verification that uploaded PDFs are processed and surfaced correctly -- delivered.

Ticket US-016 status: delivered. Commit: 3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf.

**Related:** US-016, EPIC-003

### DEV-RUN-001 · approved · source: development:run

Overall development run status: completed.

The development run for this plan version is marked completed. Only one ticket (US-016) was itemized in the input, with status delivered; no per-ticket detail was provided for the remaining backlog items.

**Related:** US-016
<!-- sdlc:auto:end narrative -->
