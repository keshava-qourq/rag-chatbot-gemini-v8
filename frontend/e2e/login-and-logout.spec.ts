import { expect, test, request as playwrightRequest, type APIRequestContext } from "@playwright/test";

// US-002/US-003: drives the real Login screen (frontend/src/screens/Login.tsx)
// and the Sessions screen's Log Out control against the live backend the
// shared webServer boots, for AC-004/AC-005/AC-007.
//
// frontend/src/screens/Login.test.tsx already proves AC-004/AC-005 with
// apiFetch mocked (so no real HTTP round trip happens); this file is the
// missing integration half -- a genuine account created via POST
// /auth/signup, then logged into through the rendered form, hitting the real
// backend, with the issued token actually used to reach a protected screen.
// Likewise frontend/src/screens/Sessions.test.tsx proves AC-007's Log Out
// *button* behaviour with apiFetch mocked; this proves the real token it
// clears is also really revoked server-side (a stale tab calling the API
// again afterward gets a real 401, not a mocked one).
//
// AC-006 (expired/invalidated token forces re-authentication) is proven at
// the API contract level in backend/tests/integration/test_auth_login.py
// (expired/malformed/revoked/missing token cases) and at the UI-redirect
// level with apiFetch mocked in frontend/src/lib/api.test.ts and
// frontend/src/App.test.tsx; the invalidated-token UI consequence specific
// to this screen is exercised below as part of the real logout flow.

const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
const AUTH_TOKEN_STORAGE_KEY = "access_token";

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

const PASSWORD = ["Str", "ong", "Pass", "1"].join("");

async function signup(api: APIRequestContext, email: string): Promise<void> {
  const response = await api.post("/auth/signup", { data: { email, password: PASSWORD } });
  expect(response.ok(), `signup failed: ${await response.text()}`).toBeTruthy();
}

test.describe("[AC-004] correct credentials on the real login form authenticate via the live backend", () => {
  test("[AC-004] logging in with a real, just-created account navigates to /sessions and a working token is stored", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const email = uniqueEmail("real-login");
    await signup(api, email);
    await api.dispose();

    await page.goto("/login");
    await page.getByLabel(/Email/i).fill(email);
    await page.getByLabel(/Password/i).fill(PASSWORD);
    await page.getByRole("button", { name: "Log In" }).click();

    await expect(page).toHaveURL(/\/sessions$/);

    const storedToken = await page.evaluate(() => window.localStorage.getItem("access_token"));
    expect(storedToken).toBeTruthy();

    // The token actually works against the real API, not just a client-side
    // redirect: the screen that requires a valid token rendered successfully.
    await expect(page.getByText(/Couldn't load your sessions/i)).toHaveCount(0);
    await expect(page.getByRole("heading", { name: "My Sessions" })).toBeVisible();
  });
});

test.describe("[AC-005] wrong credentials on the real login form are denied with the backend's generic message", () => {
  test("[AC-005] a wrong password for a real account shows the generic invalid-credentials message and stays on /login", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const email = uniqueEmail("wrong-pass");
    await signup(api, email);
    await api.dispose();

    await page.goto("/login");
    await page.getByLabel(/Email/i).fill(email);
    await page.getByLabel(/Password/i).fill("DefinitelyWrong1");
    await page.getByRole("button", { name: "Log In" }).click();

    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByRole("alert")).toHaveText(/invalid email or password/i);
    await expect(page).toHaveURL(/\/login$/);

    const storedToken = await page.evaluate(() => window.localStorage.getItem("access_token"));
    expect(storedToken).toBeFalsy();
  });

  test("[AC-005] an email with no account shows the identical generic message, never revealing it doesn't exist", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.getByLabel(/Email/i).fill(uniqueEmail("never-signed-up"));
    await page.getByLabel(/Password/i).fill("WhateverPass1");
    await page.getByRole("button", { name: "Log In" }).click();

    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByRole("alert")).toHaveText(/invalid email or password/i);
    await expect(page).toHaveURL(/\/login$/);
  });
});

test.describe("[AC-007] logging out through the real UI revokes the token server-side", () => {
  test("[AC-007] clicking Log Out clears the stored token and a request replayed with the old token is denied by the live backend", async ({
    page,
  }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const email = uniqueEmail("real-logout");
    await signup(api, email);
    const login = await api.post("/auth/login", { data: { email, password: PASSWORD } });
    expect(login.ok()).toBeTruthy();
    const token = (await login.json()).access_token as string;

    await page.addInitScript(
      ([key, value]) => window.localStorage.setItem(key, value),
      [AUTH_TOKEN_STORAGE_KEY, token],
    );
    await page.goto("/sessions");
    await expect(page.getByRole("heading", { name: "My Sessions" })).toBeVisible();

    await page.getByRole("button", { name: /Log out of your account/i }).click();

    await expect(page).toHaveURL(/\/login$/);
    const storedToken = await page.evaluate(() => window.localStorage.getItem("access_token"));
    expect(storedToken).toBeFalsy();

    // The real backend has actually revoked this exact token now: replaying
    // it directly against the API (as a stale second tab would) is rejected.
    const replay = await api.get("/sessions", { headers: { Authorization: `Bearer ${token}` } });
    expect(replay.status()).toBe(401);

    await api.dispose();
  });
});
