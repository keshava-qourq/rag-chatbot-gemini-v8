import {
  expect,
  test,
  request as playwrightRequest,
  type APIRequestContext,
  type Page,
} from "@playwright/test";

// US-010-2: citation display (AC-027/AC-028/NFR-014) and session-scoped chat
// history (AC-029/AC-030) on the real, wired SessionsSessionid screen.
//
// Every one of these criteria requires at least one *successful* answer from
// POST /sessions/{session_id}/messages, which in turn requires a document
// that has actually reached status "ready". Reaching "ready" requires the
// background job (app.jobs.process_document) to call gemini-embedding-001,
// and answering requires app.rag to call gemini-2.5-flash. Gemini is not one
// of this project's provisioned services (see ENVIRONMENT.md and the
// GEMINI_API_KEY comment in backend/app/config.py) and no working credential
// is present in this sandbox -- confirmed live: uploading a PDF through the
// real /sessions/{id}/documents route and letting the real RQ worker process
// it leaves the document permanently in status "failed" with
// error_message "Embeddings could not be generated because the Gemini API is
// not configured.", never "ready". Since every one of AC-027/028/029/030
// requires a message row that only POST /sessions/{id}/messages can create,
// and that route 422s with "no ready documents" whenever none exists (see
// frontend/e2e/ask-question.spec.ts's AC-024 tests), there is no way to
// produce the fixture these criteria need through the real, unstubbed API in
// this environment -- and per this ticket's constraints, the backend must
// not be stubbed.
//
// This mirrors the precedent already established in
// frontend/e2e/ask-question.spec.ts for AC-022/023/025/026, which hit the
// identical blocker and skip with the same rationale. As there, the setup
// below is driven for real up to the point that the real backend/real Gemini
// boundary is reached, and the UI-rendering behaviour that is independent of
// that boundary (how the screen renders whatever MessageOut[] the API
// returns) is fully covered elsewhere with real DOM rendering and only
// apiFetch mocked, in frontend/src/screens/SessionsSessionid.test.tsx:
//   - "[AC-029] loads history on mount and renders prior Q/A pairs in
//     chronological order"
//   - "[AC-027] renders one citation per source chunk naming filename and
//     page number"
//   - "[AC-028/NFR-014] names the source document even when page_number is
//     null"
// and the server-side correctness of citation attachment, page-number
// nullability, chronological ordering and cross-session isolation is proven
// against the real Postgres+pgvector database (with only the google-genai
// client faked, never the HTTP boundary) in
// backend/tests/integration/test_messages.py:
//   - test_ac022_question_is_embedded_retrieved_and_answered_via_gemini_flash
//     (citation document_id/filename/page_number)
//   - test_ac029_message_history_is_returned_in_chronological_order_across_requests
//   - test_ac030_messages_from_another_session_are_never_included
//
// NFR-016 (tens-to-low-hundreds concurrent users) is a load-testing concern,
// not something a Playwright assertion can verify -- not covered here, as
// already noted in session-isolation.spec.ts.

const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
const AUTH_TOKEN_STORAGE_KEY = "access_token";

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

const PASSWORD = "StrongPass1";

async function signup(api: APIRequestContext, email: string): Promise<string> {
  const response = await api.post("/auth/signup", { data: { email, password: PASSWORD } });
  expect(response.ok(), `signup failed: ${await response.text()}`).toBeTruthy();
  return (await response.json()).access_token as string;
}

async function createSession(api: APIRequestContext, token: string, name: string): Promise<string> {
  const response = await api.post("/sessions", {
    headers: { Authorization: `Bearer ${token}` },
    data: { name },
  });
  expect(response.ok(), `create session failed: ${await response.text()}`).toBeTruthy();
  return (await response.json()).id as string;
}

async function uploadDocument(
  api: APIRequestContext,
  token: string,
  sessionId: string,
  filename: string,
): Promise<void> {
  const response = await api.post(`/sessions/${sessionId}/documents`, {
    headers: { Authorization: `Bearer ${token}` },
    multipart: {
      file: {
        name: filename,
        mimeType: "application/pdf",
        buffer: Buffer.from("%PDF-1.4 fake pdf content for e2e test"),
      },
    },
  });
  expect(response.ok(), `upload failed: ${await response.text()}`).toBeTruthy();
}

