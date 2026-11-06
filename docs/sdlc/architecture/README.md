# Architecture

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Overview

### ARCH-001 · approved · source: architecture:summary

Architecture v1 approved: React 19 SPA + FastAPI 0.115 backend (JWT auth) + S3 (PDFs) + PostgreSQL 16/pgvector (relational data + embeddings) + Redis-queued background worker + Gemini (embeddings & chat), all on AWS.

Components:
- web_app: React 19 SPA for sign-up/login, session list, PDF upload, streaming chat window, citation display.
- api_backend: FastAPI 0.115 -- JWT issuance/validation, session/document/message CRUD, upload validation, job enqueueing, retrieval/Gemini orchestration, per-user data isolation enforcement.
- worker: Python RQ background worker consuming Redis -- downloads PDF from S3, extracts text with page positions, chunks, calls Gemini for embeddings, writes to Postgres, marks document ready/failed.
- postgres: PostgreSQL 16 + pgvector -- users, sessions, documents, chunk text/embeddings, messages, citations; per-session similarity search.
- redis: Redis 7 (redis:7-alpine container) -- buffers PDF processing jobs so uploads return immediately.
- s3: Amazon S3 -- durable original PDF storage, retrievable for re-parsing and citation display.
- gemini: Google Gemini API (SaaS) -- gemini-embedding-001 for embeddings, gemini-2.5-flash for grounded chat answers.

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

### ARCH-002 · approved · source: architecture:critical_paths

Critical path: User Authentication.

Email/password sign-up and login issuing a JWT, with hashed password storage and generic failure messaging on login errors.

**Related:** EPIC-001, US-001, US-002, US-003, US-004

### ARCH-003 · approved · source: architecture:critical_paths

Critical path: PDF Upload and Processing Pipeline.

Validated PDF is stored in S3, queued, then parsed, chunked, embedded via Gemini, and persisted with page-level position for later retrieval.

**Related:** EPIC-003, US-007, US-008, US-015

### ARCH-004 · approved · source: architecture:critical_paths

Critical path: Retrieval-Augmented Question Answering.

Question embedded, similarity search scoped strictly to the active session's ready documents, answer generated with citations.

**Related:** EPIC-004, US-009, US-010

### ARCH-005 · approved · source: architecture:entities

Data model supporting users, sessions, documents, chunk embeddings, messages, and citations.

- users: id, email, password_hash, created_at.
- sessions: id, user_id, name, created_at.
- documents: id, session_id, user_id, filename, s3_key, size_bytes, page_count, status, error_message, created_at.
- document_chunks: id, document_id, session_id, chunk_index, page_number, content, embedding, created_at.
- messages: id, session_id, role, content, created_at.
- citations: id, message_id, document_id, chunk_id, page_number, snippet.

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

### ARCH-006 · approved · source: architecture:endpoints

Backend API surface for auth, sessions, documents, and messages.

- POST /auth/signup -- create account (complexity + uniqueness enforced).
- POST /auth/login -- authenticate, issue JWT.
- POST /auth/logout -- invalidate current session/token.
- GET /sessions -- list own chat sessions.
- POST /sessions -- create a new empty session.
- GET /sessions/{session_id} -- get session details, owner-scoped.
- POST /sessions/{session_id}/documents -- upload PDF (multipart), validated, queued.
- GET /sessions/{session_id}/documents -- list documents with processing status.
- POST /sessions/{session_id}/messages -- ask a question scoped to session's ready documents, get answer + citations.
- GET /sessions/{session_id}/messages -- full chronological chat history.

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005

### ARCH-007 · approved · source: architecture:deployment_nodes

Deployment topology on AWS.

- frontend: AWS S3 + CloudFront static hosting, React 19 production build.
- api_service: AWS ECS Fargate, FastAPI 0.115 on Uvicorn.
- worker_service: AWS ECS Fargate, RQ background worker.
- database: AWS RDS for PostgreSQL 16 with pgvector enabled.
- queue: ECS Fargate (self-managed container), redis:7-alpine.
- file_storage: Amazon S3, managed object storage.
- ai_provider: Google Gemini API (gemini-2.5-flash, gemini-embedding-001).

### ARCH-008 · approved · source: architecture:technology_decisions

Rationale for the four core technology choices, with alternatives considered.

- Backend: FastAPI 0.115 (alternatives: Flask, Django REST Framework) -- async endpoints let one user's long Gemini call not block another's upload.
- Frontend: React 19 (alternatives: Vue, Svelte) -- composable stateful components fit the session sidebar, streaming chat window, citation popovers; mature streaming-fetch/PDF-rendering ecosystem.
- Database: PostgreSQL 16 (alternatives: MongoDB + separate vector DB, MySQL) -- relational tables plus pgvector columns in one transactional system keep document status and embeddings in sync.
- Cloud: AWS (alternatives: GCP, Azure) -- S3, RDS, and ECS Fargate for API/worker/Redis give one provider for storage, compute, and database at this scale.
<!-- sdlc:auto:end narrative -->

