import {
  expect,
  test,
  request as playwrightRequest,
  type APIRequestContext,
  type Page,
} from "@playwright/test";

// US-004: private, isolated workspace per user (AC-008, AC-009, NFR-005).
//
// session-isolation.spec.ts already proves AC-008's *listing* half for
// sessions and documents through the real UI for two distinct users. What it
// does not reach is AC-009 -- a direct attempt to fetch another user's
// session/document/message by ID must be denied with an authorization error,
// never the data -- across every scoped route, and the UI consequence of that
// denial on the session detail screen (which never gets the session id from
// the URL, only from sessionStorage, so "direct access" here is a user or a
// script setting that key to an id they do not own and opening the screen).
const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
const AUTH_TOKEN_STORAGE_KEY = "access_token";
const ACTIVE_SESSION_STORAGE_KEY = "currentSessionId";

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

async function injectBrowserState(
  page: Page,
  token: string,
  sessionId?: string,
): Promise<void> {
  await page.addInitScript(
    ([tokenKey, tokenValue, sessionKey, sessionValue]) => {
      window.localStorage.setItem(tokenKey, tokenValue);
      if (sessionValue) {
        window.sessionStorage.setItem(sessionKey, sessionValue);
      }
    },
    [AUTH_TOKEN_STORAGE_KEY, token, ACTIVE_SESSION_STORAGE_KEY, sessionId ?? ""],
  );
}

test.describe("[AC-009] direct API access to another user's resources by ID is denied", () => {
  test("[AC-009] GET /sessions/{id} for a session owned by someone else returns an authorization error, not the session", async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const tokenB = await signup(api, uniqueEmail("intruder-b"));
    const secretName = `A's private session ${Date.now()}`;
    const sessionId = await createSession(api, tokenA, secretName);

    const response = await api.get(`/sessions/${sessionId}`, {
      headers: { Authorization: `Bearer ${tokenB}` },
    });

    expect([403, 404]).toContain(response.status());
    const bodyText = await response.text();
    expect(bodyText).not.toContain(secretName);

    await api.dispose();
  });

  test("[AC-009] GET /sessions/{id}/documents for a session owned by someone else returns an authorization error, not the documents", async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const tokenB = await signup(api, uniqueEmail("intruder-b"));
    const sessionId = await createSession(api, tokenA, `Session ${Date.now()}`);

    const docName = `confidential-${Date.now()}.pdf`;
    const upload = await api.post(`/sessions/${sessionId}/documents`, {
      headers: { Authorization: `Bearer ${tokenA}` },
      multipart: {
        file: {
          name: docName,
          mimeType: "application/pdf",
          buffer: Buffer.from("%PDF-1.4 fake pdf content for e2e test"),
        },
      },
    });
    expect(upload.ok()).toBeTruthy();

    const response = await api.get(`/sessions/${sessionId}/documents`, {
      headers: { Authorization: `Bearer ${tokenB}` },
    });

    expect([403, 404]).toContain(response.status());
    const bodyText = await response.text();
    expect(bodyText).not.toContain(docName);

    await api.dispose();
  });

  test("[AC-009] POST /sessions/{id}/documents into a session owned by someone else is denied, and nothing is written", async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const tokenB = await signup(api, uniqueEmail("intruder-b"));
    const sessionId = await createSession(api, tokenA, `Session ${Date.now()}`);

    const response = await api.post(`/sessions/${sessionId}/documents`, {
      headers: { Authorization: `Bearer ${tokenB}` },
      multipart: {
        file: {
          name: "intruder-upload.pdf",
          mimeType: "application/pdf",
          buffer: Buffer.from("%PDF-1.4 fake pdf content for e2e test"),
        },
      },
    });

    expect([403, 404]).toContain(response.status());

    // The owner's session must come back with no document from the denied attempt.
    const ownerView = await api.get(`/sessions/${sessionId}/documents`, {
      headers: { Authorization: `Bearer ${tokenA}` },
    });
    expect(ownerView.ok()).toBeTruthy();
    expect(await ownerView.json()).toEqual([]);

    await api.dispose();
  });

  test("[AC-009] GET /sessions/{id}/messages for a session owned by someone else returns an authorization error, not the messages", async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const tokenB = await signup(api, uniqueEmail("intruder-b"));
    const sessionId = await createSession(api, tokenA, `Session ${Date.now()}`);

    const response = await api.get(`/sessions/${sessionId}/messages`, {
      headers: { Authorization: `Bearer ${tokenB}` },
    });

    expect([403, 404]).toContain(response.status());
  });

  test("[AC-009] POST /sessions/{id}/messages into a session owned by someone else is denied", async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const tokenB = await signup(api, uniqueEmail("intruder-b"));
    const sessionId = await createSession(api, tokenA, `Session ${Date.now()}`);

    const response = await api.post(`/sessions/${sessionId}/messages`, {
      headers: { Authorization: `Bearer ${tokenB}` },
      data: { question: "Can I read A's documents?" },
    });

    expect([403, 404]).toContain(response.status());

    // No message leaked into the owner's history as a side effect either.
    const ownerHistory = await api.get(`/sessions/${sessionId}/messages`, {
      headers: { Authorization: `Bearer ${tokenA}` },
    });
    expect(ownerHistory.ok()).toBeTruthy();
    expect(await ownerHistory.json()).toEqual([]);

    await api.dispose();
  });

  test("[AC-009] a request with no token at all is rejected the same way (401), never falling through to someone's data", async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const sessionId = await createSession(api, tokenA, `Session ${Date.now()}`);

    const response = await api.get(`/sessions/${sessionId}`);

    expect(response.status()).toBe(401);

    await api.dispose();
  });
});

test.describe("[AC-009] the UI never shows another user's session when pointed at its id", () => {
  test("[AC-009] opening the session detail screen with another user's session id shows an error state, not that user's session history", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });

    const tokenA = await signup(api, uniqueEmail("owner-a"));
    const tokenB = await signup(api, uniqueEmail("viewer-b"));
    const secretSessionName = `Confidential session ${Date.now()}`;
    const sessionAId = await createSession(api, tokenA, secretSessionName);

    // The session detail screen reads the id to open from sessionStorage, not
    // the URL (see Sessions.tsx/SessionsSessionid.tsx) -- this is the direct
    // "URL or API call" analogue for this screen: user B is logged in as
    // themself, but the active-session key is set to a session they do not
    // own, exactly as it would be if they guessed or replayed someone else's id.
    await injectBrowserState(page, tokenB, sessionAId);
    await page.goto("/sessions-sessionid");

    // The screen must surface the denial, not user A's conversation history.
    await expect(page.getByText(/Couldn't load the conversation history/i)).toBeVisible();
    await expect(page.getByText(secretSessionName)).toHaveCount(0);

    await api.dispose();
  });
});
