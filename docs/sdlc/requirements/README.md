# Product Requirements

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Summary

### REQ-TECH-STACK · approved · source: requirements:tech-stack

Product owner approved an exact technology stack: FastAPI 0.115 backend, AWS cloud, PostgreSQL 16 (with pgvector), React 19 frontend. Instructed to design/build against exactly these, no substitutions.

Decisions and stated rationale:
- Backend: FastAPI 0.115 — core work is PDF parsing, chunking, Gemini calls for embeddings/chat, and retrieval orchestration; Python ecosystem (PDF libs, Gemini SDK) fits, and FastAPI's async support prevents one user's generation call from blocking another's upload processing.
- Cloud: AWS — provides object storage for PDFs, a place to run the FastAPI backend and Postgres, and room to grow beyond the stated tens-to-low-hundreds of users without re-platforming.
- Database: PostgreSQL 16 — relational storage for users, sessions, documents, chat history, plus pgvector for embeddings in the same system, keeping account data, session-document links, and embeddings transactionally consistent without a separate vector database.
- Frontend: React 19 — needed for a stateful, interactive single-page chat UI: multiple sessions, per-session PDF attachment, streaming answers, and citation popovers as reusable components.

**Related:** US-001, US-005, US-007, US-008, US-009

### REQ-SERVICES · approved · source: requirements:runtime-services

Four runtime services were approved for inclusion exactly as specified: Google Gemini (SaaS AI provider), pgvector (in-Postgres vector store), Amazon S3 (file storage), and Redis (background job queue).

- AI provider: Google Gemini (SaaS, env GEMINI_API_KEY) — gemini-2.5-flash for answer generation and gemini-embedding-001 for PDF-chunk embeddings; one key covers both calls.
- Vector store: pgvector (in PostgreSQL, known) — keeps per-session-searchable chunk embeddings alongside users/sessions/documents in one database, avoiding a separate vector DB for the expected small document volume.
- File storage: Amazon S3 (SaaS, env AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET) — stores original uploaded PDFs (up to ~20MB each) separately from Postgres, for later re-opening/citation display/re-parsing.
- Queue: Redis (as a queue, container redis:7-alpine) — runs PDF parsing/chunking/embedding as a background job so uploads near the 20MB limit don't block the chat UI.
Declared API keys/env vars needed app-wide: AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, GEMINI_API_KEY, REDIS_URL, S3_BUCKET.

**Related:** US-007, US-008, US-009, US-010, US-015, US-016

- ⚠ The API keys list includes REDIS_URL, but the Redis service entry specifies only a container image (redis:7-alpine) with no named connection env var — confirm REDIS_URL is in fact the intended connection string variable for that container.

### REQ-OUT-OF-SCOPE · approved · source: requirements:out-of-scope

Three items are explicitly excluded from this version: non-PDF upload formats, cross-session/cross-document querying, and email/SMTP functionality.

- Non-PDF formats (Word, text, markdown, images, etc.) are not supported for upload in this version.
- Querying across all of a user's documents/sessions at once is not supported; queries are scoped strictly to the active session's attached documents.
- Email (the previously suggested SMTP server) was removed from the stack entirely — no email sending capability exists.

**Related:** US-007, US-009, US-001, US-002

- ⚠ Email/SMTP was removed from scope, but no alternative account-recovery (password reset) mechanism is described anywhere in the requirements for US-001/US-002 — this leaves password recovery unspecified and should be confirmed as intentionally deferred.

### REQ-CAPABILITIES · approved · source: requirements:capabilities-in-scope

Confirms the in-scope capability list: individual accounts, private per-user workspaces, multi-session chat with per-session documents, PDF parsing/chunking/embedding, session-scoped Q&A with citations, full chat history, email/password-only login (no SSO), free/no-billing usage.

Capabilities in scope, as stated: user sign-up/login with individual accounts; private per-user workspace for documents, sessions, chat history; chat session creation; PDF upload attached to a session; PDF parsing/chunking/embedding; question answering scoped to the active session's PDFs; answers with citations to source PDF and page/section; full chat history retained per session; multiple sessions per user each with own documents/thread; email/password login only, no SSO; gemini-2.5-flash for answers, gemini-embedding-001 for embeddings; PostgreSQL+pgvector for embeddings and relational data; ~20MB per-PDF limit with a per-session document count cap; free to use, no billing/payment functionality.

**Related:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011

- ⚠ The per-session document count cap is referenced (US-007/AC-016) but no specific numeric cap value is given in this input — needs to be confirmed before implementation/testing.

### US-001 · draft · source: requirements:US-001

Allows a new visitor to create an account with email and password, establishing their own private workspace.