<!-- sdlc:auto:start building-blocks -->
## Building Block View

| ID | Name | Technology | Responsibility | Depends on |
|---|---|---|---|---|
| web_app | Web Application | React 19 | React SPA for sign-up/login, session list, PDF upload, chat window with streaming answers, and citation display | api_backend |
| api_backend | API Backend | FastAPI 0.115 | Auth (JWT issuance/validation), session/document/message CRUD, upload validation, enqueues processing jobs, orchestrates retrieval and Gemini calls, enforces per-user data isolation | postgres, redis, s3, gemini |
| worker | PDF Processing Worker | Python (FastAPI ecosystem) background worker using RQ, consuming Redis | Consumes queued jobs, downloads PDF from S3, extracts text with page positions, chunks text, calls Gemini for embeddings, writes chunks/embeddings to Postgres, marks document ready/failed | postgres, redis, s3, gemini |
| postgres | PostgreSQL Database | PostgreSQL 16 with pgvector extension | Stores users, sessions, documents, chunk text and embeddings, messages and citations; serves per-session similarity search via pgvector | — |
| redis | Background Job Queue | Redis 7 (redis:7-alpine, container) | Buffers PDF processing jobs so upload requests return immediately while parsing/chunking/embedding happens asynchronously | — |
| s3 | Document Storage | Amazon S3 | Durable storage of original uploaded PDFs, retrievable for re-parsing and citation source display | — |
| gemini | Gemini AI Provider | Google Gemini API (SaaS) | Generates chunk/query embeddings (gemini-embedding-001) and grounded chat answers (gemini-2.5-flash) | — |

```mermaid
graph TD
  c_web_app["Web Application"]
  c_api_backend["API Backend"]
  c_worker["PDF Processing Worker"]
  c_postgres["PostgreSQL Database"]
  c_redis["Background Job Queue"]
  c_s3["Document Storage"]
  c_gemini["Gemini AI Provider"]
  c_web_app --> c_api_backend
  c_api_backend --> c_postgres
  c_api_backend --> c_redis
  c_api_backend --> c_s3
  c_api_backend --> c_gemini
  c_worker --> c_postgres
  c_worker --> c_redis
  c_worker --> c_s3
  c_worker --> c_gemini
```
<!-- sdlc:auto:end building-blocks -->

<!-- sdlc:auto:start runtime -->
## Runtime View

### User Authentication

Email/password sign-up and login issuing a JWT, with hashed password storage and generic failure messaging

- **Components:** web_app, api_backend, postgres
- **Modules:** auth_router, auth_service, password_hashing, jwt_utils
- **Key functions:** signup(email, password), login(email, password), hash_password(password), verify_password(password, hash), create_access_token(user_id), verify_token(token)

```mermaid
sequenceDiagram
  participant U as User
  participant W as WebApp
  participant A as APIBackend
  participant DB as Postgres
  U->>W: Enter email and password
  W->>A: POST /auth/signup or /auth/login
  A->>DB: Query user by email
  DB-->>A: User record or none
  A->>A: Verify password hash or hash new password
  A->>DB: Insert new user record (signup only)
  A-->>W: JWT access token
  W-->>U: Redirect to workspace
```

### PDF Upload and Processing Pipeline

Validated PDF is stored in S3, queued, then parsed, chunked, embedded via Gemini, and persisted with page-level position for later retrieval

- **Components:** web_app, api_backend, s3, redis, worker, postgres, gemini
- **Modules:** upload_router, document_service, s3_client, pdf_parser, chunker, embedding_client, job_queue
- **Key functions:** upload_pdf(session_id, file), validate_pdf(file, session_id), enqueue_processing_job(document_id), parse_pdf(s3_key), chunk_text(pages), embed_chunks(chunks), store_chunks(document_id, chunks, embeddings), mark_status(document_id, status, error)

```mermaid
sequenceDiagram
  participant U as User
  participant W as WebApp
  participant A as APIBackend
  participant S3 as S3
  participant Q as Redis
  participant WK as Worker
  participant DB as Postgres
  participant G as Gemini
  U->>W: Select PDF and upload
  W->>A: POST /sessions/id/documents
  A->>A: Validate type, size, per-session cap
  A->>S3: Store original PDF
  A->>DB: Create document record, status processing
  A->>Q: Enqueue processing job
  A-->>W: 202 Accepted, status processing
  WK->>Q: Pick up job
  WK->>S3: Fetch PDF
  WK->>WK: Parse text and chunk by page
  WK->>G: Request embeddings for chunks
  G-->>WK: Embedding vectors
  WK->>DB: Store chunks and embeddings, mark ready or failed
  W->>A: Poll document status
  A->>DB: Read status
  A-->>W: processing, ready, or failed
```

