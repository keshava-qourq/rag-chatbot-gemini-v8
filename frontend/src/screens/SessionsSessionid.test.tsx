import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./SessionsSessionid";
import { apiFetch } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
}));

vi.mock("@/lib/navigate", async () => {
  const actual = await vi.importActual<typeof import("@/lib/navigate")>("@/lib/navigate");
  return { ...actual, useNavigate: () => vi.fn() };
});

const mockedApiFetch = vi.mocked(apiFetch);

type TestCitation = {
  id: string;
  document_id: string;
  filename: string;
  page_number: number | null;
  snippet: string;
};

function messagesResponse(
  pairs: Array<{ question: string; answer: string; citations?: TestCitation[] }>,
) {
  const out: unknown[] = [];
  pairs.forEach((pair, i) => {
    out.push({
      id: `u-${i}`,
      session_id: "sess-1",
      role: "user",
      content: pair.question,
      citations: [],
      created_at: `2026-10-2${i}T10:00:00Z`,
    });
    out.push({
      id: `a-${i}`,
      session_id: "sess-1",
      role: "assistant",
      content: pair.answer,
      citations: pair.citations ?? [],
      created_at: `2026-10-2${i}T10:00:05Z`,
    });
  });
  return out;
}

// This screen fires two independent GETs on mount -- documents and messages
// (AC-012) -- in an order the implementation is free to choose. Route each
// mocked call by its path rather than relying on call order.
function mockApiByPath(
  responses: Record<string, unknown>,
  overrides: Array<{
    match: (path: string, init?: RequestInit) => boolean;
    handler: () => unknown;
  }> = [],
) {
  mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
    for (const { match, handler } of overrides) {
      if (match(path, init)) return handler();
    }
    for (const [key, value] of Object.entries(responses)) {
      if (path === key) {
        if (value instanceof Error) throw value;
        return value;
      }
    }
    throw new Error(`Unexpected apiFetch call: ${path}`);
  });
}

beforeEach(() => {
  sessionStorage.setItem("currentSessionId", "sess-1");
  mockedApiFetch.mockReset();
});

afterEach(() => {
  sessionStorage.clear();
});

describe("SessionsSessionid documents panel", () => {
  it("[AC-012] loads documents from GET /sessions/{id}/documents on mount and renders the API's real fields", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [
        {
          id: "d1",
          filename: "policy.pdf",
          status: "ready",
          size_bytes: 2_430_000,
          page_count: 12,
          error_message: null,
          created_at: "2026-10-24T09:12:00Z",
        },
        {
          id: "d2",
          filename: "scan.pdf",
          status: "failed",
          size_bytes: 5_310_000,
          page_count: null,
          error_message: "No extractable text found.",
          created_at: "2026-10-26T11:03:00Z",
        },
      ],
      "/sessions/sess-1/messages": [],
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText("policy.pdf")).toBeInTheDocument());
    expect(screen.getByText("scan.pdf")).toBeInTheDocument();
    expect(screen.getByText("No extractable text found.")).toBeInTheDocument();
    expect(screen.getByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("Failed")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(mockedApiFetch).toHaveBeenCalledWith("/sessions/sess-1/documents", { method: "GET" });
  });

  it("[AC-012] shows the empty state when the session has no documents", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [],
      "/sessions/sess-1/messages": [],
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/No documents yet/i)).toBeInTheDocument());
  });

  it("[AC-012] shows an error state when the documents fetch fails", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": new Error("GET /sessions/sess-1/documents failed: 500"),
      "/sessions/sess-1/messages": [],
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/Couldn't load documents/i)).toBeInTheDocument());
  });

  it("[AC-012] switching sessions shows only the newly-opened session's documents, with none lingering", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [
        {
          id: "d1",
          filename: "session-one.pdf",
          status: "ready",
          size_bytes: 1000,
          page_count: 1,
          error_message: null,
          created_at: "2026-10-24T09:12:00Z",
        },
      ],
      "/sessions/sess-1/messages": [],
    });

    const { unmount } = render(<Screen />);
    await waitFor(() => expect(screen.getByText("session-one.pdf")).toBeInTheDocument());
    unmount();

    sessionStorage.setItem("currentSessionId", "sess-2");
    mockedApiFetch.mockReset();
    mockApiByPath({
      "/sessions/sess-2/documents": [
        {
          id: "d2",
          filename: "session-two.pdf",
          status: "ready",
          size_bytes: 2000,
          page_count: 2,
          error_message: null,
          created_at: "2026-10-25T09:12:00Z",
        },
      ],
      "/sessions/sess-2/messages": [],
    });

    render(<Screen />);
    await waitFor(() => expect(screen.getByText("session-two.pdf")).toBeInTheDocument());
    expect(screen.queryByText("session-one.pdf")).not.toBeInTheDocument();
  });
});

