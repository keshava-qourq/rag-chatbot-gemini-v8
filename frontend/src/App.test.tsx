import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renders a screen inside the app shell and shows its menu", () => {
    render(
      <MemoryRouter initialEntries={["/sessions"]}>
        <App />
      </MemoryRouter>,
    );
    // getAllByText, not getByText: the page may repeat its menu item's text.
    expect(screen.getAllByText("Sessions").length).toBeGreaterThan(0);
  });

  it("[AC-006] redirects to /login when no token is stored", () => {
    localStorage.removeItem("access_token");
    render(
      <MemoryRouter initialEntries={["/sessions"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Log in to your workspace/i)).toBeInTheDocument();
  });
});
