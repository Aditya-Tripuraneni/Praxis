import type { QuestionResponse } from '../../types';
import QuestionCard from './QuestionCard';

interface QuestionListProps {
  questions: QuestionResponse[];
}

export default function QuestionList({ questions }: QuestionListProps) {
  if (questions.length === 0) {
    return (
      <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic', padding: 'var(--space-6) 0' }}>
        No questions in this test.
      </p>
    );
  }

  return (
    <section aria-label="Questions list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      {questions.map((q, idx) => (
        <QuestionCard key={q.id} question={q} number={idx + 1} />
      ))}
    </section>
  );
}
