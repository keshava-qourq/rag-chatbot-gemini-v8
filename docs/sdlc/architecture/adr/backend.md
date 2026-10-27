<!-- sdlc:auto:start adr -->
# ADR-0001: Use FastAPI 0.115 for Backend

Status: Accepted  
Date: 2026-10-27

## Context and Problem Statement

Which Backend technology does the project use? Decided in architecture v1.

## Considered Options

- FastAPI 0.115
- Flask
- Django REST Framework

## Decision Outcome

Chosen option: FastAPI 0.115, because Async endpoints let one user's long-running Gemini generation call not block another user's upload request, which matters once the worker and API share the same event-loop-friendly ecosystem.

## Consequences

Async code paths require care around blocking PDF-parsing calls, which is why that work is pushed to the separate RQ worker rather than done inline in request handlers.
<!-- sdlc:auto:end adr -->