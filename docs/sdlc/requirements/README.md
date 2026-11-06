# Product Requirements

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Summary

### REQ-STACK · approved · source: requirements:stack

Product owner approved a fixed technology stack and service set for this lightweight RAG chatbot; design/build must use exactly these, no substitutions.

Stack (v2): Backend FastAPI 0.115 (async handles concurrent Gemini calls without blocking uploads); Cloud AWS (storage, compute, DB in one place, room to grow); Database PostgreSQL 16 with pgvector (relational data and embeddings transactionally consistent in one system); Frontend React 19 (stateful chat UI: sidebar, streaming window, citation popovers). Services: AI provider Google Gemini (SaaS, env GEMINI_API_KEY) for gemini-2.5-flash chat and gemini-embedding-001 embeddings; Vector store pgvector in Postgres for per-session similarity search; File storage Amazon S3 (env AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET) for original PDFs up to ~20MB; Queue Redis (container redis:7-alpine) to keep PDF processing off the upload request thread. Required API keys/env vars: AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, GEMINI_API_KEY, REDIS_URL, S3_BUCKET.

### REQ-SCOPE · approved · source: requirements:scope

Delivery scope is lightweight (requirements v2). In-scope: individual accounts, private workspace, multi-session chat with per-session PDFs, parsing/chunking/embedding, session-scoped grounded QA with citations, persistent chat history, email/password-only auth, free usage.

In scope: user sign-up/login (email/password, no SSO); private per-user workspace for documents/sessions/history; chat session creation; PDF upload attached to a session; PDF parsing, chunking, embedding; question answering scoped to the active session's PDFs; answers with citations to PDF+page/section; full per-session chat history; multiple sessions per user; Gemini gemini-2.5-flash for answers and gemini-embedding-001 for embeddings; Postgres+pgvector for embeddings and relational data; ~20MB per-PDF limit with a per-session document count cap; free, no billing. Out of scope: non-PDF formats (Word, text, markdown, images, etc.); cross-document/cross-session querying (queries are strictly scoped to the active session's attached documents); email/SMTP functionality (removed from stack).

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

### REQ-EPIC-001 · approved · source: requirements:EPIC-001

User Accounts & Authentication: individual email/password accounts with strict per-user data isolation across sessions, documents, and chat history.

US-001 (critical) Sign up with email/password: valid unused email + password meeting complexity rules creates an account (password hashed) and signs the user in (AC-001); duplicate email is rejected with an 'account already exists' message, no duplicate created (AC-002); weak password is rejected with requirements explained, no account created (AC-003).
US-002 (critical) Log in: correct credentials authenticate and issue a session/token, redirecting to workspace (AC-004); wrong password or unknown email returns a generic invalid-credentials message without confirming which was wrong (AC-005); expired/invalidated session forces redirect to login (AC-006).
US-003 (medium) Log out: logging out invalidates the session/token; subsequent protected requests require re-login (AC-007).
US-004 (critical) Private isolated workspace: listing sessions/documents/history via UI or API returns only the authenticated user's own records (AC-008); direct access to another user's session/document/message by ID is denied with an authorization error, not the data (AC-009).

**Related:** US-001, US-002, US-003, US-004

### REQ-EPIC-002 · approved · source: requirements:EPIC-002

Chat Session Management: users can create and switch between multiple independent sessions, each with its own documents and conversation thread.

US-005 (critical) Create a new session: confirming creation (optionally naming it) creates a new, empty session owned by the user with no documents or messages yet (AC-010).
US-006 (high) View and switch sessions: the sessions list shows only the user's own sessions by name/date, never other users' sessions (AC-011); opening a session shows only that session's documents and message history, independent of other sessions (AC-012).

**Related:** US-005, US-006

### REQ-EPIC-003 · approved · source: requirements:EPIC-003

PDF Upload & Processing: PDFs are validated, stored, queued, then parsed/chunked/embedded via gemini-embedding-001 into pgvector; this epic also covers the real-backend wiring and worker-run fixes needed to make the pipeline actually function end to end.

