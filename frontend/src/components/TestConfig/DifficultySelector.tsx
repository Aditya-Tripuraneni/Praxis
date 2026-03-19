interface DifficultySelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const containerStyle: React.CSSProperties = {
  marginBottom: 'var(--space-6)',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 'var(--font-size-base)',
  fontWeight: 600,
  color: 'var(--text-primary)',
  marginBottom: 'var(--space-3)',
};

const optionsStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--space-3)',
};

const radioLabelBase: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--space-2)',
  padding: '10px 20px',
  border: '1.5px solid var(--color-stone-200)',
  borderRadius: 'var(--radius-md)',
  cursor: 'pointer',
  fontSize: 'var(--font-size-sm)',
  fontWeight: 500,
  color: 'var(--text-secondary)',
  backgroundColor: '#ffffff',
  transition: 'all var(--transition-fast)',
  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
};

const radioLabelSelected: React.CSSProperties = {
  ...radioLabelBase,
  backgroundColor: '#134e4a',
  color: '#ffffff',
  fontWeight: 600,
  border: '1.5px solid #134e4a',
  boxShadow: '0 2px 4px rgba(19, 78, 74, 0.2)',
};

const DIFFICULTIES = ['easy', 'medium', 'hard'] as const;

export default function DifficultySelector({ value, onChange }: DifficultySelectorProps) {
  return (
    <fieldset style={containerStyle}>
      <legend style={labelStyle}>Difficulty</legend>
      <div style={optionsStyle} role="radiogroup" aria-label="Select difficulty">
        {DIFFICULTIES.map((diff) => (
          <label
            key={diff}
            style={value === diff ? radioLabelSelected : radioLabelBase}
          >
            <input
              type="radio"
              name="difficulty"
              value={diff}
              checked={value === diff}
              onChange={() => onChange(diff)}
              style={{ accentColor: 'var(--color-primary-700)' }}
            />
            {diff.charAt(0).toUpperCase() + diff.slice(1)}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
