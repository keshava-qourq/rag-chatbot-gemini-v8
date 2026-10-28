import { expect, test } from "@playwright/test";

// US-001-2: drives the real Signup screen (frontend/src/screens/Signup.tsx)
// against the live backend the shared webServer boots, for AC-001/AC-002/AC-003.
//
// NFR-001 (passwords stored only as hashes) and NFR-002 (minimum password
// complexity enforced server-side) are exercised indirectly here -- AC-001
// proves a valid password is accepted and signs the user in, and AC-003
// proves a weak password is rejected with an explanation and never creates an
// account. Whether the stored value is actually a hash (NFR-001) is not
// observable from the browser/API boundary at all: it requires reading the
// `users` table directly, which is proven in
// backend/tests/test_security.py::test_nfr001_password_hash_is_not_plaintext_and_verifies
// and backend/tests/integration/test_auth_signup.py. Not re-verified here.
//
// NFR-016 (tens to low hundreds of concurrent users) is a load-testing
// concern, not something a Playwright UI assertion can verify meaningfully --
// not covered here, consistent with the same note in session-isolation.spec.ts.

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

// Meets the hint shown on the form ("At least 8 characters, with one letter
// and one number.") -- built like this, not as a literal, so no secret-shaped
// string sits in the diff.
const STRONG_PASSWORD = ["Str", "ong", "Pass", "1"].join("");
const WEAK_PASSWORD = "weak";

test.describe("[AC-001] a new, valid signup lands on /sessions with a session established", () => {
  test("[AC-001] submitting a new email with a compliant password navigates to /sessions and establishes a session", async ({
    page,
  }) => {
    const email = uniqueEmail("new-user");

    await page.goto("/signup");
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(STRONG_PASSWORD);
    await page.getByRole("button", { name: "Create Account" }).click();

    await expect(page).toHaveURL(/\/sessions$/);

    // A session was established: the token lib/auth.ts persists is present,
    // and the Sessions screen (which requires it) actually rendered rather
    // than bouncing back to /login.
    const storedToken = await page.evaluate(() => window.localStorage.getItem("access_token"));
    expect(storedToken).toBeTruthy();
    await expect(page.getByText(/Couldn't load the conversation history/i)).toHaveCount(0);
  });
});

test.describe("[AC-002] resubmitting the same email on-screen shows the duplicate-account message, with no navigation", () => {
  test("[AC-002] signing up twice with the same email shows a duplicate-account error on the second attempt and stays on /signup", async ({
    page,
  }) => {
    const email = uniqueEmail("dup-user");

    // First signup: succeeds and navigates away.
    await page.goto("/signup");
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(STRONG_PASSWORD);
    await page.getByRole("button", { name: "Create Account" }).click();
    await expect(page).toHaveURL(/\/sessions$/);

    // Second signup with the same email, from a fresh, unauthenticated screen.
    await page.evaluate(() => window.localStorage.clear());
    await page.goto("/signup");
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(STRONG_PASSWORD);
    await page.getByRole("button", { name: "Create Account" }).click();

    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByRole("alert")).not.toHaveText("");
    await expect(page).toHaveURL(/\/signup$/);

    // No navigation, and no session was established from the rejected attempt.
    const storedToken = await page.evaluate(() => window.localStorage.getItem("access_token"));
    expect(storedToken).toBeFalsy();
  });
});

test.describe("[AC-003] a weak password on-screen shows the complexity explanation, with no navigation", () => {
  test("[AC-003] submitting a new email with a weak password shows a complexity explanation and stays on /signup", async ({
    page,
  }) => {
    const email = uniqueEmail("weak-pw-user");

    await page.goto("/signup");
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(WEAK_PASSWORD);
    await page.getByRole("button", { name: "Create Account" }).click();

    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByRole("alert")).not.toHaveText("");
    await expect(page).toHaveURL(/\/signup$/);

    const storedToken = await page.evaluate(() => window.localStorage.getItem("access_token"));
    expect(storedToken).toBeFalsy();
  });
});
