# Rag_chatbot_gemini_v8 — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build a rag chatbot where user can upload there own documents and ask queries about them use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings and have chat history and sessions

**Documentation version:** v5
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 18 entries |
| [Development](development/README.md) | 11 entries |
| [Testing](testing/README.md) | 1 entry |
| [Deployment](deployment/README.md) | 3 entries |
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
| [Release notes](deployment/release-notes.md) | 1 release |
| [Traceability matrix](traceability-matrix.md) | 11 requirements |
| [Changelog](CHANGELOG.md) | 5 versions |
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

- No ticket delivery status reported for US-006 or US-007 despite the dev run being marked completed.
- No ticket delivery status reported for US-008 or its sub-tasks despite the dev run being marked completed.
- No ticket delivery status reported for US-009, US-010, or US-011 or any US-009 sub-tasks despite the dev run being marked completed.
- Confirm whether US-006 through US-011 and their sub-tasks were actually implemented, or whether the 'completed' run status is premature/inaccurate.
- No commit references available for Sprints 2-4 scope.

### Testing

- Testing phase has not started -- no test records available to document.

### Deployment

- No deployment date/timestamp provided.
- No record of who approved or triggered this deployment.
- No release notes or changelog describing what version 79cbc3012d52 contains relative to prior versions.
- No mapping given between this deployment and the requirement keys (US-001..US-011) it is meant to fulfill -- cannot confirm which features are included in this release.
- No environment details (e.g., staging vs production, infra provider specifics beyond the sslip.io/Amplify hosts).
- No rollback or monitoring plan recorded.
- No confirmation of which app features/screens are live at this URL versus still pending.
- No information on custom domain, TLS cert ownership, or CI/CD pipeline used to produce this deployment.
- No confirmation that backend endpoints (upload, query, chat history, sessions) are operational at this URL -- only the base host was given.
- No information on backend infrastructure (containerization, scaling, secrets management, or database connection for chat history/sessions).
- No security/compliance notes (e.g., TLS, auth) for this backend endpoint.

### Maintenance

- Maintenance phase has not started -- no post-deployment records available to document.
<!-- sdlc:auto:end open-gaps -->
