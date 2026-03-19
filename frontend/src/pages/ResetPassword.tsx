import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { authResetPassword, extractErrorDetail } from "../services/api";
import PasswordInput from "../components/Auth/PasswordInput";
import { Check } from "lucide-react";

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

const otpInputStyle: React.CSSProperties = {
  width: "100%",
  textAlign: "center",
  fontSize: "1.5rem",
  letterSpacing: "0.5em",
  fontFamily: "monospace",
  padding: "var(--space-3)",
};

const hintStyle: React.CSSProperties = {
  fontSize: "var(--font-size-xs)",
  color: "var(--text-muted)",
  marginTop: "var(--space-1)",
};

const features = [
  "Your password is checked against known breaches",
  "Minimum 8 characters required",
  "Your account stays secure",
];

export default function ResetPassword() {
  const { loginWithTokens } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const emailParam = searchParams.get("email") || "";

  const [email] = useState(emailParam);
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!emailParam && !email) {
    return (
      <div style={{ textAlign: "center", padding: "var(--space-10)" }}>
        <p>No email address provided.</p>
        <Link to="/auth/forgot-password" className="link">
          Go to Forgot Password
        </Link>
      </div>
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await authResetPassword(email, token, newPassword);
      loginWithTokens(result.access_token, result.refresh_token, result.expires_in);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(extractErrorDetail(err, "Password reset failed. Please try again."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-split auth-full" style={splitStyle}>
      <div className="auth-branding" style={brandingStyle}>
        <h2 style={brandingHeadingStyle}>Set new password</h2>
        <p style={brandingDescStyle}>
          Enter the code from your email and choose a new password.
        </p>
        <div>
          {features.map((feature) => (
            <div key={feature} style={featureBulletStyle}>
              <span style={checkIconStyle}>
                <Check size={14} color="#ffffff" />
              </span>
              {feature}
            </div>
          ))}
        </div>
      </div>

      <div style={formPanelStyle}>
        <div style={formInnerStyle}>
          <h1 style={headingStyle}>Reset Password</h1>
          <p style={descStyle}>
            Enter the 6-digit code sent to <strong>{email}</strong> and your new password.
          </p>

          {error && (
            <div aria-live="polite" role="alert" style={{ color: "var(--color-error-text)", backgroundColor: "var(--color-error-bg)", padding: "var(--space-3) var(--space-4)", borderRadius: "var(--radius-md)", marginBottom: "var(--space-4)", textAlign: "center", fontSize: "var(--font-size-sm)" }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div style={{ marginBottom: "var(--space-4)" }}>
              <label htmlFor="reset-token" style={{ display: "block", marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--font-size-sm)", color: "var(--text-primary)" }}>
                Reset Code
              </label>
              <input
                id="reset-token"
                type="text"
                inputMode="numeric"
                className="input"
                style={otpInputStyle}
                value={token}
                onChange={(e) => setToken(e.target.value.replace(/\D/g, "").slice(0, 6))}
                required
                maxLength={6}
                autoComplete="one-time-code"
                autoFocus
                placeholder="000000"
              />
              <p style={hintStyle}>Check your email for the 6-digit code</p>
            </div>

            <PasswordInput
              id="reset-new-password"
              label="New Password"
              value={newPassword}
              onChange={setNewPassword}
            />

            <div style={{ marginTop: "var(--space-4)" }}>
              <PasswordInput
                id="reset-confirm-password"
                label="Confirm New Password"
                value={confirmPassword}
                onChange={setConfirmPassword}
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting || token.length !== 6 || !newPassword || !confirmPassword}
              style={{ width: "100%", marginTop: "var(--space-4)" }}
            >
              {isSubmitting ? "Resetting..." : "Reset Password"}
            </button>
          </form>

          <div style={footerStyle}>
            <Link to="/auth/forgot-password" className="link">
              Didn&apos;t get a code? Try again
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
