# Development

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEV-PLAN-001 · approved · source: plan:v1

Development plan version 1 was approved, organizing the project into 4 sprints of capacity 20 each, covering 5 epics and 11 user stories with detailed sub-tasks for the PDF processing and RAG QA epics.

Sprint 1 goal: stand up authentication, per-user authorization, and chat session creation (items: EPIC-001, US-001 Sign up, US-002 Log in, US-003 Log out, US-004 Private isolated workspace). Sprint 2 goal: enable browsing/switching sessions and uploading validated PDFs into a session (items: EPIC-002, US-005 Create chat session, US-006 View/switch sessions, EPIC-003, US-007 Upload PDF with sub-tasks US-007-T1 upload endpoint with type/size/count validation, US-007-T2 store PDFs in S3 and persist metadata, US-007-T3 enqueue Redis processing job, US-007-T4 document list endpoint with per-document status). Sprint 3 goal: build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector (item: US-008 with sub-tasks US-008-T1 text extraction/page-aware chunking, US-008-T2 gemini-embedding-001 integration, US-008-T3 persist embeddings into pgvector document_chunks table, US-008-T4 status transitions/failure handling). Sprint 4 goal: deliver grounded QA with citations and full persistent chat history (items: EPIC-004, US-009 Ask question scoped to session documents with sub-tasks US-009-T1 similarity search restricted to ready documents, US-009-T2 gemini-2.5-flash grounded generation, US-009-T3 handle no-ready-documents/no-relevant-content without fabrication, US-009-T4 graceful error handling for Gemini failures/missing API key; US-010 View source citations; EPIC-005, US-011 Retain/view full session chat history). Points: US-001=3, US-002=3, US-003=2, US-004=5, US-005=2, US-006=5, US-007=8, US-008=13, US-009=8, US-010=3, US-011=3.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ Epics (EPIC-001 through EPIC-005) have no assigned role/owner recorded.
- ⚠ Plan does not state who approved version 1 or when.

### DEV-US-009 · draft · source: dev:US-009

The ticket for 'Ask a question scoped to the active session's documents' was marked skipped in the development run, with no associated commit.

Development run status lists US-009 status=skipped, commit=(none). No reason for skipping was provided. Sub-tasks US-009-T1 through US-009-T4 defined in the plan (similarity search, gemini-2.5-flash integration, no-content handling, error handling) have no individual status reported.

**Related:** US-009, US-009-T1, US-009-T2, US-009-T3, US-009-T4

- ⚠ Reason the ticket was skipped is not stated.
- ⚠ No commit exists for this ticket, so it is unclear whether any of US-009-T1–T4 were implemented.
- ⚠ Status of sub-tasks US-009-T1 through US-009-T4 not individually reported.

### DEV-US-010 · draft · source: dev:US-010

The ticket for 'View source citations for each answer' was marked skipped in the development run, with no associated commit.

Development run status lists US-010 status=skipped, commit=(none). No reason for skipping was provided. This story depends functionally on US-009 (grounded QA), which was also skipped.

**Related:** US-010, US-009

- ⚠ Reason the ticket was skipped is not stated.
- ⚠ No commit exists for this ticket.
- ⚠ Dependency on US-009 (also skipped) suggests citations feature cannot function without the underlying QA pipeline; this blocking relationship is not explicitly confirmed by the input.

### DEV-US-011 · draft · source: dev:US-011

The ticket for 'Retain and view full session chat history' was marked skipped in the development run, with no associated commit.

Development run status lists US-011 status=skipped, commit=(none). No reason for skipping was provided.

**Related:** US-011

- ⚠ Reason the ticket was skipped is not stated.
- ⚠ No commit exists for this ticket, so chat history persistence/view functionality cannot be confirmed as built.

### DEV-RUN-SUMMARY · draft · source: dev:run-status

The development run is marked 'completed' overall, but its ticket list only accounts for 3 of the 11 planned stories (US-009, US-010, US-011), all of which are skipped with no commits.

Development run status field reads 'completed', yet the only tickets reported are US-009, US-010, and US-011, each with status=skipped and commit=(none). No tickets are listed for US-001 (Sign up), US-002 (Log in), US-003 (Log out), US-004 (Private workspace), US-005 (Create session), US-006 (View/switch sessions), US-007 (Upload PDF, incl. sub-tasks T1-T4), or US-008 (Parse/chunk/embed PDFs, incl. sub-tasks T1-T4).

**Related:** US-009, US-010, US-011

- ⚠ Discrepancy: run status says 'completed' but all reported tickets are 'skipped' with no commits -- unclear what 'completed' refers to.
- ⚠ No development status recorded for US-001 through US-008 or their sub-tasks (US-007-T1–T4, US-008-T1–T4) in this phase input; it is unknown whether they were implemented, are pending, or were omitted from this report.
- ⚠ No commits are recorded anywhere in this development run, so no code artifacts can be traced to any requirement.
<!-- sdlc:auto:end narrative -->
