# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v28
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v2 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 16 entries |
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
| [Release notes](deployment/release-notes.md) | 12 releases |
| [Traceability matrix](traceability-matrix.md) | 16 requirements |
| [Changelog](CHANGELOG.md) | 28 versions |
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

- No explicit mapping provided between backlog items and the sprint in which each was actually completed.
- No explicit list of which backlog items (e.g. US-001..US-005) were assigned to or completed in this sprint was given.
- No explicit list of which backlog items were assigned to or completed in this sprint was given.
- No per-ticket completion/delivery status given for US-001 through US-004; only the overall dev run is marked 'completed'.
- No per-ticket completion/delivery status given for US-005 or US-006.
- Task-level (T1-T4) completion status not reported individually; only the aggregate dev run status of 'completed' is available.
- Task-level completion status not reported individually for US-009's sub-tasks or for US-010.
- No per-ticket completion/delivery status given for US-011.
- Epic grouping not explicit in input (inferred from functional relationship to US-007).
- No individual completion/delivery status reported for this ticket.
- Epic grouping not explicit in input (inferred).
- This is a deployment/runtime configuration concern; no confirmation of actual deployed execution is available in this development-phase input (belongs to deployment phase evidence).
- Discrepancy: the run is marked 'completed' at the aggregate level, but no explicit status or commit evidence was provided for US-001 through US-015 individually -- their actual implementation/delivery state cannot be confirmed from this input.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date provided.
- No record of who approved or executed the deployment.
- No infrastructure, environment, or configuration details given (e.g. hosting provider specifics, scaling, secrets management).
- No rollback or incident plan recorded.
- No mapping of which requirements/features are confirmed live versus pending verification post-deployment.
- No test or QA sign-off referenced prior to this deployment.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
