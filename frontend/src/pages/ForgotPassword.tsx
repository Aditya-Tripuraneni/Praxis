import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { Check } from "lucide-react";
import { authForgotPassword, extractErrorDetail } from "../services/api";

const splitStyle: React.CSSProperties = {
  display: "flex",
  minHeight: "100%",
};

const brandingStyle: React.CSSProperties = {
  flex: "0 0 38%",
  background: "linear-gradient(180deg, #134e4a 0%, #0d9488 100%)",
  padding: "var(--space-9) var(--space-7)",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  color: "#ffffff",
};

const formPanelStyle: React.CSSProperties = {
  flex: 1,
  padding: "var(--space-9) var(--space-7)",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  backgroundColor: "#ffffff",
};

const headingStyle: React.CSSProperties = {
  fontSize: "1.75rem",
  fontWeight: 700,
  color: "var(--color-primary-900)",
  marginBottom: "var(--space-3)",
};

const descStyle: React.CSSProperties = {
  fontSize: "var(--font-size-sm)",
  color: "var(--text-secondary)",
  marginBottom: "var(--space-6)",
  lineHeight: 1.6,
};

const footerStyle: React.CSSProperties = {
  textAlign: "center",
  marginTop: "var(--space-6)",
  fontSize: "var(--font-size-sm)",
  color: "var(--text-secondary)",
};

const brandingHeadingStyle: React.CSSProperties = {
  fontSize: "1.75rem",
  fontWeight: 800,
  color: "#ffffff",
  marginBottom: "var(--space-4)",
};

const brandingDescStyle: React.CSSProperties = {
  color: "#99f6e4",
  marginBottom: "var(--space-6)",
  lineHeight: 1.6,
};

const featureBulletStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "var(--space-3)",
  marginBottom: "var(--space-3)",
  fontSize: "var(--font-size-sm)",
};

const checkIconStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  width: "24px",
  height: "24px",
  borderRadius: "50%",
  backgroundColor: "rgba(255, 255, 255, 0.15)",
  flexShrink: 0,
};

const formInnerStyle: React.CSSProperties = {
  maxWidth: "400px",
  width: "100%",
  margin: "0 auto",
};

const successStyle: React.CSSProperties = {
  backgroundColor: "var(--color-primary-50)",
  border: "1px solid var(--color-primary-200)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-5)",
  textAlign: "center",
  lineHeight: 1.6,
};

const steps = [
  "Enter your email address",
  "Check your inbox for a 6-digit code",
  "Set a new password",
];

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await authForgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(extractErrorDetail(err, "Something went wrong. Please try again."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-split auth-full" style={splitStyle}>
      <div className="auth-branding" style={brandingStyle}>
        <h2 style={brandingHeadingStyle}>Reset your password</h2>
        <p style={brandingDescStyle}>
          Follow these steps to regain access to your account.
        </p>
        <div>
          {steps.map((step, i) => (
            <div key={step} style={featureBulletStyle}>
              <span style={checkIconStyle}>
                <Check size={14} color="#ffffff" />
              </span>
              {i + 1}. {step}
            </div>
          ))}
        </div>
      </div>

      <div style={formPanelStyle}>
        <div style={formInnerStyle}>
          <h1 style={headingStyle}>Forgot Password</h1>
          <p style={descStyle}>
            Enter your email and we&apos;ll send you a code to reset your password.
          </p>

          {sent ? (
            <div style={successStyle}>
              <p style={{ fontWeight: 600, color: "var(--color-primary-700)", marginBottom: "var(--space-3)" }}>
                Check your email
              </p>
              <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)" }}>
                If an account exists for <strong>{email}</strong>, we sent a 6-digit reset code.
                Check your inbox (and spam folder).
              </p>
              <Link
                to={`/auth/reset-password?email=${encodeURIComponent(email)}`}
                className="btn-primary"
                style={{ display: "inline-block", marginTop: "var(--space-5)" }}
              >
                Enter Reset Code
              </Link>
            </div>
          ) : (
            <>
              {error && (
                <div aria-live="polite" role="alert" style={{ color: "var(--color-error-text)", backgroundColor: "var(--color-error-bg)", padding: "var(--space-3) var(--space-4)", borderRadius: "var(--radius-md)", marginBottom: "var(--space-4)", textAlign: "center", fontSize: "var(--font-size-sm)" }}>
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} noValidate>
                <div style={{ marginBottom: "var(--space-4)" }}>
                  <label htmlFor="forgot-email" style={{ display: "block", marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--font-size-sm)", color: "var(--text-primary)" }}>
                    Email
                  </label>
                  <input
                    id="forgot-email"
                    type="email"
                    className="input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    autoFocus
                  />
                </div>

                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isSubmitting || !email}
                  style={{ width: "100%", marginTop: "var(--space-2)" }}
                >
                  {isSubmitting ? "Sending..." : "Send Reset Code"}
                </button>
              </form>
            </>
          )}

          <div style={footerStyle}>
            <Link to="/login" className="link">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
