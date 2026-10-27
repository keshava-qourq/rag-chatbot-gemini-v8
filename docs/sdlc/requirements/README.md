# Product Requirements

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Summary

### REQ-TECHSTACK · approved · source: requirements:tech-stack

Product owner approved an exact technology stack: FastAPI 0.115 backend, AWS cloud, PostgreSQL 16 database, React 19 frontend.

Decisions, to be designed against exactly (no substitution):
- Backend: FastAPI 0.115 -- chosen for Python's PDF/Gemini SDK ecosystem and async support so Gemini network calls don't block concurrent users.
- Cloud: AWS -- provides object storage, compute for backend+Postgres, and headroom for tens-to-low-hundreds of users without re-platforming.
- Database: PostgreSQL 16 -- relational storage for users/sessions/documents/chat history plus pgvector for embeddings in one transactionally consistent system.
- Frontend: React 19 -- stateful SPA for chat window, session/document sidebar, streaming answers, and citation popovers.

### REQ-SERVICES · approved · source: requirements:services

Four runtime services approved: Google Gemini (SaaS), pgvector (in Postgres), Amazon S3, and Redis (queue).

- AI provider: Google Gemini (SaaS, env GEMINI_API_KEY) for gemini-2.5-flash (answers) and gemini-embedding-001 (embeddings).
- Vector store: pgvector inside PostgreSQL, scoped per session.
- File storage: Amazon S3 (env AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET) for original PDFs up to ~20MB, kept separate from Postgres.
- Queue: Redis (container redis:7-alpine, env REDIS_URL) for background PDF parsing/chunking/embedding so uploads don't block the UI.
Required API keys/env vars: AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, GEMINI_API_KEY, REDIS_URL, S3_BUCKET.

**Related:** REQ-TECHSTACK

### REQ-SCOPE · approved · source: requirements:scope

Requirements v1, lightweight delivery scope. Defines in-scope capabilities and explicit out-of-scope exclusions.

In scope: email/password sign-up & login (no SSO); private per-user workspace; multiple chat sessions per user, each with its own documents/thread; PDF upload attached to a session; PDF parsing/chunking/embedding; question answering scoped to the active session's PDFs; citations to source PDF and page/section; full per-session chat history; ~20MB per-PDF limit with a per-session document count cap; free to use, no billing.
Out of scope (explicitly excluded): non-PDF formats (Word, text, markdown, images, etc.); cross-session/cross-document querying; email/SMTP functionality (removed from stack).

- ⚠ Exact numeric value for the 'per-session document count cap' is not specified anywhere in the input (only that a cap must exist) -- needs a concrete number before design/build.

### REQ-US-001 · approved · source: requirements:EPIC-001/US-001

New visitors can sign up with email and password to get a private workspace.

Acceptance criteria: valid unused email + complexity-compliant password creates an account (password hashed only) and signs the user in (AC-001); duplicate email is rejected with a clear 'account already exists' message, no duplicate created (AC-002); password failing complexity rules is rejected with an explanation, no account created (AC-003). Related NFRs: passwords stored only as hashes (NFR-001), minimum password complexity enforced (NFR-002), email/password only, no SSO (NFR-015, accepted risk).

**Related:** EPIC-001, AC-001, AC-002, AC-003, NFR-001, NFR-002, NFR-015

- ⚠ Exact minimum password complexity rules (length, character classes, etc.) are not defined in the input.

### REQ-US-002 · approved · source: requirements:EPIC-001/US-002

Registered users log in with email/password to reach their private workspace.

Correct credentials authenticate and redirect to the workspace with a valid session/token (AC-004). Incorrect password or unknown email yields a generic invalid-credentials message without revealing which (AC-005). Expired/invalidated session/token forces re-authentication via redirect to login (AC-006). Related NFRs: generic login errors (NFR-003), session expiry/invalidation (NFR-004), no SSO (NFR-015).

**Related:** EPIC-001, AC-004, AC-005, AC-006, NFR-003, NFR-004, NFR-015

### REQ-US-003 · approved · source: requirements:EPIC-001/US-003

Logged-in users can log out to close their session on the current device.

Logging out invalidates the session/token immediately; subsequent requests to protected pages/APIs require re-login (AC-007). Related NFR: sessions must expire/invalidate on logout (NFR-004).

**Related:** EPIC-001, AC-007, NFR-004

### REQ-US-004 · approved · source: requirements:EPIC-001/US-004

Each user's documents, sessions, and chat history are strictly private to that user.

Listing sessions/documents/history via UI or API returns only the authenticated user's own records; other users' data is never included (AC-008). Direct ID-based access attempts to another user's session/document/message are denied with an authorization error rather than returning data (AC-009). Related NFR: strict per-user data isolation (NFR-005).

**Related:** EPIC-001, AC-008, AC-009, NFR-005

### REQ-US-005 · approved · source: requirements:EPIC-002/US-005

