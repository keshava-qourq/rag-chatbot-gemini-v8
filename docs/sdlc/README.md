# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v20
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 4 entries |
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
| [Release notes](deployment/release-notes.md) | 8 releases |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 20 versions |
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

- Epics (EPIC-001 through EPIC-005) have no assigned role or point estimate recorded.
- Plan defines scope and ownership but contains no completion/status field per item -- actual delivery must be cross-checked against the development run log.
- No test or QA evidence accompanies this delivery record -- confirm via testing phase before treating as fully verified.
- Sub-tasks US-007-T1 through US-007-T4 have no individual status reported -- only the parent story ticket is confirmed delivered.
- No test or QA evidence accompanies this delivery record.
- Discrepancy: run status says 'completed' while 9 of 11 planned stories have no recorded ticket outcome -- confirm whether these were actually implemented, are pending, or were simply omitted from this report.
- No commit references exist for US-001, US-002, US-003, US-004, US-005, US-008, US-009, US-010, or US-011.
- No sub-task-level status for US-008-T1..T4 or US-009-T1..T4, which are critical to the embedding pipeline and grounded QA functionality.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date/timestamp recorded.
- No record of who triggered or approved this deployment.
- No indication of which requirements (US-001..US-011) or tickets are included in version 56d324cb54fd.
- No rollback plan or previous-version reference provided.
- No environment label (production/staging/other) given beyond 'live'.
- No mention of pre-deployment test results or sign-off backing this release.
- No monitoring/health-check or post-deployment verification info provided.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
