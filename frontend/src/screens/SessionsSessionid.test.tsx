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

beforeEach(() => {
  sessionStorage.setItem("currentSessionId", "sess-1");
  mockedApiFetch.mockReset();
});

afterEach(() => {
  sessionStorage.clear();
});

describe("SessionsSessionid ask/history/citations", () => {
  it("[AC-029] loads history on mount and renders prior Q/A pairs in chronological order", async () => {
    mockedApiFetch.mockResolvedValueOnce(
      messagesResponse([
        { question: "First question?", answer: "First answer." },
        { question: "Second question?", answer: "Second answer." },
      ]),
    );

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/First question\?/)).toBeInTheDocument());
    const items = screen.getAllByText(/Q:/);
    expect(items.length).toBe(2);
    expect(screen.getByText(/Second question\?/)).toBeInTheDocument();
    expect(mockedApiFetch).toHaveBeenCalledWith("/sessions/sess-1/messages", { method: "GET" });
  });

  it("submitting the question form calls POST /sessions/{id}/messages and renders the returned answer", async () => {
    mockedApiFetch.mockResolvedValueOnce([]); // initial GET
    mockedApiFetch.mockResolvedValueOnce({
      id: "a-new",
      session_id: "sess-1",
      role: "assistant",
      content: "Here is the answer.",
      citations: [],
      created_at: "2026-10-28T10:00:00Z",
    }); // POST
    mockedApiFetch.mockResolvedValueOnce(
      messagesResponse([{ question: "What is the policy?", answer: "Here is the answer." }]),
    ); // reload GET

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalledTimes(1));

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
    mockedApiFetch.mockResolvedValueOnce(
      messagesResponse([
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
    );

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/refund-policy\.pdf/)).toBeInTheDocument());
    expect(screen.getByText(/refund-policy\.pdf.*p\.4/)).toBeInTheDocument();
    expect(screen.getByText(/terms\.pdf.*p\.2/)).toBeInTheDocument();
  });

  it("[AC-028/NFR-014] names the source document even when page_number is null", async () => {
    mockedApiFetch.mockResolvedValueOnce(
      messagesResponse([
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
    );

    render(<Screen />);

    await waitFor(() => expect(screen.getByText(/appendix-doc\.pdf/)).toBeInTheDocument());
    const citation = screen.getByText(/appendix-doc\.pdf/);
    expect(citation.textContent).not.toMatch(/p\./);
  });

  it("surfaces a 422 'no ready documents' response via the askWarning banner instead of asking the question", async () => {
    mockedApiFetch.mockResolvedValueOnce([]); // initial GET
    mockedApiFetch.mockRejectedValueOnce(
      new Error("POST /sessions/sess-1/messages failed: 422"),
    );

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalledTimes(1));

    const input = screen.getByPlaceholderText(/Ask a question/i);
    await user.type(input, "Any ready docs?");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() =>
      expect(screen.getByText(/No ready documents yet/)).toBeInTheDocument(),
    );
    // No fake answer added
    expect(screen.queryByText(/Any ready docs\?/)).not.toBeInTheDocument();
  });

  it("[AC-026] surfaces a clear inline error on a 502/503 Gemini failure and does not add a fake answer", async () => {
    mockedApiFetch.mockResolvedValueOnce([]); // initial GET
    mockedApiFetch.mockRejectedValueOnce(
      new Error("POST /sessions/sess-1/messages failed: 502"),
    );

    const user = userEvent.setup();
    render(<Screen />);

    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalledTimes(1));

    const input = screen.getByPlaceholderText(/Ask a question/i);
    await user.type(input, "Will this fail?");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() =>
      expect(screen.getByText(/could not be generated right now/i)).toBeInTheDocument(),
    );
    expect(screen.queryByText(/Will this fail\?/)).not.toBeInTheDocument();
  });

  it("shows an error state when history fails to load", async () => {
    mockedApiFetch.mockRejectedValueOnce(new Error("GET /sessions/sess-1/messages failed: 500"));

    render(<Screen />);

    await waitFor(() =>
      expect(screen.getByText(/Couldn't load the conversation history/i)).toBeInTheDocument(),
    );
  });

  it("shows the empty state when there is no history", async () => {
    mockedApiFetch.mockResolvedValueOnce([]);

    render(<Screen />);

    await waitFor(() =>
      expect(screen.getByText(/No questions asked yet/i)).toBeInTheDocument(),
    );
  });
});
