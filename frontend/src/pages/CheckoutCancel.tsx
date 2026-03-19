import { useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { useSubscription } from "../context/SubscriptionContext";
import { extractErrorDetail } from "../services/api";

const containerStyle: React.CSSProperties = {
  maxWidth: "500px",
  margin: "0 auto",
  padding: "var(--space-9) var(--space-4)",
  textAlign: "center",
};

const headingStyle: React.CSSProperties = {
  fontSize: "1.75rem",
  fontWeight: 700,
  color: "var(--text-primary)",
  marginBottom: "var(--space-4)",
};

const messageStyle: React.CSSProperties = {
  fontSize: "var(--font-size-base)",
  color: "var(--text-secondary)",
  marginBottom: "var(--space-6)",
  lineHeight: 1.6,
};

const actionsStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "var(--space-3)",
};

const errorBoxStyle: React.CSSProperties = {
  color: "var(--color-error-text)",
  backgroundColor: "var(--color-error-bg)",
  border: "1px solid var(--color-error-border)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-3) var(--space-4)",
  marginBottom: "var(--space-4)",
  fontSize: "var(--font-size-sm)",
};

export default function CheckoutCancel() {
  const { subscribe } = useSubscription();
  const [error, setError] = useState("");

  const handleTryAgain = useCallback(async () => {
    setError("");
    try {
      await subscribe("student");
    } catch (err) {
      setError(extractErrorDetail(err, "Failed to start checkout. Please try again."));
    }
  }, [subscribe]);

  return (
    <section style={containerStyle}>
      <h1 style={headingStyle}>Checkout cancelled</h1>
      <p style={messageStyle}>
        No charges were made. You can try again whenever you are ready.
      </p>

      {error && (
        <div aria-live="polite" role="alert" style={errorBoxStyle}>
          {error}
        </div>
      )}

      <div style={actionsStyle}>
        <button
          type="button"
          className="btn-primary"
          onClick={handleTryAgain}
          aria-label="Try subscribing again"
        >
          Try Again
        </button>
        <Link to="/dashboard" className="link">
          Back to Dashboard
        </Link>
      </div>
    </section>
  );
}
