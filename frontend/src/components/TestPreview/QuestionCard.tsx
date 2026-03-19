import { useState } from 'react';
import { MathRenderer } from '../MathRenderer';
import type { QuestionResponse } from '../../types';

interface QuestionCardProps {
  question: QuestionResponse;
  number: number;
}

const cardStyle: React.CSSProperties = {
  padding: 'var(--space-6)',
  border: 'none',
  borderLeft: '3px solid var(--color-primary-500)',
  borderRadius: 'var(--radius-lg)',
  backgroundColor: 'var(--bg-card)',
  boxShadow: 'var(--shadow-card)',
  transition: 'box-shadow var(--transition-normal)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'baseline',
  gap: 'var(--space-3)',
  marginBottom: 'var(--space-4)',
};

const numberStyle: React.CSSProperties = {
  backgroundColor: 'var(--color-primary-100)',
  color: 'var(--color-primary-900)',
  borderRadius: '8px',
  width: '32px',
  height: '32px',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: 'var(--font-size-sm)',
  fontWeight: 700,
};

const metaStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--space-2)',
  marginLeft: 'auto',
};

const tagStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xs)',
  padding: 'var(--space-1) var(--space-2)',
  borderRadius: 'var(--radius-full)',
  backgroundColor: 'var(--color-primary-100)',
  color: 'var(--color-primary-700)',
  fontWeight: 500,
};

const questionBodyStyle: React.CSSProperties = {
  fontSize: '1.05rem',
  lineHeight: 1.7,
  color: 'var(--text-primary)',
  marginBottom: 'var(--space-4)',
  padding: 'var(--space-2) 0',
};

const toggleButtonStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: 'var(--color-primary-700)',
  fontSize: 'var(--font-size-sm)',
  fontWeight: 600,
  cursor: 'pointer',
  padding: 'var(--space-1) 0',
  fontFamily: 'var(--font-family)',
};

const answerStyle: React.CSSProperties = {
  marginTop: 'var(--space-3)',
  padding: 'var(--space-4) var(--space-5)',
  backgroundColor: 'var(--color-primary-50)',
  borderRadius: 'var(--radius-md)',
  borderLeft: '3px solid var(--color-primary-500)',
};

const answerLabelStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xs)',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  marginBottom: 'var(--space-2)',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
};

const solutionSectionStyle: React.CSSProperties = {
  borderLeft: '3px solid var(--color-primary-300)',
  paddingLeft: 'var(--space-4)',
  marginTop: 'var(--space-3)',
};

const solutionHeaderStyle: React.CSSProperties = {
  fontWeight: 600,
  fontSize: 'var(--font-size-sm)',
  color: 'var(--color-primary-700)',
  marginBottom: 'var(--space-2)',
};

const stepsListStyle: React.CSSProperties = {
  margin: 0,
  paddingLeft: 'var(--space-5)',
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--space-2)',
};

const stepItemStyle: React.CSSProperties = {
  color: 'var(--text-primary)',
};

const buttonRowStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--space-3)',
};

export default function QuestionCard({ question, number }: QuestionCardProps) {
  const [showAnswer, setShowAnswer] = useState(false);
  const [showSolution, setShowSolution] = useState(false);

  const hasSolution = question.solution_steps.length > 0;

  return (
    <article style={cardStyle} aria-label={`Question ${number}`}>
      <div style={headerStyle}>
        <span style={numberStyle}>Q{number}</span>
        <div style={metaStyle}>
          <span style={tagStyle}>{question.topic}</span>
          <span style={tagStyle}>{question.difficulty}</span>
          {question.subtopic && <span style={tagStyle}>{question.subtopic.replace(/_/g, " ")}</span>}
        </div>
      </div>

      <div style={questionBodyStyle}>
        <MathRenderer latex={question.question_latex} displayMode />
      </div>

      <div style={buttonRowStyle}>
        {hasSolution && !showSolution && (
          <button
            type="button"
            style={toggleButtonStyle}
            onClick={() => setShowSolution(true)}
            aria-expanded={showSolution}
          >
            Show Solution
          </button>
        )}
        {hasSolution && showSolution && (
          <button
            type="button"
            style={toggleButtonStyle}
            onClick={() => setShowSolution(false)}
            aria-expanded={showSolution}
          >
            Hide Solution
          </button>
        )}
        {!showSolution && (
          <button
            type="button"
            style={toggleButtonStyle}
            onClick={() => setShowAnswer(!showAnswer)}
            aria-expanded={showAnswer}
          >
            {showAnswer ? 'Hide Answer' : 'Show Answer'}
          </button>
        )}
      </div>

      {showSolution && hasSolution && (
        <div className="reveal-enter" style={solutionSectionStyle} role="region" aria-label="Worked solution">
          <div style={solutionHeaderStyle}>Solution</div>
          <ol style={stepsListStyle}>
            {question.solution_steps.map((step, idx) => (
              <li key={idx} style={stepItemStyle}>
                <MathRenderer latex={step} />
              </li>
            ))}
          </ol>
        </div>
      )}

      {showAnswer && !showSolution && (
        <div className="reveal-enter" style={answerStyle}>
          <div style={answerLabelStyle}>Answer</div>
          <MathRenderer latex={question.answer_latex} displayMode />
        </div>
      )}
    </article>
  );
}