US-007 (critical) Upload a PDF: valid PDF within size limit is accepted, tied to the session, and queued (AC-013); non-PDF files are rejected with a PDF-only message, nothing stored (AC-014); oversized PDFs (~20MB limit) are rejected with a size-limit message, nothing stored (AC-015); exceeding the per-session document cap rejects the new upload with a limit-reached message (AC-016).
US-008 (critical) Parse/chunk/embed: accepted PDFs are extracted, chunked with page-level position retained, embedded via gemini-embedding-001, and stored in pgvector linked to the document/session (AC-017); while processing, document shows 'processing' and is unusable for QA (AC-018); on success it is marked 'ready' with chunks available (AC-019); unparseable/scanned image-only PDFs (no OCR support) are marked 'failed' with an explanatory message and excluded from retrieval until re-uploaded (AC-020); missing/invalid GEMINI_API_KEY causes graceful failure, 'failed' status with a configuration error, and logging (AC-021).
US-012 (critical) Wire Upload PDF form to real endpoint: apiFetch must send a multipart request with the user's token to POST /sessions/{session_id}/documents instead of simulating locally (AC-031); on acceptance, the new document must appear in the list as 'processing' sourced from the real backend response (AC-032).
US-013 (high) Show real backend errors: rejection reasons (non-PDF, oversized, over-cap) must display the exact backend message without adding a document (AC-033); network/auth failures must show a clear error state, not a false success (AC-034).
US-014 (critical) Refresh Documents list: the list must poll/refresh GET /sessions/{session_id}/documents until 'ready' or 'failed' (AC-035); successful completion updates to 'ready' without a full reload (AC-036); failure updates to 'failed' showing the backend's error_message (AC-037).
US-015 (critical) Run RQ worker alongside API: container entrypoint must run both uvicorn and an RQ worker on the 'documents' queue concurrently (AC-038); enqueued jobs must be picked up and processed without manual intervention (AC-039); a crash in either process must be visible in logs/exit status, not silently swallowed (AC-040).
US-016 (high) End-to-end verification: with the worker fix applied, a valid PDF must go 'processing' -> 'ready' with chunks usable for QA in a reasonable time (AC-041); corrupted/scanned PDFs must reach 'failed' with an explanatory UI error (AC-042); non-PDF/oversized/over-cap uploads must show the backend's exact rejection message with no document record created (AC-043).

**Related:** US-007, US-008, US-012, US-013, US-014, US-015, US-016

### REQ-EPIC-004 · approved · source: requirements:EPIC-004

Retrieval-Augmented Question Answering: questions are answered strictly from the active session's ready documents via similarity search and gemini-2.5-flash, with citations.

US-009 (critical) Ask a scoped question: with ready PDFs present, the question is embedded, relevant chunks retrieved via similarity search restricted to the session's documents, and an answer generated via gemini-2.5-flash using those chunks (AC-022); chunks from other sessions, even the same user's, are never retrieved or referenced (AC-023); if no documents are attached or none are ready, the system states no ready documents are available rather than calling the model with empty context (AC-024); if retrieved chunks are irrelevant, the answer states it could not be found in the attached documents rather than fabricating one (AC-025); missing/invalid GEMINI_API_KEY or a failed/timed-out Gemini call shows a clear error and does not record a fabricated answer (AC-026).
US-010 (high) View citations: each answer includes a citation per source chunk identifying the source PDF and, where extractable, page/section (AC-027); if page-level position wasn't preserved, the citation still names the source document rather than being omitted (AC-028).

**Related:** US-009, US-010

### REQ-EPIC-005 · approved · source: requirements:EPIC-005

Chat History: full per-session conversation history, including citations, is retained and viewable at any time.

US-011 (high) Retain/view full history: every prior question and its answer (with citations) is shown in chronological order on reopening a session, including after logging out and back in (AC-029); viewing one session's history never shows messages from another session (AC-030).

**Related:** US-011
<!-- sdlc:auto:end narrative -->

<!-- sdlc:auto:start summary -->
**Requirements version:** v2  
**Delivery scope:** lightweight  
**Approved:** 2026-10-28

**Capabilities in scope:** User sign-up and login with individual accounts, Private per-user workspace for documents, sessions, and chat history, Chat session creation, PDF upload attached to a chat session, PDF parsing, chunking, and embedding of uploaded documents, Question answering scoped to PDFs attached to the active session, Answers with citations back to source PDF and page/section, Full chat history retained per session, Multiple sessions per user, each with its own documents and thread, Email/password login, no SSO, Gemini gemini-2.5-flash for answers, gemini-embedding-001 for embeddings, PostgreSQL with pgvector for embeddings plus relational data, ~20MB per-PDF upload limit with a per-session document count cap, Free to use, no billing or payment functionality

**Approved technology stack:**

