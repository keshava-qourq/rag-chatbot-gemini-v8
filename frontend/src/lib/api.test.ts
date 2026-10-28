import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiFetch } from "@/lib/api";
import { getToken, setToken } from "@/lib/auth";

function stubLocationHref(): { get: () => string } {
  let href = "";
  Object.defineProperty(window, "location", {
    configurable: true,
    value: {
      ...window.location,
      set href(value: string) {
        href = value;
      },
      get href() {
        return href;
      },
    },
  });
  return { get: () => href };
}

describe("apiFetch", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("[AC-006] attaches the stored token as Authorization: Bearer on every call", async () => {
    setToken("my-jwt");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiFetch("/sessions");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/sessions",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer my-jwt" }),
      }),
    );
  });

  it("[AC-006] a 401 response clears the stored token and redirects to /login", async () => {
    const location = stubLocationHref();
    setToken("stale-jwt");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Not authenticated" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiFetch("/sessions")).rejects.toThrow();

    expect(getToken()).toBeNull();
    expect(location.get()).toBe("/login");
  });
});
