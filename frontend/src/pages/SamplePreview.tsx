import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { QuestionList } from '../components/TestPreview';
import { fetchSampleTest } from '../services/api';
import type { TestResponse } from '../types';
import { formatDifficultyId, formatTopicId } from '../utils/displayFormat';

const pageStyle: React.CSSProperties = {
  paddingBottom: 'var(--space-11)',
  marginTop: 'calc(-1 * var(--space-8))',
};

const headerStyle: React.CSSProperties = {
  background: '#134e4a',
  padding: 'var(--space-6) var(--space-7)',
  textAlign: 'center',
};

const headerTitleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-2xl)',
  fontWeight: 700,
  color: '#ffffff',
  margin: 0,
};

const headerSubStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-sm)',
  color: '#99f6e4',
  marginTop: 'var(--space-2)',
};

const contentStyle: React.CSSProperties = {
  maxWidth: '800px',
  margin: '0 auto',
  padding: 'var(--space-6) var(--space-4)',
};

const ctaBannerStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, #134e4a 0%, #0f766e 100%)',
  borderRadius: 'var(--radius-lg)',
  padding: 'var(--space-7)',
  textAlign: 'center',
  marginTop: 'var(--space-8)',
};

const ctaTitleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xl)',
  fontWeight: 700,
  color: '#ffffff',
  margin: 0,
};

const ctaDescStyle: React.CSSProperties = {
  color: '#99f6e4',
  fontSize: 'var(--font-size-sm)',
  marginTop: 'var(--space-2)',
  marginBottom: 'var(--space-5)',
};

const loadingStyle: React.CSSProperties = {
  textAlign: 'center',
  padding: 'var(--space-10)',
  color: 'var(--text-secondary)',
};

const errorStyle: React.CSSProperties = {
  textAlign: 'center',
  padding: 'var(--space-10)',
  color: 'var(--color-error)',
};

const badgeRowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  gap: 'var(--space-3)',
  flexWrap: 'wrap',
  marginBottom: 'var(--space-6)',
};

const badgeStyle: React.CSSProperties = {
  backgroundColor: 'var(--color-primary-100)',
  color: 'var(--color-primary-700)',
  borderRadius: 'var(--radius-full)',
  padding: 'var(--space-1) var(--space-3)',
  fontSize: 'var(--font-size-xs)',
  fontWeight: 600,
};

export default function SamplePreview() {
  const navigate = useNavigate();
  const [test, setTest] = useState<TestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');

    fetchSampleTest('algebra,functions', 'easy', 5)
      .then((data) => {
        if (!cancelled) setTest(data);
      })
      .catch(() => {
        if (!cancelled) setError('Failed to load sample test. Please try again.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <section style={pageStyle}>
        <div style={headerStyle}>
          <h1 style={headerTitleStyle}>Sample Test</h1>
          <p style={headerSubStyle}>See what Praxis can do</p>
        </div>
        <div style={loadingStyle} role="status" aria-label="Loading sample test">
          Generating sample questions...
        </div>
      </section>
    );
  }

  if (error || !test) {
    return (
      <section style={pageStyle}>
        <div style={headerStyle}>
          <h1 style={headerTitleStyle}>Sample Test</h1>
        </div>
        <div style={errorStyle} role="alert">
          <p>{error || 'Something went wrong.'}</p>
          <button
            type="button"
            className="btn-primary"
            style={{ marginTop: 'var(--space-4)' }}
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="page-enter" style={pageStyle}>
      <div className="full-bleed" style={headerStyle}>
        <h1 style={headerTitleStyle}>Sample Test</h1>
        <p style={headerSubStyle}>
          {test.questions.length} questions — no signup required
        </p>
      </div>

      <div style={contentStyle}>
        <div style={badgeRowStyle}>
          {[...new Set(test.questions.map(q => q.topic))].map(topic => (
            <span key={topic} style={badgeStyle}>{formatTopicId(topic)}</span>
          ))}
          <span style={badgeStyle}>{formatDifficultyId(test.config.difficulty)}</span>
        </div>

        <QuestionList questions={test.questions} />

        <div style={ctaBannerStyle}>
          <h2 style={ctaTitleStyle}>Like what you see?</h2>
          <p style={ctaDescStyle}>
            Sign up to generate unlimited tests with 130+ problem types,
            PDF downloads, and step-by-step solutions.
          </p>
          <button
            type="button"
            className="btn-primary"
            onClick={() => navigate('/register')}
          >
            Sign Up — $4.99/month
          </button>
        </div>
      </div>
    </section>
  );
}
