# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v14
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 10 entries |
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
| [Release notes](deployment/release-notes.md) | 5 releases |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 14 versions |
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

- Input lists sprints and backlog items separately with no explicit field mapping which item belongs to which sprint; mapping used in epic-level entries below is inferred from goal text and epic grouping, not stated directly.
- No development-run ticket status reported for US-001, US-002, US-003, or US-004 despite the dev run being marked 'completed' -- unclear whether these were implemented.
- No development-run ticket status reported for US-005 or US-006 despite the dev run being marked 'completed' -- unclear whether these were implemented.
- No development-run ticket status reported for US-007, US-008, or any of their sub-tasks (T1-T4 each) despite the dev run being marked 'completed' -- unclear whether the upload flow or embedding pipeline were implemented.
- US-010 (citations) was recorded in the dev run as skipped with no commit -- reason not stated in input.
- No individual task-level (T1-T4) status reported for US-009 beyond the overall story being marked delivered.
- US-011 (persistent chat history) was recorded in the dev run as skipped with no commit -- reason not stated in input. This directly affects the project's stated goal of 'having chat history and sessions'.
- Discrepancy: the run is marked 'completed' but 8 of 11 planned stories (US-001-US-008) have no reported ticket status -- unclear if they were built, not attempted, or simply omitted from this input.
- No task-level (Txx) ticket statuses were reported for any story.
- Only story-level delivery is confirmed; individual sub-task (T1-T4) completion was not separately reported.
- Reason for skipping not provided in input.
- Citation display functionality should not be assumed to exist in the built application.
- Persistent chat history should not be assumed to exist in the built application, despite being a core part of the project description.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date recorded.
- No approver or responsible party recorded for this release.
- No indication of which specific requirements/features (US-001 through US-011) are included in this version -- all are tentatively linked pending confirmation.
- No rollback plan, infrastructure/environment details (e.g. region, scaling config), or CI/CD pipeline information provided.
- No post-deployment validation, smoke test, or monitoring results recorded.
- No confirmation of database/vector store or secrets configuration for the live environment.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