| Layer | Choice | Rationale |
|---|---|---|
| backend | FastAPI | The core of this product is PDF parsing, chunking, calling Gemini for embeddings and chat, and orchestrating retrieval -- all things Python's ecosystem (PDF libraries, Google's Gemini SDK) handles well. FastAPI's async support matters here because every user request to the Gemini API is a network call, and you don't want one user's generation request blocking another's upload processing. |
| cloud | AWS | AWS gives you everything this app needs in one place: object storage for the uploaded PDFs, a straightforward place to run the FastAPI backend and Postgres, and room to grow if usage increases beyond the 'tens to low hundreds of users' you described, without needing to re-platform. |
| database | PostgreSQL | You need relational storage for users, sessions, documents and chat history, plus a place to store and search embeddings -- and your own assumptions already point to Postgres with pgvector so both live in one system. That keeps a user's account data, their session-document links, and their embeddings transactionally consistent without standing up a separate vector database. |
| frontend | React | You need a responsive chat interface where users manage multiple sessions, attach PDFs per session, watch answers stream in, and click through to citations with page numbers. That's inherently a stateful, interactive single-page app, and React is the natural fit for building the chat window, document sidebar, and citation popovers as reusable components. |
<!-- sdlc:auto:end summary -->

<!-- sdlc:auto:start epics -->
## EPIC-001: User Accounts & Authentication

Enables individual users to create and access their own account using email/password credentials, with no SSO. All other data (sessions, documents, chat history) is partitioned by the authenticated user's identity so that one user can never see or affect another user's workspace.

### US-001: Sign up with email and password

**Priority:** critical

> As a new visitor, I want to create an account using my email address and a password, so that I can have my own private workspace in the application.

| ID | Given | When | Then |
|---|---|---|---|
| AC-001 | a visitor on the sign-up page enters a valid, unused email address and a password meeting minimum complexity rules | they submit the sign-up form | a new account is created, the password is stored only in hashed form, and the user is signed in |
| AC-002 | a visitor enters an email address that already has an account | they submit the sign-up form | the system rejects the submission with a clear 'account already exists' message and no duplicate account is created |
| AC-003 | a visitor enters a password that does not meet the minimum complexity rules | they submit the sign-up form | the system rejects the submission and explains the password requirements without creating an account |

### US-002: Log in with email and password

**Priority:** critical

> As a registered user, I want to log in with my email and password, so that I can access my private sessions, documents, and chat history.

| ID | Given | When | Then |
|---|---|---|---|
| AC-004 | a registered user enters the correct email and password | they submit the login form | they are authenticated and redirected to their workspace with a valid session/token issued |
| AC-005 | a user enters an incorrect password or an email with no matching account | they submit the login form | the system denies access with a generic invalid-credentials message, without revealing whether the email exists |
| AC-006 | an authenticated user's session/token has expired or been invalidated | they attempt to access a protected page or API | they are redirected to the login page and must re-authenticate |

### US-003: Log out of the application

**Priority:** medium

> As a logged-in user, I want to log out of my account, so that my session is closed and no one else can use my workspace on this device.

| ID | Given | When | Then |
|---|---|---|---|
| AC-007 | a user is logged in | they choose to log out | their session/token is invalidated and subsequent requests to protected pages require login again |

### US-004: Private, isolated workspace per user

**Priority:** critical

> As a logged-in user, I want my documents, chat sessions, and message history to be visible only to me, so that my data stays private from every other user of the application.

| ID | Given | When | Then |
|---|---|---|---|
| AC-008 | two distinct users each have their own sessions and uploaded documents | either user lists their sessions, documents, or chat history via the UI or API | only records owned by the authenticated user are returned; the other user's data is never included |
| AC-009 | a user attempts to access a session, document, or message by ID that belongs to another user | the request is made directly (e.g. via URL or API call) | the system denies access with an authorization error rather than returning the data |

## EPIC-002: Chat Session Management

Allows a logged-in user to create and maintain multiple independent chat sessions, each acting as a container for its own set of attached PDF documents and its own conversation thread.

### US-005: Create a new chat session

**Priority:** critical

> As a logged-in user, I want to create a new chat session, so that I can start a fresh conversation scoped to a new set of documents.

| ID | Given | When | Then |
|---|---|---|---|
| AC-010 | a logged-in user chooses to start a new session | they confirm creation (optionally naming it) | a new, empty session owned by that user is created with no documents attached and no messages yet |

### US-006: View and switch between my sessions

**Priority:** high

> As a logged-in user, I want to see a list of all my chat sessions and open any one of them, so that I can manage and resume multiple independent conversations, each with its own documents and thread.

| ID | Given | When | Then |
|---|---|---|---|
| AC-011 | a user has created multiple sessions, each with different attached documents | they view their sessions list | all of their sessions are shown (e.g. by name/date) and none belonging to other users appear |
| AC-012 | a user selects one of their sessions from the list | the session opens | only that session's attached documents and message history are displayed, independent of any other session |

