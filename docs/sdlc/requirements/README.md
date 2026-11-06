# Product Requirements

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Summary

### REQ-SCOPE · approved · source: requirements:scope

Lightweight v2 requirements for a PDF-only RAG chatbot with authenticated per-user workspaces, Gemini-based embeddings/answers, and no billing, SSO, or email.

- Approved stack (do not substitute): FastAPI 0.115 backend, AWS cloud, PostgreSQL 16 (with pgvector), React 19 frontend.
- Approved runtime services: Google Gemini (env GEMINI_API_KEY) for gemini-2.5-flash answers and gemini-embedding-001 embeddings; pgvector inside PostgreSQL for vector search; Amazon S3 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET) for original PDFs; Redis (REDIS_URL, container redis:7-alpine) as a background job queue.
- Out of scope: non-PDF upload formats (Word, text, markdown, images); cross-session/cross-document querying (queries scoped strictly to the active session); email/SMTP (removed from stack).
- In-scope capabilities: email/password sign-up and login (no SSO); private per-user workspace; multiple chat sessions per user, each with its own documents and thread; PDF upload with ~20MB per-file limit and per-session document count cap; PDF parsing/chunking/embedding; question answering scoped to the active session's ready PDFs; answers with citations to source PDF and page/section; full per-session chat history; free to use, no billing.

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

### EPIC-001 · approved · source: requirements:EPIC-001

Covers account creation, login/logout, and strict per-user data isolation so each user only ever sees and affects their own workspace.

- US-001 [critical]: sign up with email+password; password stored only hashed; user signed in on success (AC-001); duplicate email rejected with clear message, no duplicate account (AC-002); weak password rejected with requirements explained, no account created (AC-003).
- US-002 [critical]: login with email+password issues a valid session/token (AC-004); wrong password or unknown email gets a generic invalid-credentials message, no email enumeration (AC-005); expired/invalidated session forces redirect to login (AC-006).
- US-003 [medium]: logout invalidates the session/token; subsequent protected requests require re-login (AC-007).
- US-004 [critical, security-agent]: listing sessions/documents/history returns only the authenticated user's own records (AC-008); direct access to another user's session/document/message by ID is denied with an authorization error (AC-009).

**Related:** US-001, US-002, US-003, US-004, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009

### EPIC-002 · approved · source: requirements:EPIC-002

Lets a logged-in user create and switch between multiple independent chat sessions, each with its own documents and conversation thread.

- US-005 [critical]: creating a session (optionally naming it) produces a new, empty, user-owned session with no documents or messages yet (AC-010).
- US-006 [high, frontend-agent]: sessions list shows all of a user's own sessions by name/date, never another user's (AC-011); opening a session shows only that session's documents and history, independent of other sessions (AC-012).

**Related:** US-005, US-006, AC-010, AC-011, AC-012

### EPIC-003 · approved · source: requirements:EPIC-003

Validates and stores per-session PDF uploads, processes them asynchronously into embedded chunks, and includes later fixes ensuring the upload-to-ready pipeline actually works end-to-end in the deployed app.

- US-007 [critical]: valid PDF within size limit is accepted, scoped to its session, and queued (AC-013); non-PDF files rejected with a PDF-only message, nothing stored (AC-014); oversized (~20MB+) PDFs rejected with a size-limit message, nothing stored (AC-015); uploads beyond the per-session document cap rejected with a cap-limit message (AC-016).
- US-008 [critical]: pipeline extracts text, chunks with page-level position, embeds via gemini-embedding-001, stores in pgvector (AC-017); document shows 'processing' until done and is unusable for QA until then (AC-018); successful completion marks it 'ready' with chunks available (AC-019); failed parse (corrupted or scanned/image-only PDF, no OCR support) marks it 'failed' with an explanatory message and excludes it from retrieval (AC-020); missing/invalid GEMINI_API_KEY fails gracefully with a configuration-related error, logged (AC-021).
- US-012 [critical, frontend-agent]: Upload PDF form wired to real POST /sessions/{session_id}/documents via apiFetch with the user's token, replacing a client-only simulated upload (AC-031); new document appears in the Documents list with backend-sourced 'processing' status, not a placeholder (AC-032).
- US-013 [high, frontend-agent]: form surfaces the exact backend rejection message for non-PDF, oversized, or over-cap uploads without adding a document (AC-033); network/auth failures show a clear error state instead of a silent success or fake 'uploaded' state (AC-034).
- US-014 [critical, frontend-agent]: Documents list polls/refreshes GET /sessions/{session_id}/documents until each document reaches 'ready' or 'failed' (AC-035); status updates to 'ready' without a full page reload (AC-036); failures update to 'failed' and show the backend's error_message (AC-037).
- US-015 [critical, devops-agent]: container entrypoint runs uvicorn and an RQ worker for the 'documents' queue concurrently (AC-038), so queued jobs are consumed without manual intervention (AC-039); a crash in either process is visible in logs/exit status rather than silently swallowed (AC-040).
- US-016 [high, qa-agent]: end-to-end verification that a valid PDF reaches 'ready' with chunks usable for QA (AC-041); a corrupted/scanned PDF reaches 'failed' with an explanatory UI error (AC-042); non-PDF/oversized/over-cap uploads show the backend's exact rejection message with no document record created (AC-043).

**Related:** US-007, US-008, US-012, US-013, US-014, US-015, US-016, AC-013, AC-014, AC-015, AC-016, AC-017, AC-018, AC-019, AC-020, AC-021, AC-031, AC-032, AC-033, AC-034, AC-035, AC-036, AC-037, AC-038, AC-039, AC-040, AC-041, AC-042, AC-043

### EPIC-004 · approved · source: requirements:EPIC-004

Answers user questions using only the active session's ready documents via similarity search and gemini-2.5-flash, always including source citations.

- US-009 [critical]: question is embedded, similarity search restricted to the session's ready documents, and an answer generated via gemini-2.5-flash from retrieved chunks (AC-022); never retrieves/references chunks from other sessions, even the same user's (AC-023); no ready documents yields an explicit 'no ready documents' response instead of calling the model with empty context (AC-024); irrelevant retrieved content yields a 'not found in attached documents' response rather than a fabricated answer (AC-025); missing/invalid API key or a failed/timed-out Gemini call shows a clear error and records no fabricated assistant answer (AC-026).
- US-010 [high, frontend-agent]: each answer includes a citation per source chunk naming the source PDF and, where extractable, the page/section (AC-027); if page/section can't be extracted, the citation still names the document rather than being omitted (AC-028).

**Related:** US-009, US-010, AC-022, AC-023, AC-024, AC-025, AC-026, AC-027, AC-028

### EPIC-005 · approved · source: requirements:EPIC-005

Persists and displays the full chronological chat history (questions, answers, citations) per session, surviving logout/login.

- US-011 [high]: reopening a session, including after logout and back in, shows every prior question and answer with citations in chronological order (AC-029); viewing one session's history never shows another session's messages (AC-030).

**Related:** US-011, AC-029, AC-030
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