Critical priority. Acceptance criteria: (AC-001) valid unused email + password meeting minimum complexity creates an account, stores password hashed only, and signs the user in; (AC-002) submitting an email that already has an account is rejected with a clear 'account already exists' message and no duplicate is created; (AC-003) a password failing minimum complexity rules is rejected with an explanation, and no account is created.

**Related:** EPIC-001, US-002, US-004

- ⚠ Exact password complexity rules are not specified in this input.
- ⚠ No account-recovery/password-reset flow is specified, and email/SMTP is out of scope — recovery path is unresolved.

### US-002 · draft · source: requirements:US-002

Allows a registered user to log in with email and password to reach their private sessions, documents, and chat history.

Critical priority. Acceptance criteria: (AC-004) correct credentials authenticate the user, redirect to their workspace, and issue a valid session/token; (AC-005) incorrect password or unknown email denies access with a generic invalid-credentials message that does not reveal whether the email exists; (AC-006) an expired or invalidated session/token redirects the user to login and requires re-authentication when accessing a protected page or API.

**Related:** EPIC-001, US-001, US-003

### US-003 · draft · source: requirements:US-003

Allows a logged-in user to log out, closing their session so no one else can use their workspace on that device.

Medium priority. Acceptance criterion: (AC-007) when a logged-in user logs out, their session/token is invalidated and subsequent requests to protected pages require login again.

**Related:** EPIC-001, US-002

### US-004 · draft · source: requirements:US-004

Ensures each logged-in user's documents, chat sessions, and message history are visible only to them, with no cross-user data leakage.

Critical priority. Acceptance criteria: (AC-008) listing sessions, documents, or chat history via UI or API returns only records owned by the authenticated user, never another user's data; (AC-009) directly requesting another user's session, document, or message by ID (e.g. via URL/API) is denied with an authorization error rather than returning the data.

**Related:** EPIC-001, US-001, US-006

### US-005 · draft · source: requirements:US-005

Allows a logged-in user to create a new, empty chat session as a fresh container for documents and conversation.

Critical priority. Acceptance criterion: (AC-010) confirming creation (optionally with a name) creates a new session owned by that user, with no documents attached and no messages yet.

**Related:** EPIC-002, US-006

### US-006 · draft · source: requirements:US-006

Allows a logged-in user to view a list of all their chat sessions and open any one to resume its independent documents and thread.

High priority. Acceptance criteria: (AC-011) viewing the sessions list shows all of the user's sessions (e.g. by name/date) and none belonging to other users; (AC-012) selecting a session displays only that session's attached documents and message history, independent of any other session.

**Related:** EPIC-002, US-005, US-004

### US-007 · draft · source: requirements:US-007

Allows a logged-in user to attach one or more PDF files to a chat session so its content can later be queried.

Critical priority. Acceptance criteria: (AC-013) a valid PDF within the size limit is accepted, associated only with that session, and queued for processing; (AC-014) a non-PDF file (Word, text, image, etc.) is rejected with a message stating only PDF is supported, nothing stored; (AC-015) a PDF over the ~20MB per-file limit is rejected with a clear size-limit message, nothing stored; (AC-016) once a session hits its per-session document cap, further uploads are rejected with a message explaining the limit.

**Related:** EPIC-003, US-008, US-012, US-013

- ⚠ Exact numeric value of the per-session document cap is not given in this input.

### US-008 · draft · source: requirements:US-008

Automatically parses, chunks, and embeds an uploaded PDF so its content becomes searchable for question answering within its session.

Critical priority. Acceptance criteria: (AC-017) once accepted, the pipeline extracts text, splits it into chunks retaining page-level position, embeds via gemini-embedding-001, and stores embeddings in the pgvector-backed store linked to the document and session; (AC-018) while processing, the document list shows a 'processing' status and the document is not yet usable for Q&A; (AC-019) on successful completion, the document is marked 'ready' and its chunks become available for retrieval; (AC-020) a PDF that fails to parse (corrupted, or scanned/image-only with no extractable text — OCR not supported) is marked 'failed' with an explanatory message and excluded from retrieval until a valid PDF is re-uploaded; (AC-021) a missing/invalid GEMINI_API_KEY causes processing to fail gracefully, the document is marked 'failed' with a configuration-related error, and the failure is logged.

**Related:** EPIC-003, US-007, US-009, US-015

### US-009 · draft · source: requirements:US-009

Allows a logged-in user to ask a natural-language question in a session and get an answer generated only from that session's ready PDFs.

Critical priority. Acceptance criteria: (AC-022) with one or more 'ready' PDFs in the session, the question is embedded, relevant chunks are retrieved via similarity search restricted to that session's documents, and an answer is generated via gemini-2.5-flash using those chunks as context; (AC-023) no chunks from other sessions (even the same user's) are retrieved or referenced, even though the user has other sessions with different documents; (AC-024) if no documents are attached or none are 'ready', the system responds that no ready documents are available rather than calling the generation model with empty context; (AC-025) if retrieved chunks are irrelevant to the question, the response indicates the answer could not be found in the attached documents rather than fabricating one; (AC-026) a missing/invalid GEMINI_API_KEY or a failed/timed-out Gemini call shows a clear error message and does not record a fabricated assistant answer.

