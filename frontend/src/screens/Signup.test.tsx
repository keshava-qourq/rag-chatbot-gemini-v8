import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./Signup";
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

describe("Signup", () => {
  it("[AC-001] a valid unused email and compliant password creates the account, stores the token, and navigates to sessions", async () => {
    mockedApiFetch.mockResolvedValueOnce({
      access_token: "jwt-abc",
      user: { id: "u1", email: "new@site.com" },
    });

    const user = userEvent.setup();
    render(<Screen />);

    await user.type(screen.getByLabelText(/Email/i), "new@site.com");
    await user.type(screen.getByLabelText(/Password/i), "Password123");
    await user.click(screen.getByRole("button", { name: /Create Account/i }));

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("sessions"));
    expect(mockedApiFetch).toHaveBeenCalledWith("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email: "new@site.com", password: "Password123" }),
    });
    expect(getToken()).toBe("jwt-abc");
  });

  it("[AC-002] an email that already has an account shows the server's message, not a local demo-list check", async () => {
    mockedApiFetch.mockRejectedValueOnce(
      new ApiError("POST /auth/signup failed: 409", 409, "An account with this email already exists."),
    );

    const user = userEvent.setup();
    render(<Screen />);

    await user.type(screen.getByLabelText(/Email/i), "jordan.ramirez@gmail.com");
    await user.type(screen.getByLabelText(/Password/i), "Password123");
    await user.click(screen.getByRole("button", { name: /Create Account/i }));

    await waitFor(() =>
      expect(screen.getByText("An account with this email already exists.")).toBeInTheDocument(),
    );
    expect(navigateMock).not.toHaveBeenCalled();
    expect(getToken()).toBeNull();
  });

  it("[AC-003] a password failing complexity shows the server's explanation and creates no account", async () => {
    mockedApiFetch.mockRejectedValueOnce(
      new ApiError(
        "POST /auth/signup failed: 422",
        422,
        "Password must be at least 8 characters and include a letter and a number.",
      ),
    );

    const user = userEvent.setup();
    render(<Screen />);

    await user.type(screen.getByLabelText(/Email/i), "weak@site.com");
    await user.type(screen.getByLabelText(/Password/i), "weak");
    await user.click(screen.getByRole("button", { name: /Create Account/i }));

    await waitFor(() =>
      expect(
        screen.getByText("Password must be at least 8 characters and include a letter and a number."),
      ).toBeInTheDocument(),
    );
    expect(navigateMock).not.toHaveBeenCalled();
    expect(getToken()).toBeNull();
  });
});
