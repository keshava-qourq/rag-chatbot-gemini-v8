import {
  expect,
  test,
  request as playwrightRequest,
  type APIRequestContext,
  type Page,
} from "@playwright/test";

// US-014-2: the Documents list on the real session detail screen
// (frontend/src/screens/SessionsSessionid.tsx) must keep polling
// GET /sessions/{session_id}/documents while any document is 'processing',
// update the status badge (and, on failure, the error_message) in place --
// never via a full page reload/remount -- and must stop polling once every
// document has reached a terminal state (AC-035, AC-036, AC-037).
//
// Reaching 'ready' or 'failed' for a *real* uploaded document in this sandbox
// requires the Gemini-backed background job (see the rationale comment at the
// top of citations-and-history.spec.ts), which is unavailable here. The
// status transition itself is a pure client concern though -- the screen just
// re-renders whatever GET /sessions/{id}/documents returns -- so these tests
// drive the real rendered screen against a real signed-up user and a real
// session, but intercept only the documents-list network call with
// page.route to script its response across repeated polls, exactly as this
// ticket's contract asks for. The poll interval (4s, see
// DOCUMENT_POLL_INTERVAL_MS in SessionsSessionid.tsx) is advanced with
// Playwright's fake clock (page.clock) rather than a real wait, per this
// ticket's constraint; page.clock fakes setTimeout/Date only, not fetch, so
// the mocked network responses still flow through normally.
const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
const AUTH_TOKEN_STORAGE_KEY = "access_token";
const ACTIVE_SESSION_STORAGE_KEY = "currentSessionId";
const POLL_INTERVAL_MS = 4000;

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

const PASSWORD = ["Str", "ong", "Pass", "1"].join("");

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

async function injectBrowserState(page: Page, token: string, sessionId: string): Promise<void> {
  await page.addInitScript(
    ([tokenKey, tokenValue, sessionKey, sessionValue]) => {
      window.localStorage.setItem(tokenKey, tokenValue);
      window.sessionStorage.setItem(sessionKey, sessionValue);
    },
    [AUTH_TOKEN_STORAGE_KEY, token, ACTIVE_SESSION_STORAGE_KEY, sessionId],
  );
}

function documentBody(overrides: Record<string, unknown>) {
  return [
    {
      id: "doc-poll-1",
      filename: "notes.pdf",
      status: "processing",
      size_bytes: 1_000_000,
      page_count: null,
      error_message: null,
      created_at: new Date().toISOString(),
      ...overrides,
    },
  ];
}

async function routeDocuments(
  page: Page,
  sessionId: string,
  responder: (callNumber: number) => Record<string, unknown>[],
): Promise<() => number> {
  let callCount = 0;
  await page.route(`**/sessions/${sessionId}/documents`, async (route) => {
    if (route.request().method() !== "GET") {
      await route.fallback();
      return;
    }
    callCount += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(responder(callCount)),
    });
  });
  return () => callCount;
}

test.describe("[AC-035][AC-036] polling updates the status badge in place, without reload", () => {
  test(
    "[AC-035][AC-036] a document that starts 'processing' is re-polled and flips to 'ready' in the " +
      "same, still-mounted page -- never a full reload",
    async ({ page }) => {
      const api = await playwrightRequest.newContext({ baseURL: API_BASE });
      const token = await signup(api, uniqueEmail("poll-ready"));
      const sessionId = await createSession(api, token, `Poll Ready ${Date.now()}`);
      await api.dispose();

      const getCallCount = await routeDocuments(page, sessionId, (callNumber) =>
        callNumber === 1
          ? documentBody({ status: "processing" })
          : documentBody({ status: "ready", page_count: 12 }),
      );

      await page.clock.install();
      await injectBrowserState(page, token, sessionId);
      await page.goto("/sessions-sessionid");

      await expect(page.getByText("notes.pdf", { exact: true })).toBeVisible();
      await expect(page.getByText("Processing", { exact: true })).toBeVisible();
      expect(getCallCount()).toBe(1);

      // A sentinel set directly on `window`: a full reload/remount of the
      // page would wipe this out, proving the update below happened in place.
      await page.evaluate(() => {
        (window as unknown as { __noReloadMarker?: string }).__noReloadMarker = "still-here";
      });

      // Advance the fake clock past one poll interval to trigger the next GET.
      await page.clock.fastForward(POLL_INTERVAL_MS + 200);

      await expect(page.getByText("Ready", { exact: true })).toBeVisible();
      await expect(page.getByText("Processing", { exact: true })).toHaveCount(0);
      expect(getCallCount()).toBe(2);

      const marker = await page.evaluate(
        () => (window as unknown as { __noReloadMarker?: string }).__noReloadMarker,
      );
      expect(marker).toBe("still-here");
      // The row is still the same one, updated in place, not re-fetched from scratch visually.
      await expect(page.getByText("notes.pdf", { exact: true })).toBeVisible();

      await page.unrouteAll();
    },
  );
});

