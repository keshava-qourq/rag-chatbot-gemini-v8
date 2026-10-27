// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";

const PRODUCT = "Rag_chatbot_gemini_v8";
const SCREEN = "Sign Up";
const mix = (colour, percent) => `color-mix(in srgb, ${colour} ${percent}%, transparent)`;

// Demo data: an email that already has an account, so the "already exists" state can be shown.
const EXISTING_ACCOUNT_EMAILS = ["jordan.ramirez@gmail.com"];
const PASSWORD_RULE = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/;

export default function Screen() {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [emailError, setEmailError] = React.useState("");
  const [passwordError, setPasswordError] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);

  const glass = { backgroundColor: "rgba(255,255,255,0.07)", border: "1px solid rgba(255,255,255,0.14)", borderRadius: brand.radius };
  const glow = `0 20px 60px -10px ${mix(brand.primaryColor, 70)}`;

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitting(true);

    const trimmedEmail = email.trim();
    let nextEmailError = "";
    let nextPasswordError = "";

    if (!trimmedEmail) {
      nextEmailError = "Enter your email address.";
    } else if (EXISTING_ACCOUNT_EMAILS.includes(trimmedEmail.toLowerCase())) {
      nextEmailError = "An account with this email already exists. Log in instead.";
    }

    if (!password) {
      nextPasswordError = "Enter a password.";
    } else if (!PASSWORD_RULE.test(password)) {
      nextPasswordError = "Password needs at least 8 characters, including one letter and one number.";
    }

    setEmailError(nextEmailError);
    setPasswordError(nextPasswordError);

    if (!nextEmailError && !nextPasswordError) {
      navigate("sessions");
      return;
    }
    setSubmitting(false);
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden text-white" style={{ fontFamily: brand.fontBody, backgroundColor: brand.backgroundColor }}>
      <div aria-hidden className="absolute -left-32 top-[-120px] h-[520px] w-[520px] rounded-full blur-[120px]" style={{ backgroundColor: mix(brand.primaryColor, 70) }} />
      <div aria-hidden className="absolute bottom-[-160px] right-[-80px] h-[560px] w-[560px] rounded-full blur-[130px]" style={{ backgroundColor: mix(brand.accentColor, 60) }} />
      <p className="absolute left-10 top-8 text-lg font-bold" style={{ fontFamily: brand.fontHeading }}>{PRODUCT}</p>

      <main className="relative w-full max-w-[420px] p-10 backdrop-blur-2xl" style={{ ...glass, boxShadow: "0 40px 120px -20px rgba(0,0,0,0.6)" }}>
        <h1 data-wf="b-0-0" className="text-4xl font-extrabold tracking-tight" style={{ fontFamily: brand.fontHeading }}>{SCREEN}</h1>
        <p className="mt-2 text-sm text-white/65">Create your workspace, then upload documents and start asking questions about them.</p>

        <form data-wf="b-1-0" className="mt-8 space-y-4" onSubmit={handleSubmit} noValidate>
          <h2 className="text-sm font-bold uppercase tracking-wide text-white/70">Create your account</h2>

          <div>
            <label htmlFor="signup-email" className="sr-only">Email</label>
            <input
              id="signup-email"
              data-wf="i-1-0-0"
              type="email"
              required
              placeholder="Email"
              value={email}
              onChange={(e) => { setEmail(e.target.value); if (emailError) setEmailError(""); }}
              aria-invalid={emailError ? "true" : "false"}
              aria-describedby={emailError ? "signup-email-error" : undefined}
              className="h-12 w-full px-4 text-sm text-white placeholder:text-white/40 outline-none focus:ring-2"
              style={{ ...glass, ...(emailError ? { border: `1px solid ${brand.accentColor}` } : {}) }}
            />
            {emailError && (
              <p id="signup-email-error" role="alert" className="mt-1.5 text-xs font-semibold" style={{ color: brand.accentColor }}>{emailError}</p>
            )}
          </div>

          <div>
            <label htmlFor="signup-password" className="sr-only">Password</label>
            <input
              id="signup-password"
              data-wf="i-1-0-1"
              type="password"
              required
              placeholder="Password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); if (passwordError) setPasswordError(""); }}
              aria-invalid={passwordError ? "true" : "false"}
              aria-describedby="signup-password-hint"
              className="h-12 w-full px-4 text-sm text-white placeholder:text-white/40 outline-none focus:ring-2"
              style={{ ...glass, ...(passwordError ? { border: `1px solid ${brand.accentColor}` } : {}) }}
            />
            <p id="signup-password-hint" className={`mt-1.5 text-xs ${passwordError ? "font-semibold" : "text-white/50"}`} style={passwordError ? { color: brand.accentColor } : undefined} role={passwordError ? "alert" : undefined}>
              {passwordError || "At least 8 characters, with one letter and one number."}
            </p>
          </div>

          <button
            type="submit"
            data-wf="b-2-0"
            disabled={submitting}
            className="h-12 w-full text-sm font-bold text-white transition-transform hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-70"
            style={{ background: `linear-gradient(90deg, ${brand.primaryColor}, ${brand.accentColor})`, borderRadius: brand.radius, boxShadow: glow }}
          >
            {submitting ? "Creating account…" : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-white/60">
          Already have an account?{" "}
          <button type="button" data-wf="b-2-1" onClick={() => navigate("login")} className="font-bold underline-offset-4 hover:underline focus:outline-none focus:ring-2 rounded" style={{ color: brand.accentColor }}>
            Log In
          </button>
        </p>
      </main>
    </div>
  );
}
