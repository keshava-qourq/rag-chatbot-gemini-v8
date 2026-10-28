# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v26
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v2 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 13 entries |
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
| [Release notes](deployment/release-notes.md) | 11 releases |
| [Traceability matrix](traceability-matrix.md) | 16 requirements |
| [Changelog](CHANGELOG.md) | 26 versions |
<!-- sdlc:auto:end contents -->

## Open gaps

<!-- sdlc:auto:start open-gaps -->
### Requirements

- The API keys list includes REDIS_URL, but the Redis service entry specifies only a container image (redis:7-alpine) with no named connection env var — confirm REDIS_URL is in fact the intended connection string variable for that container.
- Email/SMTP was removed from scope, but no alternative account-recovery (password reset) mechanism is described anywhere in the requirements for US-001/US-002 — this leaves password recovery unspecified and should be confirmed as intentionally deferred.
- The per-session document count cap is referenced (US-007/AC-016) but no specific numeric cap value is given in this input — needs to be confirmed before implementation/testing.
- Exact password complexity rules are not specified in this input.
- No account-recovery/password-reset flow is specified, and email/SMTP is out of scope — recovery path is unresolved.
- Exact numeric value of the per-session document cap is not given in this input.
- Input implies an earlier version simulated uploads locally; the requirements do not state why/when that happened — flagged for traceability but not treated as a current conflict.
- This story implies a prior deployment lacked a running worker, leaving documents stuck in 'processing' — the requirements input does not state when/why that gap existed, only that it's being fixed.
- This is a verification/testing-oriented story defined at requirements time; no actual test results are included in this input — testing phase should confirm these outcomes once executed.

### Architecture

- Input does not map this architecture to specific requirement IDs (US-001..US-011); traceability from requirements to architecture elements is not explicit.
- Not explicitly linked to a specific requirement ID in the input.

### Development

- Plan input does not explicitly state which backlog items (US-xxx) were assigned to this sprint; mapping to EPIC-001/US-001-US-004 is a plausible inference only, not a stated fact.
- No development run data ties any delivered ticket to this sprint.
- Plan input does not explicitly state which backlog items were assigned to this sprint.
- Only US-014 and US-015 (from this likely range) have recorded development delivery; the rest have no dev status recorded.
- No development run record exists for US-001, US-002, US-003, or US-004 despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.
- No development run record exists for US-005 or US-006 despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.
- No development run record exists for US-007 or US-008 (or their tasks) despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.
- No development run record exists for US-009 or US-010 (or US-009's tasks) despite the dev run being marked completed; delivery status for this epic's stories is unconfirmed.
- No development run record exists for US-011 despite the dev run being marked completed; delivery status for this epic's story is unconfirmed.
- No development run record exists for US-012, US-013, or US-016 despite the overall dev run being marked 'completed' -- this is a discrepancy between claimed phase status and recorded ticket-level evidence and should be reconciled.
- US-014 and US-015 share the identical commit hash, which may indicate they were delivered together in one commit/PR; this is noted but not confirmed as intentional or erroneous by the input.
- Discrepancy: run status says 'completed' but 14 of 16 planned stories (US-001-US-013, US-016) have no delivery ticket in the input -- unclear whether they were delivered without being logged, descoped, or still pending. Needs reconciliation with the planning/dev team.
- No commit, PR, or code artifact references were provided for US-001 through US-013 or US-016.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date/timestamp provided.
- No record of who approved or triggered this deployment.
- No change-log or list of requirements/tickets included in version 34b8c5ab2f05 -- cannot link to US-001..US-016 without guessing.
- No rollback plan or previous version reference recorded.
- No confirmation of environment configuration (e.g., API keys for gemini-2.5-flash, gemini-embedding-001) or infrastructure details (database, vector store) used in this deployment.
- No post-deployment health check or smoke test results recorded.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
