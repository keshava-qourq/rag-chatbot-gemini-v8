/// <reference types="vite/client" />
// Without the reference above, `import.meta.env` is not typed and `tsc --noEmit` fails --
// which `vite build` does not catch, because it tree-shakes this module out when no screen
// imports it yet.
//
// Where the generated API lives.
//
// Set at build time: the platform bakes the deployed API URL into the frontend build. The
// fallback is the local backend so a bare `npm run dev` still points somewhere real.
import { clearToken, getToken } from "@/lib/auth";

export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// Kept for now per this ticket's constraints: no longer used to authenticate
// requests (apiFetch now attaches the per-user token from lib/auth instead),
// but other code may still import it.
export const API_SECRET_KEY: string = import.meta.env.VITE_API_SECRET_KEY ?? "";

export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = await response.json();
      detail = typeof body?.detail === "string" ? body.detail : undefined;
    } catch {
      // Body wasn't JSON (or was empty) -- no server-provided detail to surface.
    }
    // A 401 while we had a token means the session is no longer valid (expired
    // or revoked): force re-login. A 401 with no token attached (e.g. a bad
    // login attempt) is just a normal failed request -- nothing to invalidate.
    if (response.status === 401 && token) {
      clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    throw new ApiError(
      `${init?.method ?? "GET"} ${path} failed: ${response.status}`,
      response.status,
      detail,
    );
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}
