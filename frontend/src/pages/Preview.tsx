import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QuestionList, Timer } from '../components/TestPreview';
import { getTest, downloadPdf, getUserStats, saveTimerDuration } from '../services/api';
import { useSubscription } from '../context/SubscriptionContext';
import { saveTest } from '../services/api';
import type { TestResponse } from '../types';

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

export default function Preview() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();

  const [test, setTest] = useState<TestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [includeAnswers, setIncludeAnswers] = useState(true);
  const [includeSolutions, setIncludeSolutions] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [previousDuration, setPreviousDuration] = useState<number | null>(null);
  const { isTutor } = useSubscription();
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveName, setSaveName] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    getUserStats()
      .then((stats) => setPreviousDuration(stats.last_test_duration))
      .catch(() => {}); // Non-blocking — timer still works without previous time
  }, []);

  const handleTimerComplete = useCallback((durationSeconds: number) => {
    setPreviousDuration(durationSeconds); // Optimistic update
    saveTimerDuration(durationSeconds).catch(() => {
      console.error("Failed to save timer duration");
    });
  }, []);

  useEffect(() => {
    if (!testId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    getTest(testId)
      .then((data) => {
        if (!cancelled) {
          setTest(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Failed to load test. It may not exist or the backend is unreachable.');
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [testId]);

  async function handleDownload() {
    if (!testId) return;
    setDownloading(true);
    try {
      await downloadPdf(testId, includeAnswers, includeSolutions);
    } catch {
      setError('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  }

  async function handleSaveTest() {
    if (!test || !saveName.trim()) return;
    setSaving(true);
    try {
      await saveTest({
        test_name: saveName.trim(),
        config: {
          topics: test.config.topics,
          difficulty: test.config.difficulty,
          count: test.config.count,
        },
        seed: test.config.seed!,
        questions: test.questions.map((q) => ({
          id: q.id,
          question_latex: q.question_latex,
          answer_latex: q.answer_latex,
          topic: q.topic,
          difficulty: q.difficulty,
          subtopic: q.subtopic,
          solution_steps: q.solution_steps,
        })),
      });
      setShowSaveModal(false);
      setSaveName('');
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch {
      setError('Failed to save test. Please try again.');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div style={loadingStyle} role="status" aria-live="polite">
        <p>Loading test...</p>
      </div>
    );
  }

  if (error && !test) {
    return (
      <div>
        <div style={errorStyle} role="alert">{error}</div>
        <div style={{ textAlign: 'center', marginTop: 'var(--space-6)' }}>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate('/generate')}
          >
            Generate New Test
          </button>
        </div>
      </div>
    );
  }

  if (!test) return null;

  const topicsList = test.config.topics.join(', ');
  const difficultyLabel = test.config.difficulty.charAt(0).toUpperCase() + test.config.difficulty.slice(1);

  return (
    <section className="page-enter" style={sectionStyle}>
      <div className="full-bleed-padded" style={summaryBarStyle}>
        <div style={summaryLeftStyle}>
          <h1 style={summaryTitleStyle}>Test Preview</h1>
          <div style={pillRowStyle}>
            <span style={pillStyle}>Topics: {topicsList}</span>
            <span style={pillStyle}>Difficulty: {difficultyLabel}</span>
            <span style={pillStyle}>{test.questions.length} questions</span>
          </div>
        </div>
        <div style={summaryRightStyle}>
          {isTutor && (
            <button
              type="button"
              onClick={() => setShowSaveModal(true)}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 'var(--space-2)',
                padding: 'var(--space-2) var(--space-5)', minHeight: 40,
                fontFamily: 'var(--font-family)', fontSize: 'var(--font-size-sm)', fontWeight: 500,
                color: '#fff', background: 'rgba(255,255,255,0.15)',
                border: '1.5px solid rgba(255,255,255,0.3)', borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
              }}
              aria-label="Save test"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
              Save Test
            </button>
          )}
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
        {test && test.questions.some(q => q.solution_steps.length > 0) && (
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
          onClick={() => navigate('/generate')}
        >
          Generate New Test
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
      {/* Save Test Modal */}
      {showSaveModal && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.4)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', zIndex: 100,
          }}
          onClick={(e) => { if (e.target === e.currentTarget) setShowSaveModal(false); }}
        >
          <div style={{
            background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)',
            boxShadow: '0 4px 16px rgba(41,37,36,0.1)', padding: 'var(--space-7)',
            width: 420, maxWidth: '90vw',
          }}>
            <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 'var(--space-2)' }}>Save Test</h2>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-5)' }}>
              Give this test a name so you can find and replay it later.
            </p>
            <input
              type="text"
              className="input"
              placeholder="e.g., Weekly Algebra Quiz"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              maxLength={100}
              autoFocus
              onKeyDown={(e) => { if (e.key === 'Enter' && saveName.trim()) handleSaveTest(); }}
            />
            <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end', marginTop: 'var(--space-5)' }}>
              <button type="button" className="btn-secondary" onClick={() => setShowSaveModal(false)} disabled={saving}>
                Cancel
              </button>
              <button
                type="button"
                style={{
                  padding: 'var(--space-2) var(--space-5)',
                  fontFamily: 'var(--font-family)', fontSize: 'var(--font-size-sm)', fontWeight: 600,
                  color: '#fff', background: 'var(--color-primary-700)',
                  border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer',
                  minHeight: 36,
                }}
                onClick={handleSaveTest}
                disabled={saving || !saveName.trim()}
              >
                {saving ? 'Saving...' : 'Save Test'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success Toast */}
      {saveSuccess && (
        <div style={{
          position: 'fixed', bottom: 'var(--space-7)', left: '50%', transform: 'translateX(-50%)',
          background: '#ecfdf5', color: '#065f46', border: '1px solid #6ee7b7',
          padding: 'var(--space-3) var(--space-6)', borderRadius: 'var(--radius-md)',
          fontSize: 'var(--font-size-sm)', fontWeight: 500, boxShadow: '0 4px 16px rgba(41,37,36,0.1)',
          zIndex: 200,
        }}>
          &#10003; Test saved successfully
        </div>
      )}
    </section>
  );
}
