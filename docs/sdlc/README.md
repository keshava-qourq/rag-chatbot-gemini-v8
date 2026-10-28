# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v12
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 7 entries |
| [Testing](testing/README.md) | 1 entry |
| [Deployment](deployment/README.md) | 1 entry |
| [Maintenance](maintenance/README.md) | 1 entry |
| [Data model](architecture/data-model.md) | generated |
| [API (OpenAPI)](architecture/api/openapi.yaml) | generated |
| [Decisions (ADRs)](architecture/adr/README.md) | 4 decisions |
| [Sprint plan](development/sprint-plan.md) | 4 sprints |
| [Developer guide](development/developer-guide.md) | generated |
| [API reference](development/api-reference.md) | 11 routes |
| [Test report](testing/test-report.md) | not run yet |
| [Tests](testing/test-cases.md) | 0 tests |
| [Deployment guide](deployment/deployment-guide.md) | deployed |
| [Runbook](deployment/runbook.md) | deployed |
| [Release notes](deployment/release-notes.md) | 4 releases |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 12 versions |
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

- Plan input does not state which backlog items/tasks are assigned to which sprint -- only per-sprint goals and capacities are given, so sprint-to-item mapping below is inferred thematically, not confirmed.
- Epics themselves carry no story points or assigned role in the input.
- No explicit item-to-sprint assignment was provided; association above is inferred from the sprint goal text only.
- No per-sub-task (US-008-T1..T4) completion confirmation was given, only the parent ticket's delivered status and commit.
- No test or review evidence was included in this phase's input for this ticket.
- Discrepancy: phase-level run status says 'completed' but 10 of 11 planned stories have no ticket-level delivery record in the input -- flagging for confirmation rather than assuming they were delivered or skipped.
- No commit references, review notes, or task-level status exist for these items in this phase's input.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date/timestamp recorded.
- No indication of who approved or triggered this deployment.
- No release notes or changelog linking this version to specific requirements (US-001..US-011) or development tickets.
- No environment details (e.g., staging vs production, region, infra config) provided.
- No rollback plan or prior version reference provided to assess what changed in this release.
- No post-deployment verification/test results (smoke tests, health checks) recorded.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
