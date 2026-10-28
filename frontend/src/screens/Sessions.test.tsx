import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./Sessions";
import { apiFetch } from "@/lib/api";
import { getToken, setToken } from "@/lib/auth";

vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
}));

const navigateMock = vi.fn();
vi.mock("@/lib/navigate", async () => {
  const actual = await vi.importActual<typeof import("@/lib/navigate")>("@/lib/navigate");
  return { ...actual, useNavigate: () => navigateMock };
});

const mockedApiFetch = vi.mocked(apiFetch);

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  mockedApiFetch.mockReset();
  navigateMock.mockReset();
  setToken("jwt-123");
});

describe("Sessions", () => {
  it("[AC-007] loads sessions from GET /sessions on mount and lists them newest first with no seeded rows", async () => {
    mockedApiFetch.mockResolvedValueOnce([
      { id: "s2", name: "Second", created_at: "2026-10-27T10:00:00Z" },
      { id: "s1", name: "First", created_at: "2026-10-20T10:00:00Z" },
    ]);

    render(<Screen />);

    await waitFor(() => expect(screen.getByText("Second")).toBeInTheDocument());
    expect(screen.getByText("First")).toBeInTheDocument();
    expect(screen.queryByText(/Q3 Earnings Call Analysis/)).not.toBeInTheDocument();
    expect(mockedApiFetch).toHaveBeenCalledWith("/sessions", { method: "GET" });

    const rows = screen.getAllByText(/Second|First/);
    expect(rows[0]).toHaveTextContent("Second");
  });

  it("[AC-007] shows the empty state when there are no sessions", async () => {
    mockedApiFetch.mockResolvedValueOnce([]);

    render(<Screen />);

    await waitFor(() => expect(screen.getByText("No sessions yet")).toBeInTheDocument());
  });

  it("[AC-007] shows an error state when the sessions list fails to load", async () => {
    mockedApiFetch.mockRejectedValueOnce(new Error("GET /sessions failed: 500"));

    render(<Screen />);

    await waitFor(() =>
      expect(screen.getByText(/Couldn't load your sessions/)).toBeInTheDocument(),
    );
  });

  it("[AC-010] New Session posts to POST /sessions and navigates to the new empty session", async () => {
    mockedApiFetch.mockResolvedValueOnce([
      { id: "existing", name: "Existing", created_at: "2026-10-20T10:00:00Z" },
    ]); // initial load, non-empty so there's only one "New Session" button
    mockedApiFetch.mockResolvedValueOnce({
      id: "new-1",
      name: null,
      created_at: "2026-10-28T10:00:00Z",
    }); // create

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByText("Existing")).toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: /New Session/i }));

    await waitFor(() =>
      expect(mockedApiFetch).toHaveBeenCalledWith("/sessions", {
        method: "POST",
        body: JSON.stringify({}),
      }),
    );
    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("sessions-sessionid"));
    expect(sessionStorage.getItem("currentSessionId")).toBe("new-1");
  });

  it("[AC-010] Log Out calls POST /auth/logout, clears the token, and returns to /login", async () => {
    mockedApiFetch.mockResolvedValueOnce([]); // initial load
    mockedApiFetch.mockResolvedValueOnce({ status: "ok" }); // logout

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole("button", { name: /Log out of your account/i }));

    await waitFor(() =>
      expect(mockedApiFetch).toHaveBeenCalledWith("/auth/logout", { method: "POST" }),
    );
    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("login"));
    expect(getToken()).toBeNull();
  });

  it("[AC-010] Log Out still clears the token and navigates to /login even if the API call fails", async () => {
    mockedApiFetch.mockResolvedValueOnce([]); // initial load
    mockedApiFetch.mockRejectedValueOnce(new Error("POST /auth/logout failed: 401"));

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole("button", { name: /Log out of your account/i }));

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("login"));
    expect(getToken()).toBeNull();
  });
});
