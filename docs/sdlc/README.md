# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v18
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 12 entries |
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
| [Changelog](CHANGELOG.md) | 18 versions |
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

- Commit hash for US-002 is 41 characters, one longer than a standard 40-character SHA-1 hash -- possible transcription issue in the source input.
- US-003 and US-004 share the identical commit hash; confirm whether this is a single combined commit or a data entry duplication.
- Commit hash is identical across US-003, US-004, and US-005; confirm whether these were genuinely a single combined commit.
- Development run status is 'completed' but no ticket entry exists for US-006 in the input; actual delivery status is unknown.
- Development run status is 'completed' but no ticket entry exists for US-007 or its sub-tasks (T1-T4); actual delivery status is unknown.
- Development run status is 'completed' but no ticket entry exists for US-008 or its sub-tasks (T1-T4); actual delivery status, including whether gemini-embedding-001 integration works, is unknown.
- Development run status is 'completed' but no ticket entry exists for US-009 or its sub-tasks (T1-T4); actual delivery status, including whether gemini-2.5-flash grounding works, is unknown.
- Development run status is 'completed' but no ticket entry exists for US-010 in the input; actual delivery status is unknown.
- Development run status is 'completed' but no ticket entry exists for US-011 in the input; actual delivery status is unknown.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date/timestamp given.
- No record of who approved or triggered this deployment.
- No infrastructure, environment variables, or configuration details provided.
- No monitoring, logging, or rollback plan documented.
- No mapping from this deployment to which requirements (US-001..US-011) were actually included/verified in this release -- related_ids listed speculatively since all are presumably part of the product but not confirmed scoped to this version.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
