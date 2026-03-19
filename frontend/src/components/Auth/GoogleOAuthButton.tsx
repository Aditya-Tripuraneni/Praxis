interface GoogleOAuthButtonProps {
  label?: string;
  onClick: () => void;
  disabled?: boolean;
}

export default function GoogleOAuthButton({
  label = "Sign in with Google",
  onClick,
  disabled = false,
}: GoogleOAuthButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      style={{
        width: "100%",
        padding: "var(--space-3) var(--space-4)",
        border: "1.5px solid var(--color-stone-300)",
        borderRadius: "var(--radius-md)",
        backgroundColor: "var(--bg-card)",
        cursor: disabled ? "not-allowed" : "pointer",
        fontSize: "var(--font-size-base)",
        fontFamily: "var(--font-family)",
        fontWeight: 500,
        minHeight: "44px",
        color: disabled ? "var(--color-stone-300)" : "var(--text-primary)",
        transition: "background-color var(--transition-fast), border-color var(--transition-fast)",
      }}
    >
      {label}
    </button>
  );
}
