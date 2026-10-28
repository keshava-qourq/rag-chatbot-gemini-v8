import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./SessionsSessionid";
import { apiFetch, ApiError } from "@/lib/api";

// US-012-1: Upload PDF form wired to the real POST /sessions/{id}/documents
// endpoint (AC-031, AC-032). Client-side pre-checks (PDF type, 20MB size,
// 20-doc cap) remain a fast local guard (AC-013..016), but accepted uploads
// now go through apiFetch as multipart/form-data and the row that appears in
// the table comes straight from the backend response.
//
// US-013-1: when the backend rejects an upload (wrong type, oversized,
// over-cap) or the request fails outright (network/auth), the form must
// surface the real ApiError.detail verbatim, or a generic message only when
// no backend detail is present -- never a fake success.
//
// US-016-2: the local guard's cap (MAX_DOCS in SessionsSessionid.tsx) mirrors
// the backend's real per-session cap, MAX_DOCUMENTS_PER_SESSION = 20
// (backend/app/config.py), so uploads under that real cap are never blocked
// client-side.
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, apiFetch: vi.fn() };
});

vi.mock("@/lib/navigate", async () => {
  const actual = await vi.importActual<typeof import("@/lib/navigate")>("@/lib/navigate");
  return { ...actual, useNavigate: () => vi.fn() };
});

const mockedApiFetch = vi.mocked(apiFetch);

function selectFile(file: File) {
  const input = document.getElementById("pdf-file-input") as HTMLInputElement;
  fireEvent.change(input, { target: { files: [file] } });
}

function pdfFile(name: string, sizeBytes?: number): File {
  const file = new File(["%PDF-1.4 fake"], name, { type: "application/pdf" });
  if (sizeBytes != null) {
    Object.defineProperty(file, "size", { value: sizeBytes });
  }
  return file;
}

function backendDoc(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: `doc-${Math.random().toString(36).slice(2)}`,
    filename: "research-notes.pdf",
    status: "processing",
    size_bytes: 1_000_000,
    page_count: null,
    error_message: null,
    created_at: "2026-10-28T10:00:00Z",
    ...overrides,
  };
}

beforeEach(() => {
  sessionStorage.setItem("currentSessionId", "sess-1");
  mockedApiFetch.mockReset();
  // GET documents and GET messages on mount both resolve empty by default;
  // individual tests override the upload POST call.
  mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
    if (path === "/sessions/sess-1/documents" && (!init || init.method === "GET")) return [];
    if (path === "/sessions/sess-1/messages") return [];
    throw new Error(`Unexpected apiFetch call: ${path}`);
  });
});

afterEach(() => {
  sessionStorage.clear();
});

