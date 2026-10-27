<!-- sdlc:auto:start adr -->
# ADR-0002: Use React 19 for Frontend

Status: Accepted  
Date: 2026-10-27

## Context and Problem Statement

Which Frontend technology does the project use? Decided in architecture v1.

## Considered Options

- React 19
- Vue
- Svelte

## Decision Outcome

Chosen option: React 19, because The session sidebar, streaming chat window, and citation popovers are naturally expressed as composable, stateful components, and React's ecosystem has mature streaming-fetch and PDF-rendering libraries.

## Consequences

Needs a client-side router and state management (session list vs active session) to be built explicitly since this is an SPA with no server-rendering framework in the approved stack.
<!-- sdlc:auto:end adr -->