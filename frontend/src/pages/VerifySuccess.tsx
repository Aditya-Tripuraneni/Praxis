import { Link } from "react-router-dom";

const containerStyle: React.CSSProperties = {
  maxWidth: "400px",
  margin: "var(--space-11) auto",
  padding: "var(--space-7)",
  textAlign: "center",
};

export default function VerifySuccess() {
  return (
    <section className="card" style={containerStyle}>
      <h1 style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "var(--space-4)" }}>Email verified successfully!</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "var(--space-6)", lineHeight: 1.6 }}>
        Your email has been verified. You can now sign in to your account.
      </p>
      <Link to="/login" className="link" style={{ fontSize: "var(--font-size-base)" }}>
        Go to Login
      </Link>
    </section>
  );
}
