import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { extractErrorDetail } from "../services/api";
import PasswordInput from "../components/Auth/PasswordInput";
import { Check } from "lucide-react";
// Google OAuth disabled until consent screen is configured
// import GoogleOAuthButton from "../components/Auth/GoogleOAuthButton";

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
  marginBottom: "var(--space-6)",
};

// Google OAuth disabled — dividerStyle unused until re-enabled
// const dividerStyle: React.CSSProperties = {
//   textAlign: "center",
//   margin: "20px 0",
//   color: "var(--text-muted)",
//   fontSize: "var(--font-size-sm)",
// };

const footerStyle: React.CSSProperties = {
  textAlign: "center",
  marginTop: "var(--space-6)",
  fontSize: "var(--font-size-sm)",
  color: "var(--text-secondary)",
};

const hintStyle: React.CSSProperties = {
  fontSize: "var(--font-size-xs)",
  color: "var(--text-secondary)",
  marginTop: "-12px",
  marginBottom: "var(--space-4)",
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

const pricingCardStyle: React.CSSProperties = {
  backgroundColor: "rgba(255, 255, 255, 0.08)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-4)",
  marginTop: "var(--space-6)",
};

const formInnerStyle: React.CSSProperties = {
  maxWidth: "400px",
  width: "100%",
  margin: "0 auto",
};

const features = [
  "Unlimited math questions",
  "Daily streak tracker",
  "Questions tracker",
  "34 question templates",
  "Instant PDF download",
  "Unlimited test banks",
];

export default function Register() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [confirmError, setConfirmError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setConfirmError("");

    if (password !== confirmPassword) {
      setConfirmError("Passwords do not match");
      return;
    }

    setIsSubmitting(true);

    try {
      const message = await register(email, password);
      setSuccessMessage(message);
    } catch (err) {
      setError(extractErrorDetail(err, "Registration failed. Please try again."));
    } finally {
      setIsSubmitting(false);
    }
  }

  // Google OAuth disabled until consent screen is configured
  // async function handleGoogleLogin() {
  //   try {
  //     await loginWithGoogle();
  //   } catch {
  //     setError("Google sign-in failed. Please try again.");
  //   }
  // }

  const brandingPanel = (
    <div className="auth-branding" style={brandingStyle}>
      <h2 style={brandingHeadingStyle}>Start practicing</h2>
      <p style={brandingDescStyle}>
        Create your account and get access to unlimited math practice tests.
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
      <div style={pricingCardStyle}>
        <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#ffffff" }}>
          $4.99/month
        </div>
        <div style={{ fontSize: "0.75rem", color: "#99f6e4", marginTop: "var(--space-1)" }}>
          Cancel anytime
        </div>
      </div>
    </div>
  );

  if (successMessage) {
    return (
      <div className="auth-split auth-full" style={splitStyle}>
        {brandingPanel}
        <div style={formPanelStyle}>
          <div style={formInnerStyle}>
            <h1 style={{ ...headingStyle, color: "var(--color-success-text)" }}>Check Your Email</h1>
            <p style={{ textAlign: "center", color: "var(--text-secondary)", marginBottom: "var(--space-6)", lineHeight: 1.6 }}>
              We sent a 6-digit verification code to <strong>{email}</strong>
            </p>
            <div style={{ textAlign: "center" }}>
              <button
                type="button"
                className="btn-primary"
                onClick={() => navigate(`/auth/verify-email?email=${encodeURIComponent(email)}`)}
                style={{ padding: "var(--space-3) var(--space-7)" }}
              >
                Enter Verification Code
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-split auth-full" style={splitStyle}>
      {brandingPanel}

      <div style={formPanelStyle}>
        <div style={formInnerStyle}>
          <h1 style={headingStyle}>Create Account</h1>

          {error && (
            <div aria-live="polite" role="alert" style={{ color: "var(--color-error-text)", backgroundColor: "var(--color-error-bg)", padding: "var(--space-3) var(--space-4)", borderRadius: "var(--radius-md)", marginBottom: "var(--space-4)", textAlign: "center", fontSize: "var(--font-size-sm)" }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div style={{ marginBottom: "var(--space-4)" }}>
              <label htmlFor="register-email" style={{ display: "block", marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--font-size-sm)", color: "var(--text-primary)" }}>
                Email
              </label>
              <input
                id="register-email"
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <PasswordInput
              id="register-password"
              label="Password"
              value={password}
              onChange={setPassword}
            />
            <p style={hintStyle}>Minimum 8 characters</p>

            <PasswordInput
              id="register-confirm-password"
              label="Confirm Password"
              value={confirmPassword}
              onChange={setConfirmPassword}
              error={confirmError}
            />

            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
              style={{ width: "100%", marginTop: "var(--space-2)" }}
            >
              {isSubmitting ? "Creating account..." : "Create Account"}
            </button>
          </form>

          {/* Google OAuth disabled until consent screen is configured
          <div style={dividerStyle}>or</div>
          <GoogleOAuthButton label="Sign up with Google" onClick={handleGoogleLogin} />
          */}

          <div style={footerStyle}>
            Already have an account?{" "}
            <Link to="/login" className="link">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