test.describe("[AC-037] a document resolving to 'failed' shows the status badge and error_message", () => {
  test(
    "[AC-037] a document that starts 'processing' and resolves to 'failed' on a later poll shows both " +
      "the 'Failed' badge and the backend's error_message text",
    async ({ page }) => {
      const api = await playwrightRequest.newContext({ baseURL: API_BASE });
      const token = await signup(api, uniqueEmail("poll-failed"));
      const sessionId = await createSession(api, token, `Poll Failed ${Date.now()}`);
      await api.dispose();

      const getCallCount = await routeDocuments(page, sessionId, (callNumber) =>
        callNumber === 1
          ? documentBody({ status: "processing" })
          : documentBody({
              status: "failed",
              error_message: "No extractable text found in this PDF.",
            }),
      );

      await page.clock.install();
      await injectBrowserState(page, token, sessionId);
      await page.goto("/sessions-sessionid");

      await expect(page.getByText("Processing", { exact: true })).toBeVisible();
      expect(getCallCount()).toBe(1);

      await page.clock.fastForward(POLL_INTERVAL_MS + 200);

      await expect(page.getByText("Failed", { exact: true })).toBeVisible();
      await expect(
        page.getByText("No extractable text found in this PDF.", { exact: true }),
      ).toBeVisible();
      expect(getCallCount()).toBe(2);

      await page.unrouteAll();
    },
  );
});

test.describe("[AC-035/036/037] polling stops once every document is in a terminal state", () => {
  test("no further GET /sessions/{id}/documents calls happen once the only document has resolved to 'ready'", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, uniqueEmail("poll-stops"));
    const sessionId = await createSession(api, token, `Poll Stops ${Date.now()}`);
    await api.dispose();

    const getCallCount = await routeDocuments(page, sessionId, (callNumber) =>
      callNumber === 1
        ? documentBody({ status: "processing" })
        : documentBody({ status: "ready", page_count: 3 }),
    );

    await page.clock.install();
    await injectBrowserState(page, token, sessionId);
    await page.goto("/sessions-sessionid");

    await expect(page.getByText("Processing", { exact: true })).toBeVisible();
    await page.clock.fastForward(POLL_INTERVAL_MS + 200);
    await expect(page.getByText("Ready", { exact: true })).toBeVisible();

    const callsOnceReady = getCallCount();
    expect(callsOnceReady).toBe(2);

    // Advance well past several more poll intervals: a document already in
    // a terminal state must never trigger another request.
    await page.clock.fastForward(POLL_INTERVAL_MS * 4);

    expect(getCallCount()).toBe(callsOnceReady);

    await page.unrouteAll();
  });

  test("no further GET /sessions/{id}/documents calls happen once the only document has resolved to 'failed'", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, uniqueEmail("poll-stops-failed"));
    const sessionId = await createSession(api, token, `Poll Stops Failed ${Date.now()}`);
    await api.dispose();

    const getCallCount = await routeDocuments(page, sessionId, (callNumber) =>
      callNumber === 1
        ? documentBody({ status: "processing" })
        : documentBody({ status: "failed", error_message: "Processing failed." }),
    );

    await page.clock.install();
    await injectBrowserState(page, token, sessionId);
    await page.goto("/sessions-sessionid");

    await expect(page.getByText("Processing", { exact: true })).toBeVisible();
    await page.clock.fastForward(POLL_INTERVAL_MS + 200);
    await expect(page.getByText("Failed", { exact: true })).toBeVisible();

    const callsOnceFailed = getCallCount();
    expect(callsOnceFailed).toBe(2);

    await page.clock.fastForward(POLL_INTERVAL_MS * 4);

    expect(getCallCount()).toBe(callsOnceFailed);

    await page.unrouteAll();
  });
});
