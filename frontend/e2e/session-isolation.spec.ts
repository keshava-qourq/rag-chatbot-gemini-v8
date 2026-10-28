import {
  expect,
  test,
  request as playwrightRequest,
  type APIRequestContext,
} from "@playwright/test";

// The backend the webServer block in playwright.config.ts boots independently of the
// frontend preview server that `baseURL` points at, so setup calls go straight to it.
const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";

// frontend/src/lib/auth.ts does not exist in the repository yet (US-006-2 is not yet
// built), so this is the key the contract describes it reading from localStorage. If the
// implementation lands under a different key, update this constant to match -- see the
// `risk` note in this ticket's QA report.
const AUTH_TOKEN_STORAGE_KEY = "access_token";

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

const PASSWORD = "Correcthorse9!";

async function signup(api: APIRequestContext, email: string): Promise<string> {
  const response = await api.post("/auth/signup", {
    data: { email, password: PASSWORD },
  });
  expect(response.ok(), `signup failed for ${email}: ${await response.text()}`).toBeTruthy();
  const body = await response.json();
  return body.access_token as string;
}

async function login(api: APIRequestContext, email: string): Promise<string> {
  const response = await api.post("/auth/login", {
    data: { email, password: PASSWORD },
  });
  expect(response.ok(), `login failed for ${email}: ${await response.text()}`).toBeTruthy();
  const body = await response.json();
  return body.access_token as string;
}

async function createSession(api: APIRequestContext, token: string, name: string): Promise<string> {
  const response = await api.post("/sessions", {
    headers: { Authorization: `Bearer ${token}` },
    data: { name },
  });
  expect(response.ok(), `create session failed for ${name}: ${await response.text()}`).toBeTruthy();
  const body = await response.json();
  return body.id as string;
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
  expect(response.ok(), `upload failed for ${filename}: ${await response.text()}`).toBeTruthy();
}

async function injectToken(page: import("@playwright/test").Page, token: string) {
  await page.addInitScript(
    ([key, value]) => {
      window.localStorage.setItem(key, value);
    },
    [AUTH_TOKEN_STORAGE_KEY, token],
  );
}

test.describe("[AC-011] a user sees only their own sessions", () => {
  test("[AC-011] signup+login both users via the real API, then user A's session list never shows user B's session name", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });

    const emailA = uniqueEmail("user-a");
    const emailB = uniqueEmail("user-b");
    await signup(api, emailA);
    await signup(api, emailB);
    // Round-trip through /auth/login too, per the acceptance criterion, rather than
    // reusing the token /auth/signup already returned.
    const tokenA = await login(api, emailA);
    const tokenB = await login(api, emailB);

    const sessionAName = `User A Session ${Date.now()}`;
    const sessionBName = `User B Session ${Date.now()}`;

    await createSession(api, tokenA, sessionAName);
    await createSession(api, tokenB, sessionBName);

    await injectToken(page, tokenA);
    await page.goto("/sessions");

    await expect(page.getByText(sessionAName, { exact: true })).toBeVisible();
    await expect(page.getByText(sessionBName, { exact: true })).toHaveCount(0);

    await api.dispose();
  });
});

test.describe("[AC-012] a session's documents table shows only that session's documents", () => {
  test("[AC-012] opening each of two sessions in turn shows only its own documents", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });

    const email = uniqueEmail("doc-owner");
    await signup(api, email);
    const token = await login(api, email);

    const sessionOneName = `Session One ${Date.now()}`;
    const sessionTwoName = `Session Two ${Date.now()}`;
    const sessionOneId = await createSession(api, token, sessionOneName);
    const sessionTwoId = await createSession(api, token, sessionTwoName);

    const docOneName = `one-${Date.now()}.pdf`;
    const docTwoName = `two-${Date.now()}.pdf`;

    await uploadDocument(api, token, sessionOneId, docOneName);
    await uploadDocument(api, token, sessionTwoId, docTwoName);

    await injectToken(page, token);

    // Navigate via the real UI flow (open the row for the named session from the
    // sessions list) rather than guessing the session detail route's URL shape.
    await page.goto("/sessions");
    await page.getByRole("button", { name: new RegExp(`Open session ${sessionOneName}`) }).click();
    await expect(page.getByText(docOneName, { exact: true })).toBeVisible();
    await expect(page.getByText(docTwoName, { exact: true })).toHaveCount(0);

    await page.goto("/sessions");
    await page.getByRole("button", { name: new RegExp(`Open session ${sessionTwoName}`) }).click();
    await expect(page.getByText(docTwoName, { exact: true })).toBeVisible();
    await expect(page.getByText(docOneName, { exact: true })).toHaveCount(0);

    await api.dispose();
  });
});

// NFR-016 (tens to low hundreds of concurrent users) is a scalability/load-testing
// concern, not something a Playwright e2e assertion can verify meaningfully; it needs a
// load-test tool (e.g. k6/Locust) against a deployed environment. Not covered here --
// see the `risk` note in this ticket's QA report instead of a fake pass/fail here.
