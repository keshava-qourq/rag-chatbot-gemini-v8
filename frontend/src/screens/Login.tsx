// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import * as UI from "@/lib/ui";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";
import { apiFetch } from "@/lib/api";
import { setToken } from "@/lib/auth";

 
const { Input, Label } = UI;
 
const { Check } = Icons;

export default function Screen() {
  const navigate = useNavigate();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [touched, setTouched] = React.useState({ email: false, password: false });
  const [status, setStatus] = React.useState("idle"); // idle | loading | error
  const [errorMessage, setErrorMessage] = React.useState("");

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
  const emailError =
    touched.email && email.trim().length === 0
      ? "Enter your email address."
      : touched.email && !emailValid
        ? "Enter a valid email address."
        : "";
  const passwordError = touched.password && password.length === 0 ? "Enter your password." : "";

  async function handleSubmit(e) {
    e.preventDefault();
    setTouched({ email: true, password: true });
    setErrorMessage("");

    if (email.trim().length === 0 || !emailValid || password.length === 0) {
      return;
    }

    setStatus("loading");
    try {
      const response = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: email.trim(), password }),
      });
      setToken(response.access_token);
      setStatus("idle");
      navigate("sessions");
    } catch (err) {
      setStatus("error");
      // AC/NFR-003: show the server's generic invalid-credentials message
      // verbatim -- no local "does this email exist" check of our own.
      setErrorMessage(err?.detail || "Invalid email or password.");
    }
  }

  const inputBase = {
    backgroundColor: "rgba(255,255,255,0.06)",
    borderColor: "rgba(255,255,255,0.14)",
    color: "#f1f5fb",
    borderRadius: brand.radius,
  };

  return (
    <div
      className="min-h-screen w-full relative flex flex-col items-center px-6 py-16 overflow-hidden"
      style={{ backgroundColor: brand.backgroundColor, fontFamily: brand.fontBody }}
    >
      {/* decorative glows */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 -left-32 w-[520px] h-[520px] rounded-full"
        style={{ background: brand.primaryColor, opacity: 0.25, filter: "blur(120px)" }}
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute top-1/3 -right-40 w-[560px] h-[560px] rounded-full"
        style={{ background: brand.accentColor, opacity: 0.25, filter: "blur(140px)" }}
      />

      <div className="relative w-full max-w-5xl flex flex-col items-center">
        {/* Row 1 */}
        <h1
          data-wf="b-0-0"
          className="text-5xl font-extrabold tracking-tight text-center mb-10"
          style={{
            fontFamily: brand.fontHeading,
            backgroundImage: `linear-gradient(90deg, ${brand.primaryColor}, ${brand.accentColor})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            color: brand.primaryColor,
          }}
        >
          Log In
        </h1>

        {/* Row 2 */}
        <form
          data-wf="b-1-0"
          onSubmit={handleSubmit}
          noValidate
          className="w-full md:w-1/2 backdrop-blur-xl rounded-[16px] p-8 sm:p-10 flex flex-col gap-6"
          style={{
            backgroundColor: "rgba(255,255,255,0.07)",
            border: "1px solid rgba(255,255,255,0.14)",
            borderRadius: brand.radius,
            boxShadow: `0 40px 90px -30px rgba(0,0,0,0.6), 0 0 60px -10px ${brand.primaryColor}33`,
          }}
        >
          <div>
            <h2
              className="text-xl font-semibold mb-1"
              style={{ fontFamily: brand.fontHeading, color: "#f1f5fb" }}
            >
              Log in to your workspace
            </h2>
            <p className="text-sm" style={{ color: brand.neutralColor }}>
              Your sessions, documents and chat history are waiting right where you left them.
            </p>
          </div>

          {status === "error" && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex items-start gap-3 px-4 py-3 rounded-[16px]"
              style={{
                backgroundColor: "rgba(248,113,113,0.12)",
                border: "1px solid rgba(248,113,113,0.35)",
                borderRadius: brand.radius,
              }}
            >
              <Icons.AlertCircle
                aria-hidden="true"
                className="w-5 h-5 mt-0.5 flex-shrink-0"
                style={{ color: "#f87171" }}
              />
              <p className="text-sm" style={{ color: "#fecaca" }}>
                {errorMessage}
              </p>
            </div>
          )}

          <div className="flex flex-col gap-2">
            <Label
              htmlFor="login-email"
              className="text-sm font-medium"
              style={{ color: "#e7edf7" }}
            >
              Email
            </Label>
            <Input
              id="login-email"
              data-wf="i-1-0-0"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={() => setTouched((t) => ({ ...t, email: true }))}
              placeholder="you@company.com"
              aria-invalid={emailError ? "true" : "false"}
              aria-describedby={emailError ? "login-email-error" : undefined}
              className="h-12 px-4 border focus:outline-none focus:ring-2 focus:ring-offset-0"
              style={{ ...inputBase, "--tw-ring-color": brand.accentColor }}
            />
            {emailError && (
              <p id="login-email-error" className="text-xs" style={{ color: "#fca5a5" }}>
                {emailError}
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <Label
              htmlFor="login-password"
              className="text-sm font-medium"
              style={{ color: "#e7edf7" }}
            >
              Password
            </Label>
            <Input
              id="login-password"
              data-wf="i-1-0-1"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => setTouched((t) => ({ ...t, password: true }))}
              placeholder="Enter your password"
              aria-invalid={passwordError ? "true" : "false"}
              aria-describedby={passwordError ? "login-password-error" : undefined}
              className="h-12 px-4 border focus:outline-none focus:ring-2 focus:ring-offset-0"
              style={{ ...inputBase, "--tw-ring-color": brand.accentColor }}
            />
            {passwordError && (
              <p id="login-password-error" className="text-xs" style={{ color: "#fca5a5" }}>
                {passwordError}
              </p>
            )}
          </div>
        </form>

        {/* Row 3 */}
        <div className="w-full md:w-1/2 flex flex-wrap items-center gap-4 mt-6">
          <button
            data-wf="b-2-0"
            type="submit"
            form=""
            onClick={handleSubmit}
            disabled={status === "loading"}
            className="flex-1 min-w-[160px] h-12 px-6 rounded-[16px] font-semibold text-base flex items-center justify-center gap-2 transition-transform duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed"
            style={{
              backgroundImage: `linear-gradient(90deg, ${brand.primaryColor}, ${brand.accentColor})`,
              color: "#06142b",
              borderRadius: brand.radius,
              boxShadow: `0 18px 40px -14px ${brand.accentColor}99`,
              opacity: status === "loading" ? 0.75 : 1,
              "--tw-ring-color": brand.accentColor,
              "--tw-ring-offset-color": brand.backgroundColor,
            }}
          >
            {status === "loading" ? (
              <>
                <span
                  aria-hidden="true"
                  className="w-4 h-4 rounded-full border-2 border-transparent animate-spin"
                  style={{ borderTopColor: "#06142b", borderRightColor: "#06142b" }}
                />
                <span>Signing in…</span>
              </>
            ) : (
              "Log In"
            )}
          </button>

          <button
            data-wf="b-2-1"
            type="button"
            onClick={() => navigate("signup")}
            className="text-sm font-medium underline-offset-4 hover:underline focus:outline-none focus:ring-2 focus:ring-offset-2 rounded-md px-1 py-2"
            style={{
              color: brand.primaryColor,
              "--tw-ring-color": brand.accentColor,
              "--tw-ring-offset-color": brand.backgroundColor,
            }}
          >
            Need an account? Sign Up
          </button>
        </div>
      </div>

      <style>{`
        @media (prefers-reduced-motion: reduce) {
          .animate-spin { animation: none !important; }
        }
      `}</style>
    </div>
  );
}
