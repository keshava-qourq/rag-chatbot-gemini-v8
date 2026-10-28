/**
 * Per-user JWT token storage.
 *
 * The token lives under localStorage key "access_token" -- fixed, because
 * frontend/e2e/session-isolation.spec.ts already injects tokens under that
 * exact key, and other tickets (US-001-1, US-005-1) read it through these
 * same helpers rather than touching localStorage directly.
 */
const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // localStorage unavailable (e.g. private browsing) -- the session simply
    // won't persist across reloads; nothing else to do here.
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // see above.
  }
}
