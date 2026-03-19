import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
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

const features = [
  "Unlimited math questions",
  "Daily streak tracker",
  "Questions tracker",
  "34 question templates",
  "Instant PDF download",
  "Unlimited test banks",
];

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const rawRedirect = searchParams.get("redirect") || "/dashboard";
  const redirectTo =
    rawRedirect.startsWith("/") && !rawRedirect.startsWith("//")
      ? rawRedirect
      : "/dashboard";

  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(extractErrorDetail(err, "Invalid email or password"));
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

  return (
    <div className="auth-split auth-full" style={splitStyle}>
      <div className="auth-branding" style={brandingStyle}>
        <h2 style={brandingHeadingStyle}>Welcome back</h2>
        <p style={brandingDescStyle}>
          Sign in to continue generating practice tests for your studies.
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
          <h1 style={headingStyle}>Sign In</h1>

          {error && (
            <div aria-live="polite" role="alert" style={{ color: "var(--color-error-text)", backgroundColor: "var(--color-error-bg)", padding: "var(--space-3) var(--space-4)", borderRadius: "var(--radius-md)", marginBottom: "var(--space-4)", textAlign: "center", fontSize: "var(--font-size-sm)" }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div style={{ marginBottom: "var(--space-4)" }}>
              <label htmlFor="login-email" style={{ display: "block", marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--font-size-sm)", color: "var(--text-primary)" }}>
                Email
              </label>
              <input
                id="login-email"
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <PasswordInput
              id="login-password"
              label="Password"
              value={password}
              onChange={setPassword}
            />

            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
              style={{ width: "100%", marginTop: "var(--space-2)" }}
            >
              {isSubmitting ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Google OAuth disabled until consent screen is configured
          <div style={dividerStyle}>or</div>
          <GoogleOAuthButton onClick={handleGoogleLogin} />
          */}

          <div style={{ textAlign: "center", marginTop: "var(--space-4)" }}>
            <Link to="/auth/forgot-password" className="link" style={{ fontSize: "var(--font-size-sm)" }}>
              Forgot your password?
            </Link>
          </div>

          <div style={footerStyle}>
            Don&apos;t have an account?{" "}
            <Link to="/register" className="link">
              Create one
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
