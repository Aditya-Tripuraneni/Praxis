import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: "var(--space-8)",
            textAlign: "center",
            maxWidth: "500px",
            margin: "var(--space-11) auto",
          }}
        >
          <h1 style={{ fontSize: "var(--font-size-2xl)", color: "var(--text-primary)", marginBottom: "var(--space-4)" }}>
            Something went wrong
          </h1>
          <p style={{ color: "var(--text-secondary)", marginBottom: "var(--space-6)" }}>
            An unexpected error occurred. Please try refreshing the page.
          </p>
          <button
            className="btn-primary"
            onClick={() => {
              this.setState({ hasError: false });
              window.location.href = "/";
            }}
          >
            Go to Home
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
