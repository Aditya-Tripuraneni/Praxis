import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopicSelector, DifficultySelector, QuestionCount } from '../components/TestConfig';
import { fetchTopics, generateTest } from '../services/api';
import type { TopicInfo } from '../types';

const pageTitle: React.CSSProperties = {
  fontSize: '1.75rem',
  fontWeight: 700,
  color: 'var(--color-primary-900)',
  marginBottom: 'var(--space-7)',
};

const errorStyle: React.CSSProperties = {
  color: 'var(--color-error-text)',
  fontSize: 'var(--font-size-sm)',
  marginTop: 'var(--space-3)',
  padding: 'var(--space-3) var(--space-4)',
  backgroundColor: 'var(--color-error-bg)',
  borderRadius: 'var(--radius-md)',
  border: '1px solid var(--color-error-border)',
};

const spinnerStyle: React.CSSProperties = {
  display: 'inline-block',
  width: '18px',
  height: '18px',
  border: '2px solid var(--text-on-primary)',
  borderTopColor: 'transparent',
  borderRadius: '50%',
  animation: 'spin 0.6s linear infinite',
  marginRight: 'var(--space-2)',
  verticalAlign: 'middle',
};

const loadingContainerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  padding: 'var(--space-11) 0',
  color: 'var(--text-secondary)',
  fontSize: 'var(--font-size-base)',
};

const loadingSpinnerStyle: React.CSSProperties = {
  display: 'inline-block',
  width: '24px',
  height: '24px',
  border: '3px solid var(--color-stone-200)',
  borderTopColor: 'var(--color-primary-500)',
  borderRadius: '50%',
  animation: 'spin 0.8s linear infinite',
  marginRight: 'var(--space-3)',
};

export default function Generate() {
  const navigate = useNavigate();

  const [topics, setTopics] = useState<TopicInfo[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [difficulty, setDifficulty] = useState('medium');
  const [count, setCount] = useState(20);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchTopics()
      .then((data) => {
        if (!cancelled) {
          setTopics(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Failed to load topics. Is the backend running?');
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleGenerate() {
    if (selectedTopics.length === 0) {
      setError('Please select at least one topic or subtopic.');
      return;
    }
    if (count < 5 || count > 50) {
      setError('Question count must be between 5 and 50.');
      return;
    }

    setError(null);
    setGenerating(true);

    try {
      const result = await generateTest({
        topics: selectedTopics,
        difficulty,
        count,
      });
      navigate(`/preview/${result.test_id}`);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to generate test. Please try again.';
      setError(message);
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div style={loadingContainerStyle} role="status" aria-live="polite">
        <span style={loadingSpinnerStyle} aria-hidden="true" />
        <p>Loading topics...</p>
      </div>
    );
  }

  const canGenerate = selectedTopics.length > 0 && count >= 5 && count <= 50 && !generating;

  return (
    <section>
      <h1 style={pageTitle}>Configure Your Test</h1>
      <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-5)' }}>
        Select topics, difficulty, and question count
      </p>

      <TopicSelector
        topics={topics}
        selected={selectedTopics}
        onChange={setSelectedTopics}
      />

      <DifficultySelector value={difficulty} onChange={setDifficulty} />

      <QuestionCount value={count} onChange={setCount} />

      <button
        type="button"
        className="btn-primary"
        disabled={!canGenerate}
        onClick={handleGenerate}
      >
        {generating && <span style={spinnerStyle} aria-hidden="true" />}
        {generating ? 'Generating...' : 'Generate Test'}
      </button>

      {error && (
        <div style={errorStyle} role="alert">
          {error}
        </div>
      )}
    </section>
  );
}
