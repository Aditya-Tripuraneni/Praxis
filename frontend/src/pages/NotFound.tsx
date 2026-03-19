import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div
      style={{
        padding: "var(--space-8)",
        textAlign: "center",
        maxWidth: "500px",
        margin: "var(--space-11) auto",
      }}
    >
      <h1 style={{ fontSize: "var(--font-size-4xl)", color: "var(--text-primary)", fontWeight: 700, marginBottom: "var(--space-4)" }}>404</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "var(--space-6)" }}>
        Page not found. The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <Link to="/" className="btn-primary">
        Go to Home
      </Link>
    </div>
  );
}