**Related:** EPIC-004, US-008, US-010

### US-010 · draft · source: requirements:US-010

Shows a citation for each answer identifying the source PDF and, where available, the page or section it came from.

High priority. Acceptance criteria: (AC-027) an answer generated from retrieved chunks includes a citation per source chunk, identifying the source PDF and page/section where extractable; (AC-028) if page-level position wasn't preserved for a chunk (document structure limitations), the citation still names the source document rather than being omitted.

**Related:** EPIC-004, US-009

### US-011 · draft · source: requirements:US-011

Retains and displays the full question/answer history (with citations) for a session, in chronological order, across logins.

High priority. Acceptance criteria: (AC-029) every prior question and its answer (with citations) is shown in chronological order when a session is reopened, including after logging out and back in; (AC-030) viewing one session's history shows only that session's messages, never messages from another session.

**Related:** EPIC-005, US-006, US-009

### US-012 · draft · source: requirements:US-012

Wires the Upload PDF form to the real backend endpoint so submitted PDFs are actually stored and queued for processing, instead of only appearing to upload.

Critical priority — framed as a remediation of a previously simulated/local-only upload flow. Acceptance criteria: (AC-031) submitting a valid PDF on an open session sends a real multipart request with the user's token via apiFetch to POST /sessions/{session_id}/documents, rather than simulating the upload locally; (AC-032) once the backend accepts the upload, the new document appears in the session's Documents list with a 'processing' status sourced from the backend response, not a client-only placeholder.

**Related:** US-007, US-013, US-014

- ⚠ Input implies an earlier version simulated uploads locally; the requirements do not state why/when that happened — flagged for traceability but not treated as a current conflict.

### US-013 · draft · source: requirements:US-013

Displays the backend's real rejection reason when a PDF upload is refused, instead of a generic or simulated success.

High priority. Acceptance criteria: (AC-033) when POST /sessions/{session_id}/documents rejects a non-PDF, oversized, or over-cap upload, the form displays the exact backend error message and does not add a document to the list; (AC-034) if the backend call fails due to network or auth error, the form shows a clear error state instead of silently succeeding or leaving a simulated 'uploaded' state.

**Related:** US-007, US-012

### US-014 · draft · source: requirements:US-014

Refreshes the Documents list to reflect each document's true backend-reported status, moving from 'processing' to 'ready' or 'failed' without a fake/stuck status.

Critical priority. Acceptance criteria: (AC-035) while a document is 'processing', the session screen polls or refreshes GET /sessions/{session_id}/documents periodically until it reaches 'ready' or 'failed'; (AC-036) on successful completion, the displayed status updates to 'ready' without a full page reload; (AC-037) on failure, the displayed status updates to 'failed' and shows the backend's error_message.

**Related:** US-007, US-008, US-012

### US-015 · draft · source: requirements:US-015

Ensures the RQ worker consuming the Redis 'documents' queue actually starts and runs alongside the API in the deployed container, so queued PDF jobs are consumed instead of leaving documents stuck in 'processing' indefinitely.

Critical priority, framed from an operator perspective. Acceptance criteria: (AC-038) the container's entrypoint/CMD runs both uvicorn (the API) and an RQ worker for the 'documents' queue concurrently; (AC-039) when the worker is running, an enqueued processing job is picked up and processed without manual intervention; (AC-040) if either the API or worker process crashes, the failure is visible in container logs/exit status rather than being silently swallowed by the other process.

**Related:** US-008, US-014, US-016

- ⚠ This story implies a prior deployment lacked a running worker, leaving documents stuck in 'processing' — the requirements input does not state when/why that gap existed, only that it's being fixed.

### US-016 · draft · source: requirements:US-016

Defines end-to-end verification (by QA) that the full upload-to-ready/failed flow works against the real backend and worker after the worker fix.

High priority. Acceptance criteria: (AC-041) with the worker fix applied, a valid PDF uploaded via the UI transitions from 'processing' to 'ready' within a reasonable time and its chunks become available for Q&A; (AC-042) a corrupted or scanned image-only PDF transitions to 'failed' with an explanatory error shown in the UI; (AC-043) a non-PDF, oversized, or over-cap upload shows the backend's exact rejection message and creates no document record.

**Related:** US-007, US-008, US-015

- ⚠ This is a verification/testing-oriented story defined at requirements time; no actual test results are included in this input — testing phase should confirm these outcomes once executed.
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
