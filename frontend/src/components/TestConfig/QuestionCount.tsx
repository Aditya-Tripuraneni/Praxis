import { useEffect, useState } from "react";

interface QuestionCountProps {
  value: number | null;
  onChange: (value: number | null) => void;
}

const containerStyle: React.CSSProperties = {
  marginBottom: "var(--space-6)",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "var(--font-size-base)",
  fontWeight: 600,
  color: "var(--text-primary)",
  marginBottom: "var(--space-3)",
};

const hintStyle: React.CSSProperties = {
  marginLeft: "var(--space-3)",
  fontSize: "var(--font-size-xs)",
  color: "var(--text-secondary)",
};

export default function QuestionCount({ value, onChange }: QuestionCountProps) {
  const [inputValue, setInputValue] = useState(value !== null ? String(value) : "");

  useEffect(() => {
    setInputValue(value !== null ? String(value) : "");
  }, [value]);

  const isInvalid = value === null || value < 1 || value > 50;

  return (
    <div style={containerStyle}>
      <label htmlFor="question-count" style={labelStyle}>
        Number of Questions
      </label>
      <input
        id="question-count"
        type="number"
        min={1}
        max={50}
        step={1}
        inputMode="numeric"
        value={inputValue}
        onChange={(e) => {
          const raw = e.target.value;
          setInputValue(raw);

          if (raw === "") {
            onChange(null);
            return;
          }

          if (!/^\d+$/.test(raw)) {
            onChange(null);
            return;
          }

          const parsed = Number(raw);
          if (!Number.isInteger(parsed)) {
            onChange(null);
            return;
          }

          onChange(parsed);
        }}
        onBlur={() => {
          if (inputValue === "") return;
          if (!/^\d+$/.test(inputValue)) {
            setInputValue("");
            onChange(null);
            return;
          }

          const parsed = Number(inputValue);
          if (!Number.isInteger(parsed)) {
            setInputValue("");
            onChange(null);
            return;
          }

          const clamped = Math.min(50, Math.max(1, parsed));
          setInputValue(String(clamped));
          onChange(clamped);
        }}
        className="input"
        style={{ width: "120px" }}
        aria-describedby="count-hint"
        aria-invalid={isInvalid}
      />
      <span
        id="count-hint"
        style={hintStyle}
      >
        1 - 50
      </span>
    </div>
  );
}
