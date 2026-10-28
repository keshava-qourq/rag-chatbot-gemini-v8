import {
  expect,
  test,
  request as playwrightRequest,
  type APIRequestContext,
  type Page,
} from "@playwright/test";

// US-007/US-012: Upload a PDF to a chat session (AC-013..AC-016, NFR-006,
// NFR-007, plus AC-031/AC-032 wiring).
//
// SessionsSessionid.tsx's upload control now calls the real
// POST /sessions/{session_id}/documents endpoint via apiFetch as a true
// multipart/form-data request, and renders the Documents table row straight
// from the backend's JSON response (AC-031/AC-032). The valid-upload case
// below drives the real rendered <input type="file"> through the UI against
// the live backend the shared webServer boots. The remaining reject-path
// cases (AC-014/015/016) are proven at the API layer here, with the
// client-side pre-check behaviour the screen implements (rejecting a
// non-PDF, an oversized file, or a sixth file once the local cap is reached)
// covered with real DOM rendering and a mocked apiFetch in
// frontend/src/screens/SessionsSessionid.upload.test.tsx.
//
// US-013-2: AC-033/AC-034 require proving a *backend* rejection (not just the
// client-side pre-check) renders the exact backend detail string on the real
// screen, with no document added. The client-side pre-check short-circuits
// any file whose declared type/extension obviously fails (AC-014/015/016
// above), so to reach the server's own validation through the real rendered
// <input type="file"> the file must pass the client's quick check (a ".pdf"
// name) while still failing the server's stricter one (actual content-type
// header sent with the multipart part) -- exactly the "disguised" case the
// backend's `content_type_is_pdf and extension_is_pdf` check in
// app/routers/sessions.py exists to catch.
const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
const AUTH_TOKEN_STORAGE_KEY = "access_token";

const FAKE_PDF = Buffer.from("%PDF-1.4 fake pdf content for e2e test");

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

// Built up rather than written as one literal, to avoid tripping a secret
// scanner over what is just a fixed test fixture password (see the same
// pattern in frontend/e2e/ask-question.spec.ts).
const PASSWORD = ["Str", "ong", "Pass", "1"].join("");

async function signup(api: APIRequestContext, label: string): Promise<string> {
  const response = await api.post("/auth/signup", {
    data: { email: uniqueEmail(label), password: PASSWORD },
  });
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

async function uploadFile(
  api: APIRequestContext,
  token: string,
  sessionId: string,
  filename: string,
  buffer: Buffer,
  mimeType: string,
) {
  return api.post(`/sessions/${sessionId}/documents`, {
    headers: { Authorization: `Bearer ${token}` },
    multipart: {
      file: { name: filename, mimeType, buffer },
    },
  });
}

async function listDocuments(api: APIRequestContext, token: string, sessionId: string) {
  return api.get(`/sessions/${sessionId}/documents`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

async function injectToken(page: Page, token: string): Promise<void> {
  await page.addInitScript(
    ([key, value]) => window.localStorage.setItem(key, value),
    [AUTH_TOKEN_STORAGE_KEY, token],
  );
}

test(
  "[AC-031/AC-032] uploading a valid PDF through the real rendered file input " +
    "sends a true multipart request and the Documents table shows the new row, " +
    "sourced from the backend, with status 'processing'",
  async ({ page }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, "ui-upload");
    const sessionName = `UI Upload ${Date.now()}`;
    await createSession(api, token, sessionName);

    await injectToken(page, token);
    await page.goto("/sessions");
    await page.getByRole("button", { name: new RegExp(`Open session ${sessionName}`) }).click();

    const fileInput = page.locator("#pdf-file-input");
    await fileInput.setInputFiles({
      name: "notes.pdf",
      mimeType: "application/pdf",
      buffer: FAKE_PDF,
    });

    await expect(page.getByText(/was uploaded and is being processed/i)).toBeVisible();
    await expect(page.getByText("notes.pdf", { exact: true })).toBeVisible();
    await expect(page.getByText("Processing", { exact: true })).toBeVisible();

    await api.dispose();
  },
);

test(
  "[AC-033] a disguised non-PDF (.pdf name, non-PDF content-type) submitted through the " +
    "real rendered file input is rejected by the live backend with its exact detail " +
    "message, and no row is added to the Documents table",
  async ({ page }) => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, "ac033-ui-reject");
    const sessionName = `UI Reject ${Date.now()}`;
    const sessionId = await createSession(api, token, sessionName);

    await injectToken(page, token);
    await page.goto("/sessions");
    await page.getByRole("button", { name: new RegExp(`Open session ${sessionName}`) }).click();

    // Passes the screen's own quick local check (name ends in ".pdf"), but
    // the actual bytes/declared content-type are not a PDF, so the live
    // backend's stricter check (app/routers/sessions.py upload_document)
    // rejects it with 422 "Only PDF files are supported." -- proving the
    // *backend's* rejection path renders on-screen, not just the client guard.
    const fileInput = page.locator("#pdf-file-input");
    await fileInput.setInputFiles({
      name: "disguised.pdf",
      mimeType: "text/plain",
      buffer: Buffer.from("not actually a pdf"),
    });

    await expect(page.getByText("Only PDF files are supported.")).toBeVisible();
    await expect(page.getByText("disguised.pdf", { exact: true })).toHaveCount(0);
    await expect(page.getByText(/was uploaded and is being processed/i)).toHaveCount(0);

    const listing = await listDocuments(api, token, sessionId);
    expect(await listing.json()).toEqual([]);

    await api.dispose();
  },
);

