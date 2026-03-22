import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QuestionList, Timer } from '../components/TestPreview';
import { replaySavedTest, getUserStats, saveTimerDuration } from '../services/api';
import type { SavedTest } from '../types';
import { formatDifficultyId, formatTopicSelection } from '../utils/displayFormat';

// Reuse same styles as Preview
const sectionStyle: React.CSSProperties = {
  marginTop: 'calc(-1 * var(--space-8))',
};

const summaryBarStyle: React.CSSProperties = {
  background: '#134e4a',
  padding: 'var(--space-5) var(--space-7)',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  flexWrap: 'wrap',
  gap: 'var(--space-4)',
};

const summaryLeftStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--space-3)',
};

const summaryRightStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--space-5)',
};

const summaryTitleStyle: React.CSSProperties = {
  fontSize: '1.5rem',
  fontWeight: 700,
  color: '#ffffff',
  margin: 0,
};

const pillRowStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--space-3)',
  flexWrap: 'wrap',
};

const pillStyle: React.CSSProperties = {
  backgroundColor: 'rgba(255,255,255,0.12)',
  color: '#99f6e4',
  borderRadius: 'var(--radius-full)',
  padding: 'var(--space-1) var(--space-3)',
  fontSize: 'var(--font-size-xs)',
  fontWeight: 500,
};

const controlsBarStyle: React.CSSProperties = {
  backgroundColor: '#ffffff',
  padding: 'var(--space-3) var(--space-7)',
  borderBottom: '1px solid var(--color-stone-200)',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  flexWrap: 'wrap',
  gap: 'var(--space-3)',
};

const checkboxLabel: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--space-2)',
  fontSize: 'var(--font-size-sm)',
  color: 'var(--text-secondary)',
  cursor: 'pointer',
};

const questionsAreaStyle: React.CSSProperties = {
  padding: 'var(--space-5) var(--space-4)',
};

const loadingStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  padding: 'var(--space-11) 0',
  color: 'var(--text-secondary)',
  fontSize: 'var(--font-size-base)',
};

const errorStyle: React.CSSProperties = {
  color: 'var(--color-error-text)',
  fontSize: 'var(--font-size-sm)',
  padding: 'var(--space-4) var(--space-5)',
  backgroundColor: 'var(--color-error-bg)',
  borderRadius: 'var(--radius-md)',
  border: '1px solid var(--color-error-border)',
  textAlign: 'center',
};

export default function SavedTestReplay() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [test, setTest] = useState<SavedTest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [includeAnswers, setIncludeAnswers] = useState(true);
  const [includeSolutions, setIncludeSolutions] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [previousDuration, setPreviousDuration] = useState<number | null>(null);

  useEffect(() => {
    getUserStats()
      .then((stats) => setPreviousDuration(stats.last_test_duration))
      .catch(() => {});
  }, []);

  const handleTimerComplete = useCallback((durationSeconds: number) => {
    setPreviousDuration(durationSeconds);
    saveTimerDuration(durationSeconds).catch(() => {});
  }, []);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    replaySavedTest(id)
      .then((data) => { if (!cancelled) { setTest(data); setLoading(false); } })
      .catch(() => { if (!cancelled) { setError('Failed to load saved test.'); setLoading(false); } });

    return () => { cancelled = true; };
  }, [id]);

  async function handleDownload() {
    if (!test) return;
    setDownloading(true);
    try {
      // For saved test replay, we need to generate fresh for PDF since test_id is not in cache
      // For now, navigate to generate with the same config
      setError('PDF download for saved tests is not yet supported. Generate a new test with the same config for PDF.');
    } finally {
      setDownloading(false);
    }
  }

  if (loading) {
    return (
      <div style={loadingStyle} role="status" aria-live="polite">
        <p>Loading saved test...</p>
      </div>
    );
  }

  if (error && !test) {
    return (
      <div>
        <div style={errorStyle} role="alert">{error}</div>
        <div style={{ textAlign: 'center', marginTop: 'var(--space-6)' }}>
          <button type="button" className="btn-secondary" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!test) return null;

  const topicsList = test.config.topics.map(formatTopicSelection).join(', ');
  const difficultyLabel = formatDifficultyId(test.config.difficulty);

  return (
    <section className="page-enter" style={sectionStyle}>
      <div className="full-bleed-padded" style={summaryBarStyle}>
        <div style={summaryLeftStyle}>
          <h1 style={summaryTitleStyle}>Saved Test: {test.test_name}</h1>
          <div style={pillRowStyle}>
            <span style={pillStyle}>Topics: {topicsList}</span>
            <span style={pillStyle}>Difficulty: {difficultyLabel}</span>
            <span style={pillStyle}>{test.questions.length} questions</span>
          </div>
        </div>
        <div style={summaryRightStyle}>
          <Timer
            previousDuration={previousDuration}
            onTimerComplete={handleTimerComplete}
          />
          <button
            type="button"
            className="btn-primary"
            onClick={handleDownload}
            disabled={downloading}
          >
            {downloading ? 'Downloading...' : 'Download PDF'}
          </button>
        </div>
      </div>

      <div className="full-bleed-padded" style={controlsBarStyle}>
        <label style={checkboxLabel}>
          <input
            type="checkbox"
            checked={includeAnswers}
            onChange={(e) => setIncludeAnswers(e.target.checked)}
            style={{ accentColor: 'var(--color-primary-700)' }}
          />
          Include answers
        </label>
        {test.questions.some(q => q.solution_steps.length > 0) && (
          <label style={checkboxLabel}>
            <input
              type="checkbox"
              checked={includeSolutions}
              onChange={(e) => setIncludeSolutions(e.target.checked)}
              style={{ accentColor: 'var(--color-primary-700)' }}
            />
            Include solutions
          </label>
        )}

        <button
          type="button"
          className="btn-secondary"
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </button>
      </div>

      {error && (
        <div style={{ ...errorStyle, marginBottom: 'var(--space-5)' }} role="alert">
          {error}
        </div>
      )}

      <div style={questionsAreaStyle}>
        <QuestionList questions={test.questions} />
      </div>
    </section>
  );
}