Logged-in users can create a new, empty chat session, optionally named.

Confirming creation (with optional name) creates a new session owned by the user, with no documents attached and no messages yet (AC-010).

**Related:** EPIC-002, AC-010

### REQ-US-006 · approved · source: requirements:EPIC-002/US-006

Users can list and switch between their own chat sessions, each with isolated documents/history.

Viewing the sessions list shows all of the user's own sessions (by name/date) and excludes other users' sessions (AC-011). Opening a session displays only that session's attached documents and message history, independent of other sessions (AC-012).

**Related:** EPIC-002, AC-011, AC-012

### REQ-US-007 · approved · source: requirements:EPIC-003/US-007

Users can attach PDFs (only) to a session, subject to size and per-session count limits.

Valid PDF within size limit is accepted, associated only with that session, and queued for processing (AC-013). Non-PDF files are rejected with a PDF-only message, nothing stored (AC-014). PDFs over ~20MB are rejected with a size-limit message, nothing stored (AC-015). Uploads beyond the per-session document cap are rejected with an explanation (AC-016). Related NFRs: ~20MB per-file cap (NFR-006), per-session document count cap (NFR-007), PDF-only accepted risk (NFR-008).

**Related:** EPIC-003, AC-013, AC-014, AC-015, AC-016, NFR-006, NFR-007, NFR-008

- ⚠ Numeric value of the per-session document cap is not specified (see REQ-SCOPE gap).

### REQ-US-008 · approved · source: requirements:EPIC-003/US-008

Uploaded PDFs are parsed, chunked (with page position), embedded via gemini-embedding-001, and tracked through processing/ready/failed states.

On acceptance, text is extracted, chunked with page-level position retained, embedded via gemini-embedding-001, and stored in pgvector linked to the document/session (AC-017). While processing, the document shows 'processing' and is unusable for Q&A (AC-018). On success it is marked 'ready' with chunks available for retrieval (AC-019). Parse failures (corrupted or scanned/image-only PDFs, no OCR support) mark the document 'failed' with an explanatory message and exclude it from retrieval (AC-020). Missing/invalid GEMINI_API_KEY causes graceful failure, 'failed' status with a configuration-related error, and logging (AC-021). Related NFRs: no OCR accepted risk (NFR-009), background queue-based processing (NFR-010), graceful Gemini failure handling (NFR-011).

**Related:** EPIC-003, AC-017, AC-018, AC-019, AC-020, AC-021, NFR-009, NFR-010, NFR-011

### REQ-US-009 · approved · source: requirements:EPIC-004/US-009

Users ask natural-language questions answered only from the active session's ready PDFs, via gemini-2.5-flash.

With ready documents present, the question is embedded, relevant chunks retrieved via similarity search scoped to the session, and an answer generated via gemini-2.5-flash using those chunks (AC-022). No chunks from other sessions (even same user's) are ever used (AC-023). If no documents are attached or none are ready, the system states no ready documents are available rather than calling the model with empty context (AC-024). If retrieved chunks are irrelevant, the response states the answer could not be found rather than fabricating one (AC-025). Missing/invalid API key or failed/timed-out Gemini call shows a clear error and does not record a fabricated answer (AC-026). Related NFRs: graceful Gemini failure handling (NFR-011), answers grounded only in retrieved content (NFR-012), no cross-session/cross-document search, accepted risk (NFR-013).

**Related:** EPIC-004, AC-022, AC-023, AC-024, AC-025, AC-026, NFR-011, NFR-012, NFR-013

### REQ-US-010 · approved · source: requirements:EPIC-004/US-010

Every generated answer includes citations back to source PDF and page/section where available.

Answers include a citation for each source chunk used, naming the source PDF and, where extractable, the page/section (AC-027). If page-level position wasn't preserved for a chunk, the citation still names the source document rather than being omitted (AC-028). Related NFR: citations always name the source document (NFR-014).

**Related:** EPIC-004, AC-027, AC-028, NFR-014

### REQ-US-011 · approved · source: requirements:EPIC-005/US-011

Full per-session chat history (Q&A with citations) is retained and viewable in chronological order.

Reopening a session, including after logging out and back in, displays every prior question and answer (with citations) in chronological order (AC-029). History is strictly per-session; one session's messages never appear in another's view (AC-030).

**Related:** EPIC-005, AC-029, AC-030

### REQ-NFR-016 · approved · source: requirements:NFR-016

System-wide scalability target: comfortably support tens to low hundreds of concurrent users without redesign.

Applies to the whole system rather than a single story; no specific load-testing approach or infrastructure sizing has been defined yet.

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

- ⚠ No architecture or capacity plan exists yet to confirm this target is achievable.
<!-- sdlc:auto:end narrative -->

<!-- sdlc:auto:start summary -->
**Requirements version:** v1  
**Delivery scope:** lightweight  
**Approved:** 2026-10-27

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
