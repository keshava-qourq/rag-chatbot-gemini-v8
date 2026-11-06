# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-SPRINT-1 · approved · source: plan:Sprint 1

Sprint 1 goal: stand up authentication, per-user authorization, and session creation.

Capacity 20 points. Plan version 2, approved. Backlog items whose goals align with this sprint (explicit per-item sprint mapping not given in the plan input): EPIC-001 (User Accounts & Authentication), US-001 Sign up (3pts, backend-agent), US-002 Log in (3pts, backend-agent), US-003 Log out (2pts, backend-agent), US-004 Private isolated workspace (5pts, security-agent), US-005 Create a new chat session (2pts, backend-agent).

**Related:** EPIC-001, US-001, US-002, US-003, US-004, US-005

### DEV-SPRINT-2 · approved · source: plan:Sprint 2

Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs.

Capacity 20 points. Aligned backlog items (mapping inferred from goal, not explicit in input): EPIC-002 (Chat Session Management), US-006 View and switch between sessions (5pts, frontend-agent), EPIC-003 (PDF Upload & Processing), US-007 Upload a PDF to a chat session (8pts, backend-agent) with tasks US-007-T1 upload endpoint w/ validation, US-007-T2 store in S3 + persist metadata, US-007-T3 enqueue processing job, US-007-T4 document list endpoint w/ status (all backend-agent).

**Related:** EPIC-002, EPIC-003, US-006, US-007

### DEV-SPRINT-3 · approved · source: plan:Sprint 3

Sprint 3 goal: build the background pipeline that parses, chunks, and embeds PDFs into pgvector.

Capacity 20 points. Aligned backlog item: US-008 Parse, chunk, embed uploaded PDFs (13pts, backend-agent) with tasks US-008-T1 extraction/chunking in worker (backend-agent), US-008-T2 gemini-embedding-001 integration (integration-agent), US-008-T3 persist embeddings to pgvector (backend-agent), US-008-T4 status transitions/failure handling (backend-agent).

**Related:** EPIC-003, US-008

### DEV-SPRINT-4 · approved · source: plan:Sprint 4

Sprint 4 goal: deliver grounded QA with citations and full persistent chat history.

Capacity 20 points. Aligned backlog items: EPIC-004 (RAG QA), US-009 Ask a question scoped to session (8pts, backend-agent) with tasks US-009-T1 similarity search (backend-agent), US-009-T2 gemini-2.5-flash integration (integration-agent), US-009-T3 no-ready/no-relevant handling (backend-agent), US-009-T4 Gemini failure/missing-key handling (backend-agent); US-010 View source citations (3pts, frontend-agent); EPIC-005 (Chat History), US-011 Retain and view full session chat history (3pts, backend-agent).

**Related:** EPIC-004, EPIC-005, US-009, US-010, US-011

### DEV-US-012 · draft · source: plan:US-012

Wire Upload PDF form to the real upload endpoint (frontend-agent, 3pts).

Planned story, not explicitly mapped to one of the four numbered sprints in the plan input -- appears to be later corrective work beyond the original sprint scope. No delivery confirmation given in the development run input.

**Related:** EPIC-003, REQ-US-012

### DEV-US-013 · draft · source: plan:US-013

Show real backend errors for rejected uploads (frontend-agent, 2pts).

Planned story, not explicitly mapped to a numbered sprint in the plan input. No delivery confirmation given in the development run input.

**Related:** EPIC-003, REQ-US-013

### DEV-US-014 · draft · source: plan:US-014

Refresh Documents list to reflect real processing status (frontend-agent, 3pts).

Planned story, not explicitly mapped to a numbered sprint in the plan input. No delivery confirmation given in the development run input.

**Related:** EPIC-003, REQ-US-014

### DEV-US-015 · draft · source: plan:US-015

Run the RQ worker for the 'documents' queue alongside the API (devops-agent, 3pts).

Planned story, not explicitly mapped to a numbered sprint in the plan input. No delivery confirmation given in the development run input.

**Related:** EPIC-003, REQ-US-015

### DEV-US-016 · approved · source: dev:US-016

End-to-end verification that uploaded PDFs are processed and surfaced correctly (qa-agent, 2pts).

Development run status: completed. Ticket US-016 status=delivered, commit=3dea6f94ac2dd2ca528aaf6aa6729c6297c3a4bf.

**Related:** EPIC-003, REQ-US-016
<!-- sdlc:auto:end narrative -->