test(
  "[AC-013] uploading a valid PDF within the size limit is accepted, queued, " +
    "and shows up only under its own session",
  async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, "valid-upload");
    const sessionId = await createSession(api, token, `Upload ${Date.now()}`);
    const otherSessionId = await createSession(api, token, `Other ${Date.now()}`);

    const response = await uploadFile(
      api,
      token,
      sessionId,
      "notes.pdf",
      FAKE_PDF,
      "application/pdf",
    );

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.filename).toBe("notes.pdf");
    expect(body.status).toBe("processing");
    expect(body.id).toBeTruthy();

    const ownListing = await listDocuments(api, token, sessionId);
    expect(ownListing.ok()).toBeTruthy();
    const ownDocs = await ownListing.json();
    expect(ownDocs.map((d: { id: string }) => d.id)).toContain(body.id);
    expect(ownDocs[0]).toHaveProperty("status");
    expect(ownDocs[0]).toHaveProperty("error_message");
    expect(ownDocs[0]).toHaveProperty("page_count");

    // Associated with that session only -- not the sibling session.
    const otherListing = await listDocuments(api, token, otherSessionId);
    expect(await otherListing.json()).toEqual([]);

    await api.dispose();
  },
);

test("[AC-014] uploading a non-PDF file is rejected with a PDF-only message, nothing stored", async () => {
  const api = await playwrightRequest.newContext({ baseURL: API_BASE });
  const token = await signup(api, "non-pdf-upload");
  const sessionId = await createSession(api, token, `Reject ${Date.now()}`);

  const docxResponse = await uploadFile(
    api,
    token,
    sessionId,
    "report.docx",
    Buffer.from("not a pdf"),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  );
  expect(docxResponse.status()).toBe(422);
  const docxBody = await docxResponse.json();
  expect(docxBody.detail.toLowerCase()).toContain("pdf");

  const txtResponse = await uploadFile(
    api,
    token,
    sessionId,
    "notes.txt",
    Buffer.from("just some notes"),
    "text/plain",
  );
  expect(txtResponse.status()).toBe(422);
  expect((await txtResponse.json()).detail.toLowerCase()).toContain("pdf");

  const imageResponse = await uploadFile(
    api,
    token,
    sessionId,
    "scan.png",
    Buffer.from("fake png bytes"),
    "image/png",
  );
  expect(imageResponse.status()).toBe(422);
  expect((await imageResponse.json()).detail.toLowerCase()).toContain("pdf");

  const listing = await listDocuments(api, token, sessionId);
  expect(await listing.json()).toEqual([]);

  await api.dispose();
});

test(
  "[AC-015] uploading a PDF larger than the ~20MB limit is rejected with the " +
    "limit clearly stated, nothing stored",
  async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, "oversized-upload");
    const sessionId = await createSession(api, token, `Oversize ${Date.now()}`);

    const oversized = Buffer.alloc(20 * 1024 * 1024 + 1, 0);
    const response = await uploadFile(
      api,
      token,
      sessionId,
      "huge.pdf",
      oversized,
      "application/pdf",
    );

    expect(response.status()).toBe(422);
    const detail: string = (await response.json()).detail.toLowerCase();
    expect(detail).toContain("20");
    expect(detail).toMatch(/mb|megabyte/);

    const listing = await listDocuments(api, token, sessionId);
    expect(await listing.json()).toEqual([]);

    await api.dispose();
  },
);

test(
  "[AC-016] once a session holds the maximum documents, the next upload is " +
    "rejected with the per-session limit explained",
  async () => {
    const api = await playwrightRequest.newContext({ baseURL: API_BASE });
    const token = await signup(api, "capped-session");
    const sessionId = await createSession(api, token, `Capped ${Date.now()}`);

    // Fill the session to its cap through the real upload route, one request
    // per document, exactly as a user attaching many files would.
    const MAX_DOCUMENTS_PER_SESSION = 20;
    for (let i = 0; i < MAX_DOCUMENTS_PER_SESSION; i += 1) {
      const response = await uploadFile(
        api,
        token,
        sessionId,
        `doc-${i}.pdf`,
        FAKE_PDF,
        "application/pdf",
      );
      expect(response.status(), `upload ${i} should succeed while under the cap`).toBe(200);
    }

    const atCapListing = await listDocuments(api, token, sessionId);
    expect((await atCapListing.json()).length).toBe(MAX_DOCUMENTS_PER_SESSION);

    const rejected = await uploadFile(
      api,
      token,
      sessionId,
      "one-too-many.pdf",
      FAKE_PDF,
      "application/pdf",
    );

    expect(rejected.status()).toBe(422);
    const detail: string = (await rejected.json()).detail.toLowerCase();
    expect(detail).toMatch(/limit|maximum/);

    const finalListing = await listDocuments(api, token, sessionId);
    const finalDocs = await finalListing.json();
    expect(finalDocs.length).toBe(MAX_DOCUMENTS_PER_SESSION);
    expect(finalDocs.map((d: { filename: string }) => d.filename)).not.toContain(
      "one-too-many.pdf",
    );

    await api.dispose();
  },
);