describe("SessionsSessionid PDF upload", () => {
  it("[AC-031] selecting a valid PDF submits a multipart/form-data POST to /sessions/{id}/documents with the file", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        return backendDoc({ filename: "research-notes.pdf" });
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("research-notes.pdf", 1_000_000));

    await waitFor(() =>
      expect(screen.getByText(/was uploaded and is being processed/i)).toBeInTheDocument(),
    );

    const postCall = mockedApiFetch.mock.calls.find(
      ([path, init]) => path === "/sessions/sess-1/documents" && init?.method === "POST",
    );
    expect(postCall).toBeTruthy();
    const [, init] = postCall!;
    expect(init.body).toBeInstanceOf(FormData);
    expect((init.body as FormData).get("file")).toBeInstanceOf(File);
  });

  it("[AC-032] the new document appears in the table with status 'processing' sourced from the backend response", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        return backendDoc({
          id: "backend-doc-1",
          filename: "research-notes.pdf",
          status: "processing",
          page_count: null,
        });
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("research-notes.pdf", 1_000_000));

    await waitFor(() => expect(screen.getByText("research-notes.pdf")).toBeInTheDocument());
    expect(screen.getByText("Processing")).toBeInTheDocument();
  });

  it("[AC-014] selecting a Word document is rejected locally with a PDF-only message and never calls the API", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());
    mockedApiFetch.mockClear();

    const docx = new File(["fake docx"], "report.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    selectFile(docx);

    await waitFor(() => expect(screen.getByText(/isn't a PDF/i)).toBeInTheDocument());
    expect(screen.getByText(/only PDF files are supported/i)).toBeInTheDocument();
    expect(screen.queryByText("report.docx")).not.toBeInTheDocument();
    expect(mockedApiFetch).not.toHaveBeenCalled();
  });

  it("[AC-014] selecting a plain text file is rejected locally with a PDF-only message", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());
    mockedApiFetch.mockClear();

    const txt = new File(["just notes"], "notes.txt", { type: "text/plain" });
    selectFile(txt);

    await waitFor(() => expect(screen.getByText(/isn't a PDF/i)).toBeInTheDocument());
    expect(screen.getByText(/only PDF files are supported/i)).toBeInTheDocument();
    expect(screen.queryByText("notes.txt")).not.toBeInTheDocument();
    expect(mockedApiFetch).not.toHaveBeenCalled();
  });

  it("[AC-014] selecting an image file is rejected locally with a PDF-only message", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());
    mockedApiFetch.mockClear();

    const image = new File(["fake png"], "scan.png", { type: "image/png" });
    selectFile(image);

    await waitFor(() => expect(screen.getByText(/isn't a PDF/i)).toBeInTheDocument());
    expect(screen.getByText(/only PDF files are supported/i)).toBeInTheDocument();
    expect(screen.queryByText("scan.png")).not.toBeInTheDocument();
    expect(mockedApiFetch).not.toHaveBeenCalled();
  });

  it("[AC-015] selecting a PDF over the 20MB limit is rejected locally with the size limit stated, no API call", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());
    mockedApiFetch.mockClear();

    const oversized = pdfFile("huge.pdf", 21 * 1024 * 1024);
    selectFile(oversized);

    await waitFor(() =>
      expect(screen.getByText(/over the 20MB per-file limit/i)).toBeInTheDocument(),
    );
    expect(screen.queryByText("huge.pdf")).not.toBeInTheDocument();
    expect(mockedApiFetch).not.toHaveBeenCalled();
  });

  it("[AC-015] a PDF right at the 20MB limit is accepted and sent to the API", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        return backendDoc({ filename: "at-limit.pdf", size_bytes: 20 * 1024 * 1024 });
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("at-limit.pdf", 20 * 1024 * 1024));

    await waitFor(() =>
      expect(screen.getByText(/was uploaded and is being processed/i)).toBeInTheDocument(),
    );
    expect(screen.getByText("at-limit.pdf")).toBeInTheDocument();
  });

  it("[AC-016] once the session holds the maximum documents (the real backend cap of 20), the upload control is disabled and further selection is rejected locally", async () => {
    let counter = 0;
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        counter += 1;
        const file = (init.body as FormData).get("file") as File;
        return backendDoc({ id: `doc-${counter}`, filename: file.name });
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    const names = Array.from({ length: 20 }, (_, i) => `doc-${i + 1}.pdf`);
    for (const name of names) {
      selectFile(pdfFile(name, 500_000));
      await waitFor(() => expect(screen.getByText(name)).toBeInTheDocument());
    }

    const input = document.getElementById("pdf-file-input") as HTMLInputElement;
    expect(input).toBeDisabled();
    expect(screen.getByText(/Document limit reached for this session/i)).toBeInTheDocument();

    // Attempting to select a 21st file anyway must not attach it or call the API.
    mockedApiFetch.mockClear();
    selectFile(pdfFile("twenty-first.pdf", 500_000));
    await waitFor(() =>
      expect(screen.getByText(/already has 20 of 20 documents attached/i)).toBeInTheDocument(),
    );
    expect(screen.queryByText("twenty-first.pdf")).not.toBeInTheDocument();
    expect(mockedApiFetch).not.toHaveBeenCalled();
  }, 20000);

  it("[AC-016] uploading an additional document while under the real cap of 20 is never blocked client-side", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        return backendDoc({ id: "doc-under-cap", filename: "under-cap.pdf" });
      }
      // Simulate a session that already holds 19 of the real 20-cap.
      if (path === "/sessions/sess-1/documents") {
        return Array.from({ length: 19 }, (_, i) =>
          backendDoc({ id: `existing-${i}`, filename: `existing-${i}.pdf`, status: "ready" }),
        );
      }
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(screen.getByText("existing-0.pdf")).toBeInTheDocument());

    const input = document.getElementById("pdf-file-input") as HTMLInputElement;
    expect(input).not.toBeDisabled();

    selectFile(pdfFile("under-cap.pdf", 500_000));

    await waitFor(() =>
      expect(screen.getByText(/was uploaded and is being processed/i)).toBeInTheDocument(),
    );
    expect(screen.getByText("under-cap.pdf")).toBeInTheDocument();
  });

  it("surfaces a backend upload failure instead of adding a fake document row", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        throw new Error("POST /sessions/sess-1/documents failed: 500");
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("broken.pdf", 500_000));

    await waitFor(() => expect(screen.getByText(/couldn't be uploaded/i)).toBeInTheDocument());
    expect(screen.queryByText("broken.pdf")).not.toBeInTheDocument();
  });

  it("[AC-033] a backend rejection for a disguised non-PDF upload shows the exact ApiError detail and adds no document", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        throw new ApiError(
          "POST /sessions/sess-1/documents failed: 415",
          415,
          "File content does not match a PDF (declared .pdf extension with mismatched content type).",
        );
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("fake.pdf", 500_000));

    await waitFor(() =>
      expect(
        screen.getByText(
          "File content does not match a PDF (declared .pdf extension with mismatched content type).",
        ),
      ).toBeInTheDocument(),
    );
    expect(screen.queryByText("fake.pdf")).not.toBeInTheDocument();
  });

  it("[AC-033] a backend 413 oversized-file rejection shows the exact ApiError detail verbatim and adds no document", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        throw new ApiError(
          "POST /sessions/sess-1/documents failed: 413",
          413,
          "File exceeds the 20MB size limit.",
        );
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("not-flagged-locally.pdf", 500_000));

    await waitFor(() =>
      expect(screen.getByText("File exceeds the 20MB size limit.")).toBeInTheDocument(),
    );
    expect(screen.queryByText("not-flagged-locally.pdf")).not.toBeInTheDocument();
  });

  it("[AC-033] a backend 409 document-cap rejection shows the exact ApiError detail verbatim and adds no document", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        throw new ApiError(
          "POST /sessions/sess-1/documents failed: 409",
          409,
          "This session already has the maximum of 20 documents.",
        );
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("capped.pdf", 500_000));

    await waitFor(() =>
      expect(
        screen.getByText("This session already has the maximum of 20 documents."),
      ).toBeInTheDocument(),
    );
    expect(screen.queryByText("capped.pdf")).not.toBeInTheDocument();
  });

  it("[AC-034] a 401 auth failure with no backend detail shows a generic error state, not a simulated success", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        throw new ApiError("POST /sessions/sess-1/documents failed: 401", 401);
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("unauth.pdf", 500_000));

    await waitFor(() => expect(screen.getByText(/couldn't be uploaded/i)).toBeInTheDocument());
    expect(screen.queryByText("unauth.pdf")).not.toBeInTheDocument();
    expect(screen.queryByText(/was uploaded and is being processed/i)).not.toBeInTheDocument();
  });

  it("[AC-034] a plain network failure (no ApiError, no detail) shows a generic error state and adds no document", async () => {
    mockedApiFetch.mockImplementation(async (path: string, init?: RequestInit) => {
      if (path === "/sessions/sess-1/documents" && init?.method === "POST") {
        throw new TypeError("Failed to fetch");
      }
      if (path === "/sessions/sess-1/documents") return [];
      if (path === "/sessions/sess-1/messages") return [];
      throw new Error(`Unexpected apiFetch call: ${path}`);
    });

    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("offline.pdf", 500_000));

    await waitFor(() => expect(screen.getByText(/couldn't be uploaded/i)).toBeInTheDocument());
    expect(screen.queryByText("offline.pdf")).not.toBeInTheDocument();
    expect(screen.queryByText(/was uploaded and is being processed/i)).not.toBeInTheDocument();
  });
});
