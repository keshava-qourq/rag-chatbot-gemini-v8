// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.

import React from "react";

import * as UI from "@/lib/ui";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";
import { apiFetch } from "@/lib/api";

const { Button, Input, Label, Table, THead, TBody, TR, TH, TD, Empty } = UI;

// This screen's route carries no :sessionId segment (see App.tsx), so the id
// of the session that was opened travels via sessionStorage, set by
// Sessions.tsx right before it navigates here.
const ACTIVE_SESSION_STORAGE_KEY = "currentSessionId";

const MAX_DOCS = 5;
const MAX_SIZE_BYTES = 20 * 1024 * 1024;

const glassStyle = {
  borderRadius: brand.radius,
  background: "rgba(255,255,255,0.07)",
  border: "1px solid rgba(255,255,255,0.14)",
  backdropFilter: "blur(20px)",
  WebkitBackdropFilter: "blur(20px)",
};

function formatBytes(bytes) {
  if (bytes == null) return "—";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

function formatTime(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function StatusBadge({ status }) {
  const map = {
    ready: { label: "Ready", Icon: Icons.CheckCircle, color: "#34d399" },
    processing: { label: "Processing", Icon: Icons.Clock, color: "#fbbf24" },
    failed: { label: "Failed", Icon: Icons.AlertCircle, color: "#fb7185" },
  };
  const cfg = map[status] || map.processing;
  const Icon = cfg.Icon;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
      style={{
        color: cfg.color,
        background: `${cfg.color}1f`,
        border: `1px solid ${cfg.color}40`,
      }}
    >
      <Icon size={13} aria-hidden="true" />
      {cfg.label}
    </span>
  );
}

// Turns the flat, chronological message list the API returns into
// question/answer pairs for rendering. The backend always writes a user
// message immediately followed by its assistant reply (sessions.py
// create_message), so consecutive pairing is safe; a dangling user message
// with no reply yet (a request in flight) is rendered as pending.
function buildExchangesFromMessages(messages) {
  const result = [];
  let i = 0;
  while (i < messages.length) {
    const m = messages[i];
    if (m.role === "user") {
      const next = messages[i + 1];
      if (next && next.role === "assistant") {
        result.push({
          id: next.id,
          question: m.content,
          answer: next.content,
          citations: next.citations ?? [],
          created_at: next.created_at,
        });
        i += 2;
        continue;
      }
      result.push({
        id: m.id,
        question: m.content,
        answer: null,
        citations: [],
        created_at: m.created_at,
        pending: true,
      });
      i += 1;
      continue;
    }
    i += 1;
  }
  return result;
}

// apiFetch only surfaces a generic `Error` whose message ends in the HTTP
// status code (see lib/api.ts) -- pull that back out so we can branch on it.
function extractStatus(error) {
  const match = /(\d{3})\s*$/.exec(error?.message ?? "");
  return match ? Number(match[1]) : null;
}

function readActiveSessionId() {
  try {
    return sessionStorage.getItem(ACTIVE_SESSION_STORAGE_KEY);
  } catch {
    return null;
  }
}

export default function Screen() {
  const navigate = useNavigate();
  const [sessionId] = React.useState(readActiveSessionId);

  // AC-012: this session's real documents, fetched once from the API when
  // the session is opened -- never a seeded/sample list, and never carried
  // over from a previously viewed session (sessionId is read once per mount,
  // and the detail screen is remounted each time Sessions.tsx opens a row).
  const [documents, setDocuments] = React.useState([]);
  const [documentsLoading, setDocumentsLoading] = React.useState(true);
  const [documentsError, setDocumentsError] = React.useState(null);
  const [exchanges, setExchanges] = React.useState([]);
  const [historyLoading, setHistoryLoading] = React.useState(true);
  const [historyError, setHistoryError] = React.useState(null);
  const [question, setQuestion] = React.useState("");
  const [asking, setAsking] = React.useState(false);
  const [askWarning, setAskWarning] = React.useState(null);
  const [askError, setAskError] = React.useState(null);
  const [uploadMessage, setUploadMessage] = React.useState(null);
  const [uploadIsError, setUploadIsError] = React.useState(false);
  const [uploading, setUploading] = React.useState(false);
  const idCounter = React.useRef(0);
  const fileInputRef = React.useRef(null);

  function nextId(prefix) {
    idCounter.current += 1;
    return `${prefix}-${Date.now()}-${idCounter.current}`;
  }

  function resetFileInput() {
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function rejectUpload(message) {
    setUploadIsError(true);
    setUploadMessage(message);
    resetFileInput();
  }

  const loadDocuments = React.useCallback(async () => {
    if (!sessionId) {
      setDocumentsLoading(false);
      return;
    }
    setDocumentsError(null);
    try {
      // AC-012: only this session's real documents from the API -- no
      // seeded/sample array, and nothing carried over from another session.
      const docs = await apiFetch(`/sessions/${sessionId}/documents`, { method: "GET" });
      setDocuments(docs ?? []);
    } catch {
      setDocumentsError("Couldn't load documents. Try refreshing the page.");
    } finally {
      setDocumentsLoading(false);
    }
  }, [sessionId]);

  React.useEffect(() => {
    setDocumentsLoading(true);
    loadDocuments();
  }, [loadDocuments]);

  const loadHistory = React.useCallback(async () => {
    if (!sessionId) {
      setHistoryLoading(false);
      return;
    }
    setHistoryError(null);
    try {
      const messages = await apiFetch(`/sessions/${sessionId}/messages`, { method: "GET" });
      setExchanges(buildExchangesFromMessages(messages ?? []));
    } catch {
      setHistoryError("Couldn't load the conversation history. Try refreshing the page.");
    } finally {
      setHistoryLoading(false);
    }
  }, [sessionId]);

  React.useEffect(() => {
    setHistoryLoading(true);
    loadHistory();
  }, [loadHistory]);

  async function handleFileChange(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    setUploadIsError(false);

    // Fast local guard only -- the backend remains the source of truth for
    // what's actually accepted, stored and queued (AC-031).
    const isPdf = file.type === "application/pdf" || /\.pdf$/i.test(file.name);
    if (!isPdf) {
      rejectUpload(`"${file.name}" isn't a PDF. Only PDF files are supported for this session.`);
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      rejectUpload(
        `"${file.name}" is ${formatBytes(file.size)}, which is over the 20MB per-file limit.`,
      );
      return;
    }
    if (documents.length >= MAX_DOCS) {
      rejectUpload(
        `This session already has ${MAX_DOCS} of ${MAX_DOCS} documents attached, the maximum allowed. Open a new session to add more.`,
      );
      return;
    }
    if (!sessionId) return;

    setUploading(true);
    try {
      // AC-031: a true multipart request to the real upload endpoint -- no
      // client-only simulated document object.
      const formData = new FormData();
      formData.append("file", file);
      const created = await apiFetch(`/sessions/${sessionId}/documents`, {
        method: "POST",
        body: formData,
      });
      // AC-032: the new row comes straight from the backend response
      // (including its real status, e.g. 'processing'), not a local placeholder.
      setDocuments((prev) => [...prev, created]);
      setUploadIsError(false);
      setUploadMessage(`"${file.name}" was uploaded and is being processed.`);
      resetFileInput();
    } catch (err) {
      rejectUpload(
        err?.detail || `"${file.name}" couldn't be uploaded. Please try again.`,
      );
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(e) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || !sessionId) return;

    setAskWarning(null);
    setAskError(null);

    const pendingId = nextId("ex");
    setExchanges((prev) => [
      ...prev,
      {
        id: pendingId,
        question: trimmed,
        answer: null,
        citations: [],
        created_at: new Date().toISOString(),
        pending: true,
      },
    ]);
    setQuestion("");
    setAsking(true);

    try {
      await apiFetch(`/sessions/${sessionId}/messages`, {
        method: "POST",
        body: JSON.stringify({ question: trimmed }),
      });
      await loadHistory();
    } catch (err) {
      setExchanges((prev) => prev.filter((ex) => ex.id !== pendingId));
      setQuestion(trimmed);
      const status = extractStatus(err);
      if (status === 422) {
        setAskWarning(
          "No ready documents yet. Upload a PDF above and wait for it to finish processing before asking a question.",
        );
      } else {
        setAskError("The answer could not be generated right now. Please try again in a moment.");
      }
    } finally {
      setAsking(false);
    }
  }

  return (
    <div
      className="min-h-full w-full px-4 py-6 md:px-8 md:py-8"
      style={{ fontFamily: brand.fontBody, color: "#e7edf6" }}
    >
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        {/* Row 1 */}
        <div className="flex items-start gap-4">
          <button
            type="button"
            data-wf="b-0-0"
            aria-label="Back to sessions"
            onClick={() => navigate("sessions")}
            className="mt-1 flex h-11 w-11 flex-none items-center justify-center rounded-full transition-colors duration-150 hover:bg-white/10 focus:outline-none focus-visible:ring-2"
            style={{
              border: "1px solid rgba(255,255,255,0.16)",
              ["--tw-ring-color"]: brand.primaryColor,
            }}
          >
            <Icons.ArrowLeft size={18} aria-hidden="true" />
          </button>
          <h1
            data-wf="b-0-1"
            className="text-3xl font-bold leading-tight md:text-4xl"
            style={{ fontFamily: brand.fontHeading }}
          >
            Session: Research Papers
          </h1>
        </div>

        {/* Row 2 */}
        <div className="grid grid-cols-1 gap-5 md:grid-cols-12">
          {/* Documents table */}
          <section
            data-wf="b-1-0"
            className="md:col-span-5 p-5"
            style={glassStyle}
            aria-labelledby="documents-heading"
          >
            <h2
              id="documents-heading"
              className="mb-3 text-lg font-semibold"
              style={{ fontFamily: brand.fontHeading }}
            >
              Documents
            </h2>
            {documentsLoading ? (
              <p className="flex items-center gap-2 text-sm" style={{ color: brand.neutralColor }}>
                <Icons.Clock size={14} aria-hidden="true" />
                Loading documents…
              </p>
            ) : documentsError ? (
              <p
                role="alert"
                className="flex items-center gap-2 text-sm"
                style={{ color: "#fb7185" }}
              >
                <Icons.AlertCircle size={15} aria-hidden="true" />
                {documentsError}
              </p>
            ) : documents.length === 0 ? (
              <Empty title="No documents yet" description="Upload a PDF below to get started." />
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <THead>
                    <TR>
                      <TH data-wf="i-1-0-0" scope="col">
                        Filename
                      </TH>
                      <TH data-wf="i-1-0-1" scope="col">
                        Status
                      </TH>
                      <TH data-wf="i-1-0-2" scope="col" className="text-right">
                        Pages
                      </TH>
                      <TH data-wf="i-1-0-3" scope="col" className="text-right">
                        Uploaded
                      </TH>
                    </TR>
                  </THead>
                  <TBody>
                    {documents.map((doc) => (
                      <TR key={doc.id}>
                        <TD>
                          <div className="flex flex-col">
                            <span className="font-medium" style={{ color: "#f3f6fb" }}>
                              {doc.filename}
                            </span>
                            <span className="text-xs" style={{ color: brand.neutralColor }}>
                              {formatBytes(doc.size_bytes)}
                            </span>
                            {doc.status === "failed" && doc.error_message && (
                              <span
                                className="mt-1 max-w-[220px] text-xs"
                                style={{ color: "#fb7185" }}
                              >
                                {doc.error_message}
                              </span>
                            )}
                          </div>
                        </TD>
                        <TD>
                          <StatusBadge status={doc.status} />
                        </TD>
                        <TD className="text-right tabular-nums">{doc.page_count ?? "—"}</TD>
                        <TD className="text-right tabular-nums text-xs">
                          {formatTime(doc.created_at)}
                        </TD>
                      </TR>
                    ))}
                  </TBody>
                </Table>
              </div>
            )}
          </section>

          {/* Upload form */}
          <section
            data-wf="b-1-1"
            className="md:col-span-4 p-5"
            style={glassStyle}
            aria-labelledby="upload-heading"
          >
            <h2
              id="upload-heading"
              className="mb-3 text-lg font-semibold"
              style={{ fontFamily: brand.fontHeading }}
            >
              Upload PDF
            </h2>
            <form onSubmit={(e) => e.preventDefault()} className="flex flex-col gap-3">
              <div>
                <Label
                  htmlFor="pdf-file-input"
                  className="mb-1.5 block text-sm"
                  style={{ color: brand.neutralColor }}
                >
                  Select PDF file (max 20MB)
                </Label>
                <input
                  id="pdf-file-input"
                  data-wf="i-1-1-0"
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={handleFileChange}
                  disabled={documents.length >= MAX_DOCS || uploading}
                  className="block w-full text-sm file:mr-3 file:rounded-full file:border-0 file:px-4 file:py-2 file:text-sm file:font-medium focus:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50"
                  style={{
                    color: brand.neutralColor,
                    ["--tw-ring-color"]: brand.accentColor,
                  }}
                />
              </div>
              {documents.length >= MAX_DOCS && (
                <p className="text-xs" style={{ color: "#fbbf24" }}>
                  Document limit reached for this session. Open a new session to upload more.
                </p>
              )}
              {uploadMessage && (
                <p
                  role="status"
                  aria-live="polite"
                  className="flex items-start gap-1.5 text-xs"
                  style={{ color: uploadIsError ? "#fb7185" : "#34d399" }}
                >
                  {uploadIsError ? (
                    <Icons.AlertCircle size={14} className="mt-0.5 flex-none" aria-hidden="true" />
                  ) : (
                    <Icons.CheckCircle size={14} className="mt-0.5 flex-none" aria-hidden="true" />
                  )}
                  {uploadMessage}
                </p>
              )}
            </form>
          </section>

          {/* Helper text */}
          <aside data-wf="b-1-2" className="md:col-span-3 flex items-center p-5" style={glassStyle}>
            <p className="text-sm leading-relaxed" style={{ color: brand.neutralColor }}>
              <span className="font-semibold tabular-nums" style={{ color: "#f3f6fb" }}>
                {documents.length} of {MAX_DOCS}
              </span>{" "}
              documents attached. PDF only, 20MB limit per file.
            </p>
          </aside>
        </div>

        {/* Row 3 */}
        <section
          data-wf="b-2-0"
          className="p-5 md:p-6"
          style={glassStyle}
          aria-labelledby="history-heading"
        >
          <h2
            id="history-heading"
            className="mb-4 text-lg font-semibold"
            style={{ fontFamily: brand.fontHeading }}
          >
            Conversation History
          </h2>
          {historyLoading ? (
            <p className="flex items-center gap-2 text-sm" style={{ color: brand.neutralColor }}>
              <Icons.Clock size={14} aria-hidden="true" />
              Loading conversation history…
            </p>
          ) : historyError ? (
            <p
              role="alert"
              className="flex items-center gap-2 text-sm"
              style={{ color: "#fb7185" }}
            >
              <Icons.AlertCircle size={15} aria-hidden="true" />
              {historyError}
            </p>
          ) : exchanges.length === 0 ? (
            <Empty
              title="No questions asked yet"
              description="Once a document finishes processing, ask something about it below and the answer, with citations, will show up here."
            />
          ) : (
            <ul className="flex flex-col gap-4">
              {exchanges.map((ex, idx) => {
                const wfId = idx < 3 ? ["i-2-0-0", "i-2-0-1", "i-2-0-2"][idx] : undefined;
                return (
                  <li
                    key={ex.id}
                    data-wf={wfId}
                    className="rounded-2xl p-4 transition-opacity duration-300"
                    style={{
                      borderRadius: brand.radius,
                      background: "rgba(255,255,255,0.04)",
                      border: "1px solid rgba(255,255,255,0.10)",
                    }}
                  >
                    <p className="text-sm font-semibold" style={{ color: "#f3f6fb" }}>
                      <span style={{ color: brand.primaryColor }}>Q:</span> {ex.question}
                    </p>
                    {ex.pending ? (
                      <p
                        className="mt-2 flex items-center gap-2 text-sm animate-pulse motion-reduce:animate-none"
                        style={{ color: brand.neutralColor }}
                      >
                        <Icons.Clock size={14} aria-hidden="true" />
                        Searching ready documents…
                      </p>
                    ) : (
                      <>
                        <p className="mt-2 text-sm leading-relaxed" style={{ color: "#dfe7f2" }}>
                          <span style={{ color: brand.accentColor }}>A:</span> {ex.answer}
                        </p>
                        {ex.citations.length > 0 && (
                          <div className="mt-2.5 flex flex-wrap gap-2">
                            {ex.citations.map((c) => (
                              <span
                                key={c.id ?? `${c.filename}-${c.page_number}`}
                                className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs"
                                style={{
                                  color: brand.primaryColor,
                                  background: `${brand.primaryColor}14`,
                                  border: `1px solid ${brand.primaryColor}3a`,
                                }}
                              >
                                <Icons.FileText size={12} aria-hidden="true" />
                                {c.filename}
                                {c.page_number != null ? `, p.${c.page_number}` : ""}
                              </span>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                    <p className="mt-2 text-xs" style={{ color: brand.neutralColor }}>
                      {formatTime(ex.created_at)}
                    </p>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        {/* Row 4 */}
        <div>
          {askWarning && (
            <p
              role="alert"
              className="mb-2 flex items-center gap-2 text-sm"
              style={{ color: "#fbbf24" }}
            >
              <Icons.AlertCircle size={15} aria-hidden="true" />
              {askWarning}
            </p>
          )}
          {askError && (
            <p
              role="alert"
              className="mb-2 flex items-center gap-2 text-sm"
              style={{ color: "#fb7185" }}
            >
              <Icons.AlertCircle size={15} aria-hidden="true" />
              {askError}
            </p>
          )}
          <form
            data-wf="b-3-0"
            onSubmit={handleAsk}
            className="grid grid-cols-1 gap-3 p-3 md:grid-cols-12 md:items-end"
            style={{
              ...glassStyle,
              boxShadow: `0 0 70px -20px ${brand.accentColor}70`,
            }}
          >
            <div className="md:col-span-10">
              <Label htmlFor="question-input" className="sr-only">
                Ask a question about your documents
              </Label>
              <Input
                id="question-input"
                data-wf="i-3-0-0"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your documents..."
                autoComplete="off"
                className="w-full focus:outline-none focus-visible:ring-2"
                style={{
                  borderRadius: brand.radius,
                  background: "rgba(255,255,255,0.06)",
                  border: "1px solid rgba(255,255,255,0.18)",
                  color: "#f3f6fb",
                  ["--tw-ring-color"]: brand.primaryColor,
                }}
              />
            </div>
            <div className="md:col-span-2">
              <Button
                type="submit"
                data-wf="b-3-1"
                disabled={asking || question.trim().length === 0}
                className="flex w-full items-center justify-center gap-2 font-semibold transition-transform duration-150 focus:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-60"
                style={{
                  borderRadius: brand.radius,
                  background: `linear-gradient(135deg, ${brand.primaryColor}, ${brand.accentColor})`,
                  color: "#061018",
                  padding: "0.7rem 1rem",
                  ["--tw-ring-color"]: brand.accentColor,
                }}
              >
                {asking ? (
                  <>Thinking…</>
                ) : (
                  <>
                    Send
                    <Icons.ArrowRight size={15} aria-hidden="true" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
