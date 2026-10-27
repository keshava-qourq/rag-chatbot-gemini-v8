# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v3
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 5 entries |
| [Testing](testing/README.md) | 1 entry |
| [Deployment](deployment/README.md) | 1 entry |
| [Maintenance](maintenance/README.md) | 1 entry |
| [Data model](architecture/data-model.md) | generated |
| [API (OpenAPI)](architecture/api/openapi.yaml) | generated |
| [Decisions (ADRs)](architecture/adr/README.md) | 4 decisions |
| [Sprint plan](development/sprint-plan.md) | 4 sprints |
| [Developer guide](development/developer-guide.md) | generated |
| [API reference](development/api-reference.md) | 1 route |
| [Test report](testing/test-report.md) | not run yet |
| [Tests](testing/test-cases.md) | 0 tests |
| [Deployment guide](deployment/deployment-guide.md) | not deployed yet |
| [Runbook](deployment/runbook.md) | not deployed yet |
| [Release notes](deployment/release-notes.md) | 0 releases |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 3 versions |
<!-- sdlc:auto:end contents -->

## Open gaps

<!-- sdlc:auto:start open-gaps -->
### Requirements

- Exact numeric value for the 'per-session document count cap' is not specified anywhere in the input (only that a cap must exist) -- needs a concrete number before design/build.
- Exact minimum password complexity rules (length, character classes, etc.) are not defined in the input.
- Numeric value of the per-session document cap is not specified (see REQ-SCOPE gap).
- No architecture or capacity plan exists yet to confirm this target is achievable.

### Architecture

- Input does not map this architecture to specific requirement IDs (US-001..US-011); traceability from requirements to architecture elements is not explicit.
- Not explicitly linked to a specific requirement ID in the input.

### Development

- No record of who approved the plan or when.
- No execution/progress status (in-progress, done, blocked) given for any sprint or item — only the backlog plan itself was provided.
- No evidence provided that these items were actually implemented or completed — only planned.
- No evidence provided that these items or sub-tasks were actually implemented or completed — only planned.
- No detail on validation rules (allowed file types, size/count limits) beyond the task title.
- No specifics given on chunking strategy parameters (chunk size, overlap) or failure-handling behavior beyond task titles.
- No detail on how citations are rendered or on chat history retention limits/format beyond the story titles.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment recorded yet -- nothing to document for this phase.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
