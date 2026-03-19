interface QuestionCountProps {
  value: number;
  onChange: (value: number) => void;
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
  return (
    <div style={containerStyle}>
      <label htmlFor="question-count" style={labelStyle}>
        Number of Questions
      </label>
      <input
        id="question-count"
        type="number"
        min={5}
        max={50}
        value={value}
        onChange={(e) => {
          const raw = e.target.value;
          if (raw === "") return;
          const num = parseInt(raw, 10);
          if (!isNaN(num)) {
            onChange(num);
          }
        }}
        className="input"
        style={{ width: "120px" }}
        aria-describedby="count-hint"
      />
      <span
        id="count-hint"
        style={hintStyle}
      >
        5 - 50
      </span>
    </div>
  );
}
