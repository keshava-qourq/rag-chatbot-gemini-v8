# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v24
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v2 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 15 entries |
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
| [Release notes](deployment/release-notes.md) | 10 releases |
| [Traceability matrix](traceability-matrix.md) | 16 requirements |
| [Changelog](CHANGELOG.md) | 24 versions |
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

- No explicit item-to-sprint assignment given in input; alignment with EPIC-001/US-005 is inferred from goal wording only.
- No development run confirmation of completion for this sprint's likely scope.
- No explicit item-to-sprint assignment given in input.
- Items US-012 through US-016 appear in the backlog after this sprint's listed goal but are not explicitly assigned to any sprint.
- No development run status recorded for US-001 through US-004 in this input.
- No development run status recorded for US-005 or US-006 in this input.
- No development run status recorded for US-007, US-008, or their subtasks in this input.
- No development run status recorded for US-009, US-010, or US-009's subtasks in this input.
- No development run status recorded for US-011 in this input.
- Not listed in the development run's delivered tickets; completion status unconfirmed.
- Discrepancy: overall run status is 'completed' but 14 of 16 planned stories (US-001–US-011, US-014–US-016) have no ticket-level delivery record in this input -- needs human verification of whether this is an incomplete report or an actual scope gap.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date recorded.
- No indication of which requirements/user stories (e.g. US-001..US-016) are included in this release version.
- No record of who approved or triggered this deployment.
- No rollback plan, release notes, or changelog provided.
- No confirmation of environment type (staging vs. production) beyond the generic 'live' status.
- Backend URL uses an IP-based sslip.io domain with no TLS/cert details noted.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
