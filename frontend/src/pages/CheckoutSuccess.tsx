import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useSubscription } from "../context/SubscriptionContext";

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

const successHeadingStyle: React.CSSProperties = {
  fontSize: "1.75rem",
  fontWeight: 700,
  color: "var(--color-success-text)",
  marginBottom: "var(--space-4)",
};

const successCardStyle: React.CSSProperties = {
  padding: "var(--space-8) var(--space-6)",
};

const POLL_INTERVAL_MS = 2000;
const POLL_TIMEOUT_MS = 30000;

export default function CheckoutSuccess() {
  const { refreshStatus, isSubscribed } = useSubscription();
  const navigate = useNavigate();
  const [timedOut, setTimedOut] = useState(false);

  const poll = useCallback(async () => {
    try {
      await refreshStatus();
    } catch {
      // ignore polling errors, will retry
    }
  }, [refreshStatus]);

  useEffect(() => {
    if (isSubscribed) return;

    let cancelled = false;

    const intervalId = setInterval(() => {
      if (!cancelled) {
        poll();
      }
    }, POLL_INTERVAL_MS);

    const timeoutId = setTimeout(() => {
      if (!cancelled) {
        setTimedOut(true);
        clearInterval(intervalId);
      }
    }, POLL_TIMEOUT_MS);

    // Initial poll
    poll();

    return () => {
      cancelled = true;
      clearInterval(intervalId);
      clearTimeout(timeoutId);
    };
  }, [isSubscribed, poll]);

  if (isSubscribed) {
    return (
      <section style={containerStyle}>
        <div className="card" style={successCardStyle}>
          <h1 style={successHeadingStyle}>Subscribed!</h1>
          <p style={messageStyle}>
            Your subscription is now active. You can start generating practice tests right away.
          </p>
          <button
            type="button"
            className="btn-primary"
            onClick={() => navigate("/dashboard", { replace: true })}
            aria-label="Go to dashboard"
          >
            Go to Dashboard
          </button>
        </div>
      </section>
    );
  }

  if (timedOut) {
    return (
      <section style={containerStyle}>
        <h1 style={headingStyle}>Taking longer than expected</h1>
        <p style={messageStyle}>
          Your payment is being processed. This can sometimes take a minute.
          You can check your dashboard for the latest status.
        </p>
        <button
          type="button"
          className="btn-primary"
          onClick={() => navigate("/dashboard", { replace: true })}
          aria-label="Go to dashboard"
        >
          Go to Dashboard
        </button>
      </section>
    );
  }

  return (
    <section style={containerStyle}>
      <h1 style={headingStyle}>Processing your subscription...</h1>
      <p style={{ ...messageStyle, color: "var(--text-secondary)" }} aria-live="polite" role="status">
        Please wait while we confirm your payment.
      </p>
    </section>
  );
}