## EPIC-003: PDF Upload & Processing

Lets users attach one or more PDF files to a chat session; uploaded files are validated, parsed into text, split into chunks, and embedded using gemini-embedding-001, with embeddings stored in a pgvector-backed PostgreSQL store for later retrieval. PDF is the only supported format in this version.

### US-007: Upload a PDF to a chat session

**Priority:** critical

> As a logged-in user, I want to attach one or more PDF files to a chat session, so that I can ask questions about their content within that session.

| ID | Given | When | Then |
|---|---|---|---|
| AC-013 | a user has an open session and selects a valid PDF file within the size limit | they upload it | the file is accepted, associated with that session only, and queued for processing |
| AC-014 | a user attempts to upload a non-PDF file (e.g. Word, text, image) | they submit the upload | the system rejects the file with a message stating only PDF files are supported, and nothing is stored |
| AC-015 | a user attempts to upload a PDF larger than the configured per-file size limit (~20MB) | they submit the upload | the system rejects the file with a clear message stating the size limit, and nothing is stored |
| AC-016 | a session already has the maximum allowed number of attached documents (per-session cap) | the user attempts to attach another PDF | the system rejects the new upload with a message explaining the per-session document limit has been reached |

### US-008: Parse, chunk, and embed uploaded PDFs

**Priority:** critical

> As a logged-in user, I want my uploaded PDF to be automatically parsed into text, split into chunks, and embedded, so that its content becomes searchable for question answering in that session.

| ID | Given | When | Then |
|---|---|---|---|
| AC-017 | a PDF has been successfully uploaded and accepted | the processing pipeline runs | its text is extracted, split into chunks retaining page-level position information, embedded via gemini-embedding-001, and the embeddings are stored in the pgvector-backed store linked to that document and session |
| AC-018 | a document is still being processed | the user views the session's document list | the document shows a 'processing' status and is not yet usable for question answering |
| AC-019 | processing completes successfully | the user views the document list | the document is marked 'ready' and its chunks are available for retrieval |
| AC-020 | a PDF fails to parse (e.g. corrupted file, or a scanned/image-only PDF with no extractable text, since OCR is not supported in this version) | the processing pipeline runs | the document is marked 'failed' with an explanatory message, and it is excluded from retrieval until a valid PDF is re-uploaded |
| AC-021 | the GEMINI_API_KEY is missing or invalid | the system attempts to generate embeddings for a document | processing fails gracefully, the document is marked 'failed' with a configuration-related error, and the failure is logged |

### US-012: Wire Upload PDF form to the real upload endpoint

**Priority:** critical

> As a logged-in user, I want my PDF upload to actually be sent to the backend when I submit the Upload PDF form, so that my document is really stored and queued for processing instead of only appearing to upload.

| ID | Given | When | Then |
|---|---|---|---|
| AC-031 | a user on an open session selects a valid PDF and submits the Upload PDF form | the form is submitted | apiFetch sends a multipart request with the user's token to POST /sessions/{session_id}/documents instead of simulating the upload locally |
| AC-032 | the backend accepts the upload | the response is received | the new document appears in the session's Documents list with status 'processing' sourced from the backend response, not a client-only placeholder |

### US-013: Show real backend errors for rejected uploads

**Priority:** high

> As a logged-in user, I want to see the backend's actual rejection reason when my PDF upload is refused, so that I understand why a non-PDF file, an oversized file, or a file over the session's document cap was not accepted.

| ID | Given | When | Then |
|---|---|---|---|
| AC-033 | a user submits a non-PDF file, an oversized PDF, or a file when the session is at its document cap | POST /sessions/{session_id}/documents responds with a rejection | the form displays the exact backend error message and does not add a document to the list |
| AC-034 | the backend call fails due to a network or auth error | the request fails | the form shows a clear error state instead of silently succeeding or leaving the form in a simulated 'uploaded' state |

### US-014: Refresh Documents list to reflect real processing status

**Priority:** critical

> As a logged-in user, I want the Documents list to refresh and reflect each document's true backend status, so that I can see a document move from 'processing' to 'ready', or see its 'failed' error, without it being stuck on a fake status.

| ID | Given | When | Then |
|---|---|---|---|
| AC-035 | a document was just uploaded and is 'processing' | the session screen is open | the Documents list polls or refreshes GET /sessions/{session_id}/documents periodically until the document reaches 'ready' or 'failed' |
| AC-036 | a document's processing completes successfully | the list refreshes | the document's displayed status updates to 'ready' without requiring a full page reload |
| AC-037 | a document's processing fails | the list refreshes | the document's displayed status updates to 'failed' and shows the backend's error_message |

