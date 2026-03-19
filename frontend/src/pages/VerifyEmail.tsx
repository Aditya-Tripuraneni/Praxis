import { useState, useEffect, type FormEvent } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { authVerifyEmail, authResendVerification, extractErrorDetail } from "../services/api";
import { useAuth } from "../context/AuthContext";

// Style constants matching existing pages
const containerStyle: React.CSSProperties = {
  maxWidth: "400px",
  margin: "var(--space-9) auto",
  padding: "var(--space-7)",
};

const headingStyle: React.CSSProperties = {
  fontSize: "1.75rem",
  fontWeight: 700,
  color: "var(--text-primary)",
  marginBottom: "var(--space-2)",
  textAlign: "center",
};

const subtitleStyle: React.CSSProperties = {
  color: "var(--text-secondary)",
  textAlign: "center",
  marginBottom: "var(--space-7)",
  lineHeight: 1.6,
};

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated, loginWithTokens } = useAuth();
  const email = searchParams.get("email") || "";

  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resendStatus, setResendStatus] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const result = await authVerifyEmail(email, token);
      await loginWithTokens(result.access_token, result.refresh_token, result.expires_in);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(extractErrorDetail(err, "Invalid or expired code. Please try again."));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleResend() {
    setResendStatus("");
    try {
      await authResendVerification(email);
      setResendStatus("Code resent. Check your inbox.");
      setResendCooldown(60);
    } catch {
      setResendStatus("Failed to resend. Please try again.");
    }
  }

  if (!email) {
    return (
      <section className="card" style={containerStyle}>
        <h1 style={headingStyle}>Verify Your Email</h1>
        <p style={{ textAlign: "center", color: "var(--text-secondary)" }}>
          No email address provided.{" "}
          <a href="/register" className="link">Go to Register</a>
        </p>
      </section>
    );
  }

  return (
    <section className="card" style={containerStyle}>
      <h1 style={headingStyle}>Verify Your Email</h1>
      <p style={subtitleStyle}>
        We sent a 6-digit code to <strong>{email}</strong>
      </p>

      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: "var(--space-4)" }}>
          <label
            htmlFor="otp-code"
            style={{ display: "block", marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--font-size-sm)", color: "var(--text-primary)" }}
          >
            Verification Code
          </label>
          <input
            id="otp-code"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={6}
            value={token}
            onChange={(e) => {
              const val = e.target.value.replace(/\D/g, "");
              setToken(val);
            }}
            placeholder="000000"
            required
            autoComplete="one-time-code"
            style={{
              width: "100%",
              padding: "var(--space-3) var(--space-4)",
              fontSize: "var(--font-size-2xl)",
              textAlign: "center",
              letterSpacing: "0.5em",
              border: error ? "1.5px solid var(--color-error-text)" : "1.5px solid var(--color-stone-300)",
              borderRadius: "var(--radius-md)",
              boxSizing: "border-box",
              fontFamily: "monospace",
              color: "var(--text-primary)",
              background: "var(--bg-card)",
              transition: "border-color var(--transition-fast), box-shadow var(--transition-fast)",
            }}
            aria-describedby={error ? "otp-error" : undefined}
          />
        </div>

        {error && (
          <p
            id="otp-error"
            role="alert"
            aria-live="polite"
            style={{ color: "var(--color-error-text)", backgroundColor: "var(--color-error-bg)", padding: "var(--space-2) var(--space-3)", borderRadius: "var(--radius-sm)", fontSize: "var(--font-size-sm)", marginBottom: "var(--space-4)" }}
          >
            {error}
          </p>
        )}

        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting || token.length !== 6}
          style={{ width: "100%", padding: "var(--space-3)", fontSize: "var(--font-size-base)" }}
        >
          {isSubmitting ? "Verifying..." : "Verify Email"}
        </button>
      </form>

      <div style={{ marginTop: "var(--space-6)", textAlign: "center" }}>
        <div aria-live="polite" role="status">
          {resendStatus && (
            <p style={{ color: resendStatus.includes("Failed") ? "var(--color-error-text)" : "var(--text-secondary)", fontSize: "var(--font-size-sm)", marginBottom: "var(--space-2)" }}>
              {resendStatus}
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={handleResend}
          disabled={resendCooldown > 0}
          style={{
            background: "none",
            border: "none",
            color: resendCooldown > 0 ? "var(--text-muted)" : "var(--color-primary-700)",
            cursor: resendCooldown > 0 ? "not-allowed" : "pointer",
            textDecoration: "underline",
            textUnderlineOffset: "2px",
            fontSize: "var(--font-size-sm)",
            fontFamily: "var(--font-family)",
            transition: "color var(--transition-fast)",
          }}
        >
          {resendCooldown > 0 ? `Resend code (${resendCooldown}s)` : "Resend code"}
        </button>
      </div>

      <div style={{ textAlign: "center", marginTop: "var(--space-4)" }}>
        <a href="/register" className="link" style={{ fontSize: "var(--font-size-sm)" }}>
          Back to Register
        </a>
      </div>
    </section>
  );
}
