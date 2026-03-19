import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import supabase from "../services/supabase";
import { useAuth } from "../context/AuthContext";

const containerStyle: React.CSSProperties = {
  maxWidth: "400px",
  margin: "var(--space-11) auto",
  padding: "0 var(--space-4)",
  textAlign: "center",
};

const linkStyle: React.CSSProperties = {
  color: "var(--color-primary-700)",
  textDecoration: "underline",
  textUnderlineOffset: "2px",
};

export default function OAuthCallback() {
  const navigate = useNavigate();
  const { loginWithTokens } = useAuth();
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function handleCallback() {
      try {
        const { data, error: sessionError } = await supabase.auth.getSession();

        if (cancelled) return;

        if (sessionError) {
          setError(sessionError.message);
          return;
        }

        if (data.session) {
          await loginWithTokens(
            data.session.access_token,
            data.session.refresh_token ?? "",
            data.session.expires_in ?? 900,
          );
          if (!cancelled) {
            navigate("/dashboard", { replace: true });
          }
        } else {
          setError("No session found. Please try signing in again.");
        }
      } catch {
        if (!cancelled) {
          setError("Something went wrong. Please try signing in again.");
        }
      }
    }

    handleCallback();
    return () => { cancelled = true; };
  }, [navigate, loginWithTokens]);

  if (error) {
    return (
      <section style={containerStyle}>
        <h1 style={{ fontSize: "var(--font-size-xl)", fontWeight: 700, color: "var(--text-primary)", marginBottom: "var(--space-4)" }}>
          Sign-in Failed
        </h1>
        <p role="alert" style={{ color: "var(--color-error-text)", backgroundColor: "var(--color-error-bg)", padding: "var(--space-3) var(--space-4)", borderRadius: "var(--radius-md)", marginBottom: "var(--space-6)" }}>
          {error}
        </p>
        <Link to="/login" style={linkStyle}>
          Back to Login
        </Link>
      </section>
    );
  }

  return (
    <section style={containerStyle} role="status" aria-label="Processing login">
      <p style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-lg)" }}>Processing login...</p>
    </section>
  );
}
