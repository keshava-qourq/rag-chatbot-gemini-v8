# Planning

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### EPIC-001 · approved · source: planning:EPIC-001

Enables individual users to create and access their own account via email/password (no SSO), with all other data partitioned by authenticated user identity.

Goal: ensure one user can never see or affect another user's workspace (sessions, documents, chat history). Stories: US-001, US-002, US-003, US-004.

**Related:** US-001, US-002, US-003, US-004

### EPIC-002 · approved · source: planning:EPIC-002

Allows a logged-in user to create and maintain multiple independent chat sessions, each a container for its own attached documents and conversation thread.

Goal: support multiple independent, resumable conversations per user. Stories: US-005, US-006.

**Related:** US-005, US-006

### EPIC-003 · approved · source: planning:EPIC-003

Lets users attach one or more PDF files to a chat session; files are validated, parsed, chunked, and embedded via gemini-embedding-001 into a pgvector-backed store. PDF is the only supported format.

Goal: deliver a working end-to-end PDF ingestion pipeline. Includes original upload/processing stories (US-007, US-008) plus later stories (US-012-US-016) added to wire the upload form to the real backend endpoint, surface real backend errors, refresh document status, run the RQ worker in the deployed container, and perform end-to-end QA verification of the previously broken upload-to-ready/failed flow.

**Related:** US-007, US-008, US-012, US-013, US-014, US-015, US-016

### EPIC-004 · approved · source: planning:EPIC-004

Lets users ask natural-language questions within a session; the system retrieves relevant chunks from only that session's ready PDFs and generates an answer via gemini-2.5-flash, with citations.

Goal: grounded, session-scoped question answering with source traceability. Stories: US-009, US-010.

**Related:** US-009, US-010

### EPIC-005 · approved · source: planning:EPIC-005

Persists the full conversation (questions, answers, citations) for every session so users can review past exchanges at any time they return.

Goal: durable, session-scoped chat history retrieval. Story: US-011.

**Related:** US-011

### SPRINT-1 · draft · source: planning:SPRINT-1

First sprint of plan v5, capacity 20, focused on authentication, authorization, and basic session creation.

Goal: 'Stand up authentication, per-user authorization, and the ability to create a chat session.' Capacity: 20. Goal wording maps to EPIC-001 stories (sign up, log in, log out, private workspace) and EPIC-002's create-session story (US-005); exact point/role assignment to this sprint is not specified in the input.

**Related:** US-001, US-002, US-003, US-004, US-005

### SPRINT-2 · draft · source: planning:SPRINT-2

Second sprint of plan v5, capacity 20, focused on session browsing/switching and validated PDF upload.

Goal: 'Enable browsing/switching sessions and uploading validated PDFs into a session.' Capacity: 20. Goal wording maps to US-006 (view/switch sessions) and US-007 (upload a PDF); exact point/role assignment to this sprint is not specified in the input.

**Related:** US-006, US-007

### SPRINT-3 · draft · source: planning:SPRINT-3

Third sprint of plan v5, capacity 20, focused on the background PDF parse/chunk/embed pipeline into pgvector.

Goal: 'Build the background pipeline that parses, chunks, and embeds uploaded PDFs into pgvector.' Capacity: 20. Goal wording maps to US-008; exact point/role assignment to this sprint is not specified in the input.

**Related:** US-008

### SPRINT-4 · draft · source: planning:SPRINT-4

Fourth sprint of plan v5, capacity 20, focused on grounded QA with citations and persistent chat history.

Goal: 'Deliver grounded question answering with citations and full persistent chat history.' Capacity: 20. Goal wording maps to US-009 (ask a question), US-010 (citations), and US-011 (chat history); exact point/role assignment to this sprint is not specified in the input.

**Related:** US-009, US-010, US-011
<!-- sdlc:auto:end narrative -->