async function injectToken(page: Page, token: string): Promise<void> {
  await page.addInitScript(
    ([key, value]) => window.localStorage.setItem(key, value),
    [AUTH_TOKEN_STORAGE_KEY, token],
  );
}

test.describe("[AC-027][AC-028/NFR-014] citation badges on the real session detail screen", () => {
  test(
    "[AC-027][AC-028/NFR-014] rendering an answer's citation badge (filename + page, " +
      "or filename alone when no page) requires a real 'ready' document and a real " +
      "Gemini-generated answer -- unavailable in this sandbox, see rationale above",
    async ({ page }) => {
      const api = await playwrightRequest.newContext({ baseURL: API_BASE });
      const token = await signup(api, uniqueEmail("citation-ui"));
      const sessionId = await createSession(api, token, `Citations ${Date.now()}`);
      await uploadDocument(api, token, sessionId, `doc-${Date.now()}.pdf`);

      await injectToken(page, token);
      await page.goto("/sessions");
      // The real setup (signup, login, session, upload) all genuinely happened
      // against the live API; what cannot be driven further without Gemini is
      // asking a question and getting back a real, cited answer.
      await api.dispose();

      test.skip(
        true,
        "Document processing requires gemini-embedding-001 to reach status " +
          "'ready', and answering requires gemini-2.5-flash -- neither is " +
          "available in this sandbox. See the rationale comment at the top of " +
          "this file for the equivalent coverage that does exist.",
      );
    },
  );
});

test.describe("[AC-029] chat history survives a reload in chronological order", () => {
  test(
    "[AC-029] reloading the session detail page after asking several real " +
      "questions shows them in order -- requires real generated answers, " +
      "unavailable in this sandbox, see rationale above",
    async ({ page }) => {
      const api = await playwrightRequest.newContext({ baseURL: API_BASE });
      const token = await signup(api, uniqueEmail("history-order"));
      await createSession(api, token, `History order ${Date.now()}`);
      await injectToken(page, token);
      await page.goto("/sessions");
      await api.dispose();

      test.skip(
        true,
        "Every message this screen renders comes from a prior POST " +
          "/sessions/{id}/messages call, which 422s without a 'ready' " +
          "document (AC-024, already covered by ask-question.spec.ts) and " +
          "cannot reach 'ready' without Gemini in this sandbox. See the " +
          "rationale comment at the top of this file.",
      );
    },
  );
});

test.describe("[AC-030] a second session's history never shows a message from the first", () => {
  test(
    "[AC-030] two sessions with real messages never leak into each other's " +
      "history on this screen -- requires real generated answers, " +
      "unavailable in this sandbox, see rationale above",
    async ({ page }) => {
      const api = await playwrightRequest.newContext({ baseURL: API_BASE });
      const token = await signup(api, uniqueEmail("history-isolation"));
      await createSession(api, token, `Isolation A ${Date.now()}`);
      await createSession(api, token, `Isolation B ${Date.now()}`);
      await injectToken(page, token);
      await page.goto("/sessions");
      await api.dispose();

      test.skip(
        true,
        "Proving isolation needs at least one real message per session, which " +
          "needs a real generated answer -- unavailable in this sandbox. " +
          "Server-side isolation is already proven against the real database " +
          "in backend/tests/integration/test_messages.py's " +
          "test_ac030_messages_from_another_session_are_never_included. See " +
          "the rationale comment at the top of this file.",
      );
    },
  );

  test(
    "[AC-030] (real, executable today) two sessions with zero messages each " +
      "both show the empty history state on reload -- never a message that " +
      "does not belong to them",
    async ({ page }) => {
      const api = await playwrightRequest.newContext({ baseURL: API_BASE });
      const token = await signup(api, uniqueEmail("history-isolation-empty"));
      const sessionAName = `Empty A ${Date.now()}`;
      const sessionBName = `Empty B ${Date.now()}`;
      await createSession(api, token, sessionAName);
      await createSession(api, token, sessionBName);

      await injectToken(page, token);

      await page.goto("/sessions");
      await page.getByRole("button", { name: new RegExp(`Open session ${sessionAName}`) }).click();
      await expect(page.getByText(/No questions asked yet/i)).toBeVisible();

      await page.goto("/sessions");
      await page.getByRole("button", { name: new RegExp(`Open session ${sessionBName}`) }).click();
      await expect(page.getByText(/No questions asked yet/i)).toBeVisible();

      await api.dispose();
    },
  );
});
