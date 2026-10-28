# Sprint Plan

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start sprints -->
## Sprint 1: Sprint 1

Stand up authentication, per-user authorization, and the ability to create a chat session.

Capacity: 20 points · Committed: 15

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-001 | Story | Sign up with email and password | 3 | backend-agent | — |
| US-002 | Story | Log in with email and password | 3 | backend-agent | US-001 |
| US-003 | Story | Log out of the application | 2 | backend-agent | US-002 |
| US-004 | Story | Private, isolated workspace per user | 5 | security-agent | US-001, US-002 |
| US-005 | Story | Create a new chat session | 2 | backend-agent | US-004 |

## Sprint 2: Sprint 2

Enable browsing/switching sessions and uploading validated PDFs into a session.

Capacity: 20 points · Committed: 18

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-006 | Story | View and switch between my sessions | 5 | frontend-agent | US-005 |
| US-007 | Story | Upload a PDF to a chat session | 8 | backend-agent | US-004, US-005 |
| ↳ US-007-T1 | Task | Implement PDF upload endpoint with type/size/count validation | — | backend-agent | — |
| ↳ US-007-T2 | Task | Store accepted PDFs in S3 and persist document metadata | — | backend-agent | — |
| ↳ US-007-T3 | Task | Enqueue processing job on Redis queue after successful upload | — | backend-agent | — |
| ↳ US-007-T4 | Task | Implement document list endpoint with per-document status | — | backend-agent | — |
| US-012 | Story | Wire Upload PDF form to the real upload endpoint | 3 | frontend-agent | — |
| US-013 | Story | Show real backend errors for rejected uploads | 2 | frontend-agent | — |

## Sprint 3: Sprint 3

Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.

Capacity: 20 points · Committed: 19

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-008 | Story | Parse, chunk, and embed uploaded PDFs | 13 | backend-agent | US-007 |
| ↳ US-008-T1 | Task | Implement PDF text extraction and page-aware chunking in worker | — | backend-agent | — |
| ↳ US-008-T2 | Task | Integrate gemini-embedding-001 calls to embed chunks | — | integration-agent | — |
| ↳ US-008-T3 | Task | Persist chunk embeddings into pgvector-backed document_chunks table | — | backend-agent | — |
| ↳ US-008-T4 | Task | Implement status transitions and failure handling for parse/API errors | — | backend-agent | — |
| US-014 | Story | Refresh Documents list to reflect real processing status | 3 | frontend-agent | — |
| US-015 | Story | Run the RQ worker for the 'documents' queue alongside the API in the deployed container | 3 | devops-agent | — |

## Sprint 4: Sprint 4

Deliver grounded question answering with citations and full persistent chat history.

Capacity: 20 points · Committed: 16

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-009 | Story | Ask a question scoped to the active session's documents | 8 | backend-agent | US-008, US-004 |
| ↳ US-009-T1 | Task | Implement similarity search restricted to session's ready documents | — | backend-agent | — |
| ↳ US-009-T2 | Task | Integrate gemini-2.5-flash generation grounded in retrieved chunks | — | integration-agent | — |
| ↳ US-009-T3 | Task | Handle no-ready-documents and no-relevant-content cases without fabricating answers | — | backend-agent | — |
| ↳ US-009-T4 | Task | Implement graceful error handling for Gemini failures and missing API key | — | backend-agent | — |
| US-010 | Story | View source citations for each answer | 3 | frontend-agent | US-009 |
| US-011 | Story | Retain and view full session chat history | 3 | backend-agent | US-009 |
| US-016 | Story | End-to-end verification that uploaded PDFs are processed and surfaced correctly | 2 | qa-agent | — |

## Unscheduled

_Nothing unscheduled._
<!-- sdlc:auto:end sprints -->
