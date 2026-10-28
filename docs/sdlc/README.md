# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v9
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
| [Release notes](deployment/release-notes.md) | 3 releases |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 9 versions |
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

- No explicit sprint-to-story assignment table was given; sprint-to-story mapping below is inferred from sprint goal text matching story content, not an authoritative field in the input.
- Epic has no assigned role or point total in the input.
- No implementation tasks (T1, T2, ...) were broken out for US-001–US-004, unlike later epics -- unclear if this is intentional or missing.
- No delivery/ticket status reported for US-001, US-002, US-003, or US-004.
- No implementation tasks were broken out for US-005/US-006.
- No delivery/ticket status reported for US-005 or US-006.
- No delivery/ticket status reported for US-007 or any of its sub-tasks (T1–T4), despite US-008 (which logically depends on uploads existing) being marked delivered -- potential sequencing discrepancy worth flagging to the team.
- No delivery/ticket status reported for US-009, US-010, or US-009's sub-tasks.
- No delivery/ticket status reported for US-011.
- Discrepancy: run status is 'completed' but delivery evidence (ticket status + commit) was only supplied for US-008; no ticket records were given for US-001 through US-007, US-009, US-010, or US-011, so their completion cannot be confirmed from this input.
- No date/timestamp was provided for the run or for the US-008 delivery.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- Deployment date/timestamp not provided.
- No record of who approved or triggered this deployment.
- No mapping given between this release and specific requirement IDs (US-001 through US-011), so related requirements cannot be confirmed as live.
- No rollback plan, infrastructure details, or environment configuration (e.g. staging vs production) documented.
- No post-deployment verification or smoke-test results recorded.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