### US-015: Run the RQ worker for the 'documents' queue alongside the API in the deployed container

**Priority:** critical

> As a operator of the deployed application, I want the RQ worker for the Redis 'documents' queue to actually start and run when the container starts, so that queued PDF processing jobs are consumed and documents stop being stuck in 'processing' forever.

| ID | Given | When | Then |
|---|---|---|---|
| AC-038 | the application container starts | the container's entrypoint/CMD runs | both uvicorn (the API) and an RQ worker consuming the 'documents' queue are running concurrently in the container |
| AC-039 | a document is uploaded and a job is enqueued on the Redis 'documents' queue | the worker process is running | the job is picked up and processed without manual intervention |
| AC-040 | either the API process or the worker process crashes | the container is inspected | the failure is visible in container logs/exit status rather than being silently swallowed by the other process |

### US-016: End-to-end verification that uploaded PDFs are processed and surfaced correctly

**Priority:** high

> As a QA engineer, I want to verify the full upload-to-ready/failed flow works against the real backend and worker, so that we have confidence the previously broken end-to-end path now functions as the delivered stories require.

| ID | Given | When | Then |
|---|---|---|---|
| AC-041 | a running deployment with the worker fix applied | a valid PDF is uploaded via the UI | the document transitions from 'processing' to 'ready' within a reasonable time and its chunks become available for question answering |
| AC-042 | a running deployment with the worker fix applied | a corrupted or scanned image-only PDF is uploaded | the document transitions to 'failed' with an explanatory error shown in the UI |
| AC-043 | a running deployment | a non-PDF, oversized, or over-cap upload is attempted | the UI shows the backend's exact rejection message and no document record is created |

## EPIC-004: Retrieval-Augmented Question Answering

Lets users ask natural-language questions within a session; the system retrieves the most relevant chunks from only that session's ready PDFs and generates an answer using gemini-2.5-flash, with citations back to the originating PDF and page/section.

### US-009: Ask a question scoped to the active session's documents

**Priority:** critical

> As a logged-in user, I want to ask a natural-language question in a session, so that I get an answer based only on the PDFs I attached to that session.

| ID | Given | When | Then |
|---|---|---|---|
| AC-022 | a session has one or more PDFs with status 'ready' | the user submits a question | the system embeds the question, retrieves the most relevant chunks using similarity search restricted to that session's documents, and generates an answer via gemini-2.5-flash using those chunks as context |
| AC-023 | a session has documents belonging to it and the user also has other sessions with different documents | a question is asked in this session | no chunks from documents attached to other sessions (even the same user's) are retrieved or referenced in the answer |
| AC-024 | a session has no documents attached, or none are yet in 'ready' status | the user submits a question | the system responds that no ready documents are available to answer from, instead of calling the generation model with empty context |
| AC-025 | the retrieved chunks do not contain information relevant to the question | the answer is generated | the response indicates the answer could not be found in the attached documents rather than fabricating an answer |
| AC-026 | the GEMINI_API_KEY is missing, invalid, or the Gemini API call fails/times out | the user submits a question | the system shows a clear error message and does not record a fabricated assistant answer |

### US-010: View source citations for each answer

**Priority:** high

> As a logged-in user, I want each answer to include citations to the source PDF and page/section it came from, so that I can verify the information against the original document.

| ID | Given | When | Then |
|---|---|---|---|
| AC-027 | an answer was generated using one or more retrieved chunks | the answer is displayed | it includes a citation for each source chunk used, identifying the source PDF file and, where extractable, the page number or section |
| AC-028 | a source PDF's text extraction did not preserve page-level position information (e.g. due to document structure limitations) | a citation for that chunk is shown | the citation still identifies the source document by name even if page/section cannot be shown, rather than omitting the citation entirely |

## EPIC-005: Chat History

Persists the full conversation (questions and answers, with citations) for every session so users can review past exchanges at any time they return to that session.

### US-011: Retain and view full session chat history

**Priority:** high

> As a logged-in user, I want to see the complete history of questions and answers in a session, so that I can review past exchanges without losing context.

| ID | Given | When | Then |
|---|---|---|---|
| AC-029 | a user has asked multiple questions in a session over time | they reopen that session, including after logging out and back in | every prior question and its corresponding answer (with citations) is displayed in chronological order |
| AC-030 | a user has multiple sessions with separate histories | they view one session's history | only that session's messages are shown, never messages from another session |
<!-- sdlc:auto:end epics -->
