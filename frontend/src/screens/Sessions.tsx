// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import * as UI from "@/lib/ui";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";
import { apiFetch } from "@/lib/api";
import { clearToken } from "@/lib/auth";

const { Button, Table, THead, TBody, TR, TH, TD, Empty } = UI;

// The session detail screen's route (unchanged by this ticket) carries no
// :sessionId segment, so the id it needs to call /sessions/{id}/messages is
// handed off here, the only place that knows which row was opened. The name
// travels alongside it so the detail screen can show the real session name
// in its heading without a second round trip to GET /sessions/{id}.
const ACTIVE_SESSION_STORAGE_KEY = "currentSessionId";
const ACTIVE_SESSION_NAME_STORAGE_KEY = "currentSessionName";

function setActiveSession(id, name) {
  try {
    sessionStorage.setItem(ACTIVE_SESSION_STORAGE_KEY, id);
    if (name) {
      sessionStorage.setItem(ACTIVE_SESSION_NAME_STORAGE_KEY, name);
    } else {
      sessionStorage.removeItem(ACTIVE_SESSION_NAME_STORAGE_KEY);
    }
  } catch (e) {
    // sessionStorage unavailable (e.g. private browsing) -- the detail
    // screen will fall back to its own empty state.
  }
}

export default function Screen() {
  const navigate = useNavigate();

  const [sessions, setSessions] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState(null);
  const [justCreatedId, setJustCreatedId] = React.useState(null);
  const [creating, setCreating] = React.useState(false);

  const loadSessions = React.useCallback(async () => {
    setLoadError(null);
    try {
      // AC-007: list only the signed-in user's sessions, newest first.
      const data = await apiFetch("/sessions", { method: "GET" });
      setSessions(data ?? []);
    } catch (err) {
      setLoadError("Couldn't load your sessions. Try refreshing the page.");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    setLoading(true);
    loadSessions();
  }, [loadSessions]);

  const formatDate = (iso) => {
    const d = new Date(iso);
    const datePart = d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
    const timePart = d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    return `${datePart} · ${timePart}`;
  };

  const handleNewSession = async () => {
    if (creating) return;
    setCreating(true);
    try {
      const newSession = await apiFetch("/sessions", {
        method: "POST",
        body: JSON.stringify({}),
      });
      setSessions((prev) => [newSession, ...prev]);
      setJustCreatedId(newSession.id);
      setActiveSession(newSession.id, newSession.name);
      navigate("sessions-sessionid");
    } catch (err) {
      setLoadError("Couldn't create a new session. Please try again.");
    } finally {
      setCreating(false);
    }
  };

  const handleOpenSession = (id, name) => {
    setActiveSession(id, name);
    navigate("sessions-sessionid");
  };

  // NFR-004: logging out must immediately invalidate the session server-side
  // (revoke the token) and clear it locally, so a stale tab can't keep making
  // authenticated requests.
  const handleLogout = async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch (e) {
      // Already-expired/invalid token, or offline -- still clear locally and
      // send the user back to /login either way.
    } finally {
      clearToken();
      navigate("login");
    }
  };

  const hairline = "rgba(255,255,255,0.13)";
  const glassFill = "rgba(255,255,255,0.07)";

  return (
    <div
      style={{
        minHeight: "100%",
        padding: "48px 32px",
        fontFamily: brand.fontBody,
        color: "#eaf2fb",
      }}
    >
      <style>{`
        @keyframes sessRowIn {
          from { opacity: 0; transform: translateY(-6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .sess-row-new { animation: sessRowIn 420ms ease-out; }
        @media (prefers-reduced-motion: reduce) {
          .sess-row-new { animation: none; }
        }
        .sess-row {
          transition: background-color 160ms ease;
        }
        .sess-row:hover {
          background-color: rgba(255,255,255,0.05);
        }
        .sess-row-link:focus-visible {
          outline: 2px solid #e879f9;
          outline-offset: -2px;
        }
        .sess-btn-primary:focus-visible,
        .sess-btn-secondary:focus-visible {
          outline: 2px solid #22d3ee;
          outline-offset: 2px;
        }
      `}</style>

      <div style={{ maxWidth: 1040, margin: "0 auto" }}>
        {/* Row 1 */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 40,
            flexWrap: "wrap",
          }}
        >
          <h1
            data-wf="b-0-0"
            style={{
              flex: "1 1 480px",
              fontFamily: brand.fontHeading,
              fontWeight: 800,
              fontSize: 40,
              lineHeight: 1.1,
              margin: 0,
              letterSpacing: "-0.02em",
              background: `linear-gradient(90deg, #ffffff 0%, ${brand.primaryColor} 120%)`,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            My Sessions
          </h1>

          <div style={{ display: "flex", gap: 12 }}>
            <Button
              data-wf="b-0-2"
              onClick={handleLogout}
              className="sess-btn-secondary"
              aria-label="Log out of your account"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "12px 20px",
                borderRadius: brand.radius,
                background: "rgba(255,255,255,0.06)",
                border: `1px solid ${hairline}`,
                color: brand.neutralColor,
                fontWeight: 600,
                fontSize: 15,
                cursor: "pointer",
              }}
            >
              <Icons.X size={16} aria-hidden="true" />
              Log Out
            </Button>

            <Button
              data-wf="b-0-1"
              onClick={handleNewSession}
              disabled={creating}
              className="sess-btn-primary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "12px 22px",
                borderRadius: brand.radius,
                border: "none",
                background: `linear-gradient(90deg, ${brand.primaryColor} 0%, ${brand.accentColor} 100%)`,
                color: "#06142b",
                fontWeight: 800,
                fontSize: 15,
                cursor: creating ? "not-allowed" : "pointer",
                opacity: creating ? 0.75 : 1,
                boxShadow: `0 0 40px 0 rgba(232,121,249,0.35), 0 0 60px 0 rgba(34,211,238,0.25)`,
              }}
            >
              <Icons.Plus size={18} aria-hidden="true" />
              New Session
            </Button>
          </div>
        </div>

        {loadError && (
          <p
            role="alert"
            style={{
              marginBottom: 20,
              fontSize: 14,
              color: "#fb7185",
            }}
          >
            {loadError}
          </p>
        )}

        {/* Row 2 + Row 3 */}
        {loading ? (
          <p style={{ fontSize: 14, color: brand.neutralColor }}>Loading sessions…</p>
        ) : sessions.length === 0 ? (
          <div
            data-wf="b-2-0"
            style={{
              borderRadius: brand.radius,
              background: glassFill,
              border: `1px solid ${hairline}`,
              backdropFilter: "blur(16px)",
              WebkitBackdropFilter: "blur(16px)",
              padding: 8,
            }}
          >
            <Empty
              title="No sessions yet"
              description="No sessions yet. Click 'New Session' to start your first conversation."
              action={
                <Button
                  onClick={handleNewSession}
                  disabled={creating}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "12px 22px",
                    borderRadius: brand.radius,
                    border: "none",
                    background: `linear-gradient(90deg, ${brand.primaryColor} 0%, ${brand.accentColor} 100%)`,
                    color: "#06142b",
                    fontWeight: 800,
                    fontSize: 15,
                    cursor: creating ? "not-allowed" : "pointer",
                  }}
                >
                  <Icons.Plus size={18} aria-hidden="true" />
                  New Session
                </Button>
              }
            />
          </div>
        ) : (
          <div
            data-wf="b-1-0"
            style={{
              borderRadius: brand.radius,
              background: glassFill,
              border: `1px solid ${hairline}`,
              backdropFilter: "blur(16px)",
              WebkitBackdropFilter: "blur(16px)",
              overflow: "hidden",
              boxShadow: "0 20px 60px 0 rgba(6,20,43,0.5)",
            }}
          >
            <Table style={{ width: "100%", borderCollapse: "collapse" }}>
              <THead>
                <TR style={{ borderBottom: `1px solid ${hairline}` }}>
                  <TH
                    data-wf="i-1-0-0"
                    style={{
                      textAlign: "left",
                      padding: "18px 24px",
                      fontSize: 13,
                      fontWeight: 700,
                      letterSpacing: "0.04em",
                      textTransform: "uppercase",
                      color: brand.neutralColor,
                    }}
                  >
                    Name
                  </TH>
                  <TH
                    data-wf="i-1-0-1"
                    style={{
                      textAlign: "left",
                      padding: "18px 24px",
                      fontSize: 13,
                      fontWeight: 700,
                      letterSpacing: "0.04em",
                      textTransform: "uppercase",
                      color: brand.neutralColor,
                      width: 260,
                    }}
                  >
                    Created At
                  </TH>
                </TR>
              </THead>
              <TBody>
                {sessions.map((s) => (
                  <TR
                    key={s.id}
                    className={`sess-row${s.id === justCreatedId ? " sess-row-new" : ""}`}
                    style={{
                      borderBottom: `1px solid ${hairline}`,
                      position: "relative",
                    }}
                  >
                    <TD style={{ padding: 0 }}>
                      <button
                        type="button"
                        data-wf={`i-1-0-0-${s.id}`}
                        className="sess-row-link"
                        onClick={() => handleOpenSession(s.id, s.name)}
                        aria-label={`Open session ${s.name ?? "Untitled Session"}`}
                        style={{
                          all: "unset",
                          position: "absolute",
                          inset: 0,
                          cursor: "pointer",
                        }}
                      />
                      <div
                        style={{
                          padding: "18px 24px",
                          display: "flex",
                          alignItems: "center",
                          gap: 12,
                          fontSize: 16,
                          fontWeight: 600,
                          color: "#f4f8ff",
                          pointerEvents: "none",
                        }}
                      >
                        <Icons.FileText
                          size={18}
                          aria-hidden="true"
                          style={{ color: brand.accentColor, flexShrink: 0 }}
                        />
                        {s.name ?? "Untitled Session"}
                        <Icons.ChevronRight
                          size={16}
                          aria-hidden="true"
                          style={{ color: brand.neutralColor, marginLeft: 4 }}
                        />
                      </div>
                    </TD>
                    <TD
                      style={{
                        padding: "18px 24px",
                        fontSize: 14,
                        color: brand.neutralColor,
                        fontVariantNumeric: "tabular-nums",
                        pointerEvents: "none",
                      }}
                    >
                      {formatDate(s.created_at)}
                    </TD>
                  </TR>
                ))}
              </TBody>
            </Table>
          </div>
        )}

        <p
          style={{
            marginTop: 24,
            fontSize: 13,
            color: brand.neutralColor,
          }}
        >
          Private to your account — other users can never see these sessions, documents, or
          conversations.
        </p>
      </div>
    </div>
  );
}
