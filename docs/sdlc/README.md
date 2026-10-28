# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v16
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
| [API reference](development/api-reference.md) | 11 routes |
| [Test report](testing/test-report.md) | not run yet |
| [Tests](testing/test-cases.md) | 0 tests |
| [Deployment guide](deployment/deployment-guide.md) | deployed |
| [Runbook](deployment/runbook.md) | deployed |
| [Release notes](deployment/release-notes.md) | 6 releases |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 16 versions |
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

- Epics (EPIC-001 through EPIC-005) have no assigned role/owner recorded in the plan.
- Plan does not state who approved version 1 or on what date.
- The commit hash recorded for US-009 (0886b2162d958978b854135663937aadf5774199) is identical to the commit hash recorded for US-011 -- flagged as a possible data discrepancy since they are different tickets.
- No per-task (T1-T4) delivery confirmation was provided, only story-level status.
- No implementation detail (e.g. which UI elements display citations) was provided beyond the delivered status and commit.
- The commit hash recorded for US-011 is identical to the one recorded for US-009 -- flagged as a possible data discrepancy since they are different tickets and this may indicate a reporting error or a combined commit covering both.
- Development run status is reported as 'completed', but only 3 of 11 planned stories (US-009, US-010, US-011) have ticket delivery records -- status for US-001 through US-008 is unknown/unreported, which is inconsistent with a 'completed' run.
- Cannot confirm whether these 8 stories were built, partially built, or not started.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date/timestamp provided.
- No record of who approved or triggered this deployment.
- No information on deployment method (CI/CD pipeline, manual, containerized, etc.).
- No rollback or incident plan documented.
- No post-deployment validation or smoke test results recorded.
- No mapping given between this deployment and which requirements/features (US-001 through US-011) are actually live in this version -- related_ids assumed as full set but not confirmed by input.
- No environment variables, infrastructure, or hosting provider details (e.g. database, vector store hosting) documented.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