### Retrieval-Augmented Question Answering

Question embedded, similarity search scoped strictly to the active session's ready documents, answer generated with citations

- **Components:** web_app, api_backend, postgres, gemini
- **Modules:** chat_router, retrieval_service, embedding_client, gemini_client, citation_builder
- **Key functions:** ask_question(session_id, question), embed_query(question), similarity_search(session_id, query_vector, top_k), generate_answer(question, chunks), build_citations(chunks), save_message(session_id, role, content, citations)

```mermaid
sequenceDiagram
  participant U as User
  participant W as WebApp
  participant A as APIBackend
  participant DB as Postgres
  participant G as Gemini
  U->>W: Ask question in session
  W->>A: POST /sessions/id/messages
  A->>DB: Check session has ready documents
  A->>G: Embed question text
  G-->>A: Query embedding vector
  A->>DB: Similarity search scoped to session documents
  DB-->>A: Top matching chunks
  A->>G: Generate answer with chunks as context
  G-->>A: Answer text
  A->>DB: Save message and citations
  A-->>W: Answer with citations
  W-->>U: Display answer and citation links
```
<!-- sdlc:auto:end runtime -->

<!-- sdlc:auto:start deployment-view -->
## Deployment View

| Name | Service | Runtime | Scaling | Environment |
|---|---|---|---|---|
| frontend | AWS S3 + CloudFront static hosting | React 19 production build | CDN edge caching, no server scaling needed | dev |
| api_service | AWS ECS Fargate | FastAPI 0.115 on Uvicorn | 1 task for dev, autoscale on CPU for staging/prod | dev |
| worker_service | AWS ECS Fargate | RQ background worker (Python, FastAPI ecosystem) | 1 task for dev, autoscale on Redis queue depth | dev |
| database | AWS RDS for PostgreSQL | PostgreSQL 16 with pgvector extension enabled | single db.t4g.micro instance for dev | dev |
| queue | ECS Fargate (self-managed container) | redis:7-alpine | single instance for dev | dev |
| file_storage | Amazon S3 | object storage, managed | managed by AWS | dev |
| ai_provider | Google Gemini API | gemini-2.5-flash, gemini-embedding-001 | managed by Google | dev |

| Source | Target | Protocol |
|---|---|---|
| frontend | api_service | HTTPS |
| api_service | database | PostgreSQL (TCP 5432, TLS) |
| api_service | queue | Redis protocol (TCP 6379) |
| api_service | file_storage | HTTPS |
| api_service | ai_provider | HTTPS |
| worker_service | queue | Redis protocol (TCP 6379) |
| worker_service | database | PostgreSQL (TCP 5432, TLS) |
| worker_service | file_storage | HTTPS |
| worker_service | ai_provider | HTTPS |

```mermaid
graph LR
  n_frontend["frontend<br/>AWS S3 + CloudFront static hosting"]
  n_api_service["api_service<br/>AWS ECS Fargate"]
  n_worker_service["worker_service<br/>AWS ECS Fargate"]
  n_database["database<br/>AWS RDS for PostgreSQL"]
  n_queue["queue<br/>ECS Fargate (self-managed container)"]
  n_file_storage["file_storage<br/>Amazon S3"]
  n_ai_provider["ai_provider<br/>Google Gemini API"]
  n_frontend -->|"HTTPS"| n_api_service
  n_api_service -->|"PostgreSQL (TCP 5432, TLS)"| n_database
  n_api_service -->|"Redis protocol (TCP 6379)"| n_queue
  n_api_service -->|"HTTPS"| n_file_storage
  n_api_service -->|"HTTPS"| n_ai_provider
  n_worker_service -->|"Redis protocol (TCP 6379)"| n_queue
  n_worker_service -->|"PostgreSQL (TCP 5432, TLS)"| n_database
  n_worker_service -->|"HTTPS"| n_file_storage
  n_worker_service -->|"HTTPS"| n_ai_provider
```
<!-- sdlc:auto:end deployment-view -->

<!-- sdlc:auto:start decisions -->
## Architecture Decisions

| Layer | Choice | ADR |
|---|---|---|
| Backend | FastAPI 0.115 | [ADR-0001](adr/backend.md) |
| Frontend | React 19 | [ADR-0002](adr/frontend.md) |
| Database | PostgreSQL 16 | [ADR-0003](adr/database.md) |
| Cloud | AWS | [ADR-0004](adr/cloud.md) |
<!-- sdlc:auto:end decisions -->

<!-- sdlc:auto:start links -->
## Related Documents

- [Data Model](data-model.md)
- [API Specification](api/openapi.yaml)
- [Architecture Decision Records](adr/README.md)
<!-- sdlc:auto:end links -->
