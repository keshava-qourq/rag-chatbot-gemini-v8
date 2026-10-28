# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v29
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v2 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 8 entries |
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
| [Changelog](CHANGELOG.md) | 29 versions |
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

- No approver name or approval date recorded for plan v2.
- No explicit mapping in the input of which sprint each individual story (e.g. US-012-US-016) was executed in; sprint-to-item assignment above is inferred only where sprint goal text clearly matches the epic/story content.
- No ticket-level delivery status, commit, or completion date provided for US-001 through US-004 despite the overall run being marked 'completed'.
- No ticket-level delivery status or commit provided for US-005 or US-006.
- No ticket-level delivery status or commit provided for US-007, US-008, or any of their sub-tasks.
- No ticket-level delivery status or commit provided for US-009, US-010, or US-009's sub-tasks.
- No ticket-level delivery status or commit provided for US-011.
- No ticket-level delivery status or commit provided for US-012, US-013, US-014, or US-015, even though US-016 (which functionally depends on their completion for E2E verification to pass) is marked delivered -- this is a discrepancy worth confirming.
- Run-level status 'completed' is not individually corroborated for the other 24 plan items (epics, stories, and tasks); only US-016 has a ticket record with status and commit. Recommend confirming whether the remaining items were in fact completed or if ticket records are simply missing from this input.

### Testing

- No ticket reference was provided for this check run, so it cannot be traced to a specific requirement, user story, or development ticket.
- No breakdown of the 4 individual checks (names, scope, what each verified) was provided -- only an aggregate pass count.
- No test plan, test case list, or formal QA sign-off was documented for this phase.
- Coverage of the known requirements (US-001 through US-016) against this check run is unknown; none can be confidently linked as related_ids.

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
