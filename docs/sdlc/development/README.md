# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-OVERVIEW · approved · source: plan:overview

Development plan approved at version 2, organized into 4 sprints of 20-point capacity each; the development run against this plan is reported complete.

Plan status: approved, version 2. Sprint goals: Sprint 1 -- stand up authentication, per-user authorization, and chat session creation; Sprint 2 -- enable browsing/switching sessions and uploading validated PDFs; Sprint 3 -- build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector; Sprint 4 -- deliver grounded question answering with citations and full persistent chat history. Development run status: completed.

### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 (capacity 20): stand up authentication, per-user authorization, and the ability to create a chat session.

Goal: Stand up authentication, per-user authorization, and the ability to create a chat session. Capacity: 20 points.

**Related:** EPIC-001, US-001, US-002, US-003, US-004, US-005

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 (capacity 20): enable browsing/switching sessions and uploading validated PDFs into a session.

Goal: Enable browsing/switching sessions and uploading validated PDFs into a session. Capacity: 20 points.

**Related:** EPIC-002, US-006, EPIC-003, US-007

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 (capacity 20): build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Goal: Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector. Capacity: 20 points.

**Related:** US-008

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 (capacity 20): deliver grounded question answering with citations and full persistent chat history.

Goal: Deliver grounded question answering with citations and full persistent chat history. Capacity: 20 points.

**Related:** EPIC-004, US-009, US-010, EPIC-005, US-011

### DEV-BACKLOG · approved · source: plan:backlog

Full backlog of epics, stories, and tasks with story points and assigned agent role.

EPIC-001 User Accounts & Authentication (unassigned): US-001 Sign up (3pt, backend-agent); US-002 Log in (3pt, backend-agent); US-003 Log out (2pt, backend-agent); US-004 Private isolated workspace (5pt, security-agent).
EPIC-002 Chat Session Management (unassigned): US-005 Create session (2pt, backend-agent); US-006 View/switch sessions (5pt, frontend-agent).
EPIC-003 PDF Upload & Processing (unassigned): US-007 Upload a PDF (8pt, backend-agent) with tasks T1 upload endpoint validation, T2 S3 storage+metadata, T3 enqueue Redis job, T4 document list endpoint (all backend-agent, unestimated); US-008 Parse/chunk/embed (13pt, backend-agent) with tasks T1 extraction/chunking (backend-agent), T2 gemini-embedding-001 integration (integration-agent), T3 persist embeddings to pgvector (backend-agent), T4 status transitions/failure handling (backend-agent); US-012 Wire upload form to real endpoint (3pt, frontend-agent); US-013 Show real backend upload errors (2pt, frontend-agent); US-014 Refresh documents list for real status (3pt, frontend-agent); US-015 Run RQ worker alongside API in deployed container (3pt, devops-agent); US-016 End-to-end upload verification (2pt, qa-agent).
EPIC-004 Retrieval-Augmented Question Answering (unassigned): US-009 Ask a scoped question (8pt, backend-agent) with tasks T1 similarity search (backend-agent), T2 gemini-2.5-flash integration (integration-agent), T3 no-ready/no-relevant handling (backend-agent), T4 Gemini error handling (backend-agent); US-010 View citations (3pt, frontend-agent).
EPIC-005 Chat History (unassigned): US-011 Retain/view full history (3pt, backend-agent).

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005, US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012, US-013, US-014, US-015, US-016

### DEV-TICKET-US-016 · approved · source: dev:US-016

End-to-end verification ticket for the upload-to-ready/failed pipeline was delivered.

Ticket US-016 (End-to-end verification that uploaded PDFs are processed and surfaced correctly): status=delivered, commit=3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf.

**Related:** US-016, US-015, US-014, US-013, US-012
<!-- sdlc:auto:end narrative -->
