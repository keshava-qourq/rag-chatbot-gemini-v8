import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./Login";
import { apiFetch, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, apiFetch: vi.fn() };
});

const navigateMock = vi.fn();
vi.mock("@/lib/navigate", async () => {
  const actual = await vi.importActual<typeof import("@/lib/navigate")>("@/lib/navigate");
  return { ...actual, useNavigate: () => navigateMock };
});

const mockedApiFetch = vi.mocked(apiFetch);

beforeEach(() => {
  localStorage.clear();
  mockedApiFetch.mockReset();
  navigateMock.mockReset();
});

describe("Login", () => {
  it("[AC-004] submitting correct credentials calls POST /auth/login, stores access_token, and navigates to sessions", async () => {
    mockedApiFetch.mockResolvedValueOnce({
      access_token: "jwt-123",
      user: { id: "u1", email: "a@b.com" },
    });

    const user = userEvent.setup();
    render(<Screen />);

    await user.type(screen.getByLabelText(/Email/i), "a@b.com");
    await user.type(screen.getByLabelText(/Password/i), "password123");
    await user.click(screen.getByRole("button", { name: /Log In/i }));

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("sessions"));
    expect(mockedApiFetch).toHaveBeenCalledWith("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "a@b.com", password: "password123" }),
    });
    expect(getToken()).toBe("jwt-123");
  });

  it("[AC-005] submitting wrong credentials shows the server's generic message verbatim with no local existence check", async () => {
    mockedApiFetch.mockRejectedValueOnce(
      new ApiError("POST /auth/login failed: 401", 401, "Invalid email or password."),
    );

    const user = userEvent.setup();
    render(<Screen />);

    await user.type(screen.getByLabelText(/Email/i), "nobody@nowhere.com");
    await user.type(screen.getByLabelText(/Password/i), "wrongpass");
    await user.click(screen.getByRole("button", { name: /Log In/i }));

    await waitFor(() =>
      expect(screen.getByText("Invalid email or password.")).toBeInTheDocument(),
    );
    expect(navigateMock).not.toHaveBeenCalled();
    expect(getToken()).toBeNull();
  });
});
