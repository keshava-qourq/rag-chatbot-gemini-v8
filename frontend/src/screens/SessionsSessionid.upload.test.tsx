import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./SessionsSessionid";
import { apiFetch } from "@/lib/api";

// US-007: PDF upload to a chat session (AC-013..AC-016).
//
// SessionsSessionid.tsx's upload control still validates and tracks documents
// client-side against local state only -- it does not yet call POST
// /sessions/{id}/documents (see the top-of-screen comment and the note at
// frontend/src/lib/api.ts about which screens are wired). These tests cover
// exactly what this screen can be driven to do today: a person selecting a
// file through the real <input type="file"> and seeing it accepted or
// rejected with the right message, for every one of AC-013..016. The backend
// contract itself (what the API actually accepts/stores/queues/rejects) is
// proven against the real database/S3/Redis in
// backend/tests/integration/test_document_upload.py, and the full browser
// flow against the real backend is in frontend/e2e/upload-document.spec.ts.
vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
}));

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

beforeEach(() => {
  sessionStorage.setItem("currentSessionId", "sess-1");
  mockedApiFetch.mockReset();
  // This screen fetches both the documents list and the message history on
  // mount (AC-012); starting both empty keeps these upload-only tests
  // independent of real document/history data.
  mockedApiFetch.mockResolvedValue([]);
});

afterEach(() => {
  sessionStorage.clear();
});

describe("SessionsSessionid PDF upload", () => {
  it("[AC-013] selecting a valid PDF within the size limit is accepted and shown in the documents table", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    const before = screen.queryAllByText(/\.pdf$/).length;

    selectFile(pdfFile("research-notes.pdf", 1_000_000));

    await waitFor(() =>
      expect(screen.getByText(/was uploaded and is being processed/i)).toBeInTheDocument(),
    );
    expect(screen.getByText("research-notes.pdf")).toBeInTheDocument();
    // It was added to this session's own table, not merely announced.
    expect(screen.queryAllByText(/\.pdf$/).length).toBe(before + 1);
  });

  it("[AC-014] selecting a Word document is rejected with a PDF-only message", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    const docx = new File(["fake docx"], "report.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    selectFile(docx);

    await waitFor(() => expect(screen.getByText(/isn't a PDF/i)).toBeInTheDocument());
    expect(screen.getByText(/only PDF files are supported/i)).toBeInTheDocument();
    expect(screen.queryByText("report.docx")).not.toBeInTheDocument();
  });

  it("[AC-014] selecting a plain text file is rejected with a PDF-only message", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    const txt = new File(["just notes"], "notes.txt", { type: "text/plain" });
    selectFile(txt);

    await waitFor(() => expect(screen.getByText(/isn't a PDF/i)).toBeInTheDocument());
    expect(screen.getByText(/only PDF files are supported/i)).toBeInTheDocument();
    expect(screen.queryByText("notes.txt")).not.toBeInTheDocument();
  });

  it("[AC-014] selecting an image file is rejected with a PDF-only message", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    const image = new File(["fake png"], "scan.png", { type: "image/png" });
    selectFile(image);

    await waitFor(() => expect(screen.getByText(/isn't a PDF/i)).toBeInTheDocument());
    expect(screen.getByText(/only PDF files are supported/i)).toBeInTheDocument();
    expect(screen.queryByText("scan.png")).not.toBeInTheDocument();
  });

  it("[AC-015] selecting a PDF over the 20MB limit is rejected with the size limit stated", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    const oversized = pdfFile("huge.pdf", 21 * 1024 * 1024);
    selectFile(oversized);

    await waitFor(() =>
      expect(screen.getByText(/over the 20MB per-file limit/i)).toBeInTheDocument(),
    );
    expect(screen.queryByText("huge.pdf")).not.toBeInTheDocument();
  });

  it("[AC-015] a PDF right at the 20MB limit is accepted", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    selectFile(pdfFile("at-limit.pdf", 20 * 1024 * 1024));

    await waitFor(() =>
      expect(screen.getByText(/was uploaded and is being processed/i)).toBeInTheDocument(),
    );
    expect(screen.getByText("at-limit.pdf")).toBeInTheDocument();
  });

  it("[AC-016] once the session holds the maximum documents, the upload control is disabled and further selection is rejected", async () => {
    render(<Screen />);
    await waitFor(() => expect(mockedApiFetch).toHaveBeenCalled());

    // Starting from an empty session (the API returned no documents), add
    // five through the real control to reach the cap via real user action.
    for (const name of ["first.pdf", "second.pdf", "third.pdf", "fourth.pdf", "fifth.pdf"]) {
      selectFile(pdfFile(name, 500_000));
      await waitFor(() => expect(screen.getByText(name)).toBeInTheDocument());
    }

    const input = document.getElementById("pdf-file-input") as HTMLInputElement;
    expect(input).toBeDisabled();
    expect(screen.getByText(/Document limit reached for this session/i)).toBeInTheDocument();

    // Attempting to select a sixth file anyway must not attach it.
    selectFile(pdfFile("sixth.pdf", 500_000));
    await waitFor(() =>
      expect(screen.getByText(/already has 5 of 5 documents attached/i)).toBeInTheDocument(),
    );
    expect(screen.queryByText("sixth.pdf")).not.toBeInTheDocument();
  });
});
