import { useState } from "react";

interface PasswordInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  minLength?: number;
  maxLength?: number;
}

export default function PasswordInput({
  id,
  label,
  value,
  onChange,
  error,
  minLength = 8,
  maxLength = 128,
}: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div style={{ marginBottom: "var(--space-4)" }}>
      <label htmlFor={id} style={{ display: "block", marginBottom: "var(--space-1)", fontWeight: 600, color: "var(--text-primary)" }}>
        {label}
      </label>
      <div style={{ position: "relative" }}>
        <input
          id={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          minLength={minLength}
          maxLength={maxLength}
          required
          aria-describedby={error ? `${id}-error` : undefined}
          style={{
            width: "100%",
            padding: "var(--space-3) var(--space-8) var(--space-3) var(--space-4)",
            border: error ? "1.5px solid var(--color-error-text)" : "1.5px solid var(--color-stone-300)",
            borderRadius: "var(--radius-md)",
            fontSize: "var(--font-size-base)",
            fontFamily: "var(--font-family)",
            boxSizing: "border-box",
            color: "var(--text-primary)",
            backgroundColor: "var(--bg-card)",
            transition: "border-color var(--transition-fast), box-shadow var(--transition-fast)",
            outline: "none",
          }}
        />
        <button
          type="button"
          onClick={() => setVisible(!visible)}
          aria-label={visible ? "Hide password" : "Show password"}
          style={{
            position: "absolute",
            right: "var(--space-2)",
            top: "50%",
            transform: "translateY(-50%)",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: "var(--font-size-sm)",
            color: "var(--text-secondary)",
            fontFamily: "var(--font-family)",
            fontWeight: 500,
            padding: "var(--space-1) var(--space-2)",
          }}
        >
          {visible ? "Hide" : "Show"}
        </button>
      </div>
      {error && (
        <p id={`${id}-error`} role="alert" style={{ color: "var(--color-error-text)", fontSize: "var(--font-size-sm)", marginTop: "var(--space-1)" }}>
          {error}
        </p>
      )}
    </div>
  );
}
