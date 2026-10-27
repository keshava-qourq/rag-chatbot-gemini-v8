<!-- sdlc:auto:start adr -->
# ADR-0003: Use PostgreSQL 16 for Database

Status: Accepted  
Date: 2026-10-27

## Context and Problem Statement

Which Database technology does the project use? Decided in architecture v1.

## Considered Options

- PostgreSQL 16
- MongoDB + separate vector DB
- MySQL

## Decision Outcome

Chosen option: PostgreSQL 16, because Relational tables for users/sessions/documents/messages and pgvector columns for chunk embeddings live in one transactional system, so a document's status and its embeddings are never out of sync.

## Consequences

pgvector similarity search at low-hundreds-of-users scale needs only a basic ivfflat/hnsw index; a dedicated vector database would be unnecessary operational overhead here.
<!-- sdlc:auto:end adr -->