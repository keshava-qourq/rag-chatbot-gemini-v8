# Deployment

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### DEPLOY-79cbc30 · approved · source: deployment:79cbc3012d52

The Rag_chatbot_gemini_v8 application is deployed and live under version 79cbc3012d52. A frontend and backend endpoint are both publicly reachable.

Deployment status: live. Version/build identifier: 79cbc3012d52. Frontend hosted at https://p5b327a9dbdb3.d3j61xaup4zgrx.amplifyapp.com. Backend hosted at https://35-155-27-11.sslip.io/apps/5b327a9dbdb3/. No deployment date, deploying agent/human, approval record, or release notes were included in the input.

- ⚠ No deployment date/timestamp provided.
- ⚠ No record of who approved or triggered this deployment.
- ⚠ No release notes or changelog describing what version 79cbc3012d52 contains relative to prior versions.
- ⚠ No mapping given between this deployment and the requirement keys (US-001..US-011) it is meant to fulfill -- cannot confirm which features are included in this release.
- ⚠ No environment details (e.g., staging vs production, infra provider specifics beyond the sslip.io/Amplify hosts).
- ⚠ No rollback or monitoring plan recorded.

### DEPLOY-FRONTEND-URL · approved · source: deployment:79cbc3012d52

Frontend of the chatbot is hosted via AWS Amplify at a publicly accessible URL.

Frontend URL: https://p5b327a9dbdb3.d3j61xaup4zgrx.amplifyapp.com. No further detail on build pipeline, environment variables, or CDN/caching configuration was provided.

- ⚠ No confirmation of which app features/screens are live at this URL versus still pending.
- ⚠ No information on custom domain, TLS cert ownership, or CI/CD pipeline used to produce this deployment.

### DEPLOY-BACKEND-URL · approved · source: deployment:79cbc3012d52

Backend API for the chatbot is hosted at a sslip.io-based URL, presumably serving the RAG/chat/session endpoints.

Backend URL: https://35-155-27-11.sslip.io/apps/5b327a9dbdb3/. No details were given on backend framework, scaling configuration, database/vector-store connectivity, or API documentation.

- ⚠ No confirmation that backend endpoints (upload, query, chat history, sessions) are operational at this URL -- only the base host was given.
- ⚠ No information on backend infrastructure (containerization, scaling, secrets management, or database connection for chat history/sessions).
- ⚠ No security/compliance notes (e.g., TLS, auth) for this backend endpoint.
<!-- sdlc:auto:end narrative -->