describe("SessionsSessionid ask/history/citations", () => {
  it("[AC-029] loads history on mount and renders prior Q/A pairs in chronological order", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [],
      "/sessions/sess-1/messages": messagesResponse([
        { question: "First question?", answer: "First answer." },
        { question: "Second question?", answer: "Second answer." },
      ]),
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/First question\?/)).toBeInTheDocument());
    const items = screen.getAllByText(/Q:/);
    expect(items.length).toBe(2);
    expect(screen.getByText(/Second question\?/)).toBeInTheDocument();
    expect(mockedApiFetch).toHaveBeenCalledWith("/sessions/sess-1/messages", { method: "GET" });
  });

  it("submitting the question form calls POST /sessions/{id}/messages and renders the returned answer", async () => {
    let postCalled = false;
    mockApiByPath(
      {
        "/sessions/sess-1/documents": [],
      },
      [
        {
          match: (path, init) => path === "/sessions/sess-1/messages" && init?.method === "POST",
          handler: () => {
            postCalled = true;
            return {
              id: "a-new",
              session_id: "sess-1",
              role: "assistant",
              content: "Here is the answer.",
              citations: [],
              created_at: "2026-10-28T10:00:00Z",
            };
          },
        },
        {
          match: (path, init) =>
            path === "/sessions/sess-1/messages" && (!init || init.method === "GET"),
          handler: () =>
            postCalled
              ? messagesResponse([
                  { question: "What is the policy?", answer: "Here is the answer." },
                ])
              : [],
        },
      ],
    );

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() =>
      expect(screen.queryByText(/Loading conversation history/i)).not.toBeInTheDocument(),
    );

    const input = screen.getByPlaceholderText(/Ask a question/i);
    await user.type(input, "What is the policy?");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() => expect(screen.getByText(/Here is the answer\./)).toBeInTheDocument());

    expect(mockedApiFetch).toHaveBeenCalledWith("/sessions/sess-1/messages", {
      method: "POST",
      body: JSON.stringify({ question: "What is the policy?" }),
    });
  });

  it("[AC-027] renders one citation per source chunk naming filename and page number", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [],
      "/sessions/sess-1/messages": messagesResponse([
        {
          question: "Refund policy?",
          answer: "Refunds within 30 days.",
          citations: [
            {
              id: "c1",
              document_id: "d1",
              filename: "refund-policy.pdf",
              page_number: 4,
              snippet: "...",
            },
            {
              id: "c2",
              document_id: "d2",
              filename: "terms.pdf",
              page_number: 2,
              snippet: "...",
            },
          ],
        },
      ]),
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/refund-policy\.pdf/)).toBeInTheDocument());
    expect(screen.getByText(/refund-policy\.pdf.*p\.4/)).toBeInTheDocument();
    expect(screen.getByText(/terms\.pdf.*p\.2/)).toBeInTheDocument();
  });

  it("[AC-028/NFR-014] names the source document even when page_number is null", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [],
      "/sessions/sess-1/messages": messagesResponse([
        {
          question: "Pricing?",
          answer: "See appendix.",
          citations: [
            {
              id: "c1",
              document_id: "d1",
              filename: "appendix-doc.pdf",
              page_number: null,
              snippet: "...",
            },
          ],
        },
      ]),
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/appendix-doc\.pdf/)).toBeInTheDocument());
    const citation = screen.getByText(/appendix-doc\.pdf/);
    expect(citation.textContent).not.toMatch(/p\./);
  });

  it("surfaces a 422 'no ready documents' response via the askWarning banner instead of asking the question", async () => {
    mockApiByPath(
      {
        "/sessions/sess-1/documents": [],
      },
      [
        {
          match: (path, init) => path === "/sessions/sess-1/messages" && init?.method === "POST",
          handler: () => {
            throw new Error("POST /sessions/sess-1/messages failed: 422");
          },
        },
        {
          match: (path, init) =>
            path === "/sessions/sess-1/messages" && (!init || init.method === "GET"),
          handler: () => [],
        },
      ],
    );

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() =>
      expect(screen.queryByText(/Loading conversation history/i)).not.toBeInTheDocument(),
    );

    const input = screen.getByPlaceholderText(/Ask a question/i);
    await user.type(input, "Any ready docs?");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() => expect(screen.getByText(/No ready documents yet/)).toBeInTheDocument());
    // No fake answer added
    expect(screen.queryByText(/Any ready docs\?/)).not.toBeInTheDocument();
  });

  it("[AC-026] surfaces a clear inline error on a 502/503 Gemini failure and does not add a fake answer", async () => {
    mockApiByPath(
      {
        "/sessions/sess-1/documents": [],
      },
      [
        {
          match: (path, init) => path === "/sessions/sess-1/messages" && init?.method === "POST",
          handler: () => {
            throw new Error("POST /sessions/sess-1/messages failed: 502");
          },
        },
        {
          match: (path, init) =>
            path === "/sessions/sess-1/messages" && (!init || init.method === "GET"),
          handler: () => [],
        },
      ],
    );

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() =>
      expect(screen.queryByText(/Loading conversation history/i)).not.toBeInTheDocument(),
    );

    const input = screen.getByPlaceholderText(/Ask a question/i);
    await user.type(input, "Will this fail?");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() =>
      expect(screen.getByText(/could not be generated right now/i)).toBeInTheDocument(),
    );
    expect(screen.queryByText(/Will this fail\?/)).not.toBeInTheDocument();
  });

  it("shows an error state when history fails to load", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [],
      "/sessions/sess-1/messages": new Error("GET /sessions/sess-1/messages failed: 500"),
    });

    render(<Screen />);

    await waitFor(() =>
      expect(screen.getByText(/Couldn't load the conversation history/i)).toBeInTheDocument(),
    );
  });

  it("shows the empty state when there is no history", async () => {
    mockApiByPath({
      "/sessions/sess-1/documents": [],
      "/sessions/sess-1/messages": [],
    });

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/No questions asked yet/i)).toBeInTheDocument());
  });
});
