import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./SessionsSessionid";
import { apiFetch } from "@/lib/api";

// US-014-1: the Documents list must keep polling GET /sessions/{id}/documents
// while any row is 'processing', updating statuses in place without a full
// page reload, and must stop once nothing is left processing (AC-035..037).
// Real timers are used (rather than fake timers) because this component's
// poll loop is driven by setTimeout scheduled from inside a state update
// that resolves through a real microtask (apiFetch), which deadlocks under
// vi.useFakeTimers + waitFor's own polling. The poll interval is 4s, so
// these tests use a generous waitFor timeout instead.
vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
}));

vi.mock("@/lib/navigate", async () => {
  const actual = await vi.importActual<typeof import("@/lib/navigate")>("@/lib/navigate");
  return { ...actual, useNavigate: () => vi.fn() };
});

const mockedApiFetch = vi.mocked(apiFetch);
const POLL_WAIT = { timeout: 8000, interval: 100 };

function processingDoc(overrides = {}) {
  return {
    id: "d1",
    filename: "report.pdf",
    status: "processing",
    size_bytes: 1_000_000,
    page_count: null,
    error_message: null,
    created_at: "2026-10-28T09:00:00Z",
    ...overrides,
  };
}

function docCallCount() {
  return mockedApiFetch.mock.calls.filter(([path]) => path === "/sessions/sess-1/documents")
    .length;
}

beforeEach(() => {
  sessionStorage.setItem("currentSessionId", "sess-1");
  mockedApiFetch.mockReset();
});

afterEach(() => {
  sessionStorage.clear();
});

describe("SessionsSessionid documents polling", () => {
  it(
    "[AC-035] polls GET /sessions/{id}/documents repeatedly while a document is 'processing'",
    async () => {
      mockedApiFetch.mockImplementation(async (path: string) => {
        if (path === "/sessions/sess-1/documents") return [processingDoc()];
        if (path === "/sessions/sess-1/messages") return [];
        throw new Error(`Unexpected apiFetch call: ${path}`);
      });

      render(<Screen />);

      await waitFor(() => expect(screen.getByText("report.pdf")).toBeInTheDocument());
      expect(docCallCount()).toBe(1);

      await waitFor(() => expect(docCallCount()).toBeGreaterThanOrEqual(2), POLL_WAIT);
      await waitFor(() => expect(docCallCount()).toBeGreaterThanOrEqual(3), POLL_WAIT);
    },
    20000,
  );

  it(
    "[AC-036] updates the displayed status to 'ready' in place once processing completes, without reload",
    async () => {
      let call = 0;
      mockedApiFetch.mockImplementation(async (path: string) => {
        if (path === "/sessions/sess-1/documents") {
          call += 1;
          if (call === 1) return [processingDoc()];
          return [processingDoc({ status: "ready", page_count: 12 })];
        }
        if (path === "/sessions/sess-1/messages") return [];
        throw new Error(`Unexpected apiFetch call: ${path}`);
      });

      render(<Screen />);

      await waitFor(() => expect(screen.getByText("Processing")).toBeInTheDocument());
      await waitFor(() => expect(screen.getByText("Ready")).toBeInTheDocument(), POLL_WAIT);
      expect(screen.queryByText("Processing")).not.toBeInTheDocument();

      const callsAfterReady = docCallCount();
      await new Promise((resolve) => setTimeout(resolve, 4500));
      expect(docCallCount()).toBe(callsAfterReady);
    },
    20000,
  );

  it(
    "[AC-037] updates the displayed status to 'failed' and shows the backend's error_message",
    async () => {
      let call = 0;
      mockedApiFetch.mockImplementation(async (path: string) => {
        if (path === "/sessions/sess-1/documents") {
          call += 1;
          if (call === 1) return [processingDoc()];
          return [
            processingDoc({
              status: "failed",
              error_message: "No extractable text found.",
            }),
          ];
        }
        if (path === "/sessions/sess-1/messages") return [];
        throw new Error(`Unexpected apiFetch call: ${path}`);
      });

      render(<Screen />);

      await waitFor(() => expect(screen.getByText("Processing")).toBeInTheDocument());
      await waitFor(() => expect(screen.getByText("Failed")).toBeInTheDocument(), POLL_WAIT);
      expect(screen.getByText("No extractable text found.")).toBeInTheDocument();
    },
    20000,
  );

  it(
    "does not poll when no document is 'processing' on initial load",
    async () => {
      mockedApiFetch.mockImplementation(async (path: string) => {
        if (path === "/sessions/sess-1/documents") return [processingDoc({ status: "ready" })];
        if (path === "/sessions/sess-1/messages") return [];
        throw new Error(`Unexpected apiFetch call: ${path}`);
      });

      render(<Screen />);

      await waitFor(() => expect(screen.getByText("Ready")).toBeInTheDocument());

      await new Promise((resolve) => setTimeout(resolve, 4500));
      expect(docCallCount()).toBe(1);
    },
    20000,
  );

  it(
    "clears the poll timer on unmount so no further calls happen after the component unmounts",
    async () => {
      mockedApiFetch.mockImplementation(async (path: string) => {
        if (path === "/sessions/sess-1/documents") return [processingDoc()];
        if (path === "/sessions/sess-1/messages") return [];
        throw new Error(`Unexpected apiFetch call: ${path}`);
      });

      const { unmount } = render(<Screen />);
      await waitFor(() => expect(screen.getByText("Processing")).toBeInTheDocument());

      unmount();
      const callsAtUnmount = docCallCount();

      await new Promise((resolve) => setTimeout(resolve, 5500));
      expect(docCallCount()).toBe(callsAtUnmount);
    },
    20000,
  );

  it(
    "does not refetch or reset conversation history while polling documents",
    async () => {
      let call = 0;
      mockedApiFetch.mockImplementation(async (path: string) => {
        if (path === "/sessions/sess-1/documents") {
          call += 1;
          return call === 1 ? [processingDoc()] : [processingDoc({ status: "ready" })];
        }
        if (path === "/sessions/sess-1/messages") return [];
        throw new Error(`Unexpected apiFetch call: ${path}`);
      });

      render(<Screen />);
      await waitFor(() => expect(screen.getByText("Processing")).toBeInTheDocument());

      const messagesCallsBefore = mockedApiFetch.mock.calls.filter(
        ([path]) => path === "/sessions/sess-1/messages",
      ).length;

      await waitFor(() => expect(screen.getByText("Ready")).toBeInTheDocument(), POLL_WAIT);

      const messagesCallsAfter = mockedApiFetch.mock.calls.filter(
        ([path]) => path === "/sessions/sess-1/messages",
      ).length;
      expect(messagesCallsAfter).toBe(messagesCallsBefore);
    },
    20000,
  );
});
