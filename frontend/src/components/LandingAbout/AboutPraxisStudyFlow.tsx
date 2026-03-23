import { StudyStep } from "./types";

interface AboutPraxisStudyFlowProps {
  title: string;
  steps: StudyStep[];
}

export default function AboutPraxisStudyFlow({ title, steps }: AboutPraxisStudyFlowProps) {
  return (
    <section className="about-praxis-section about-praxis-flow" aria-labelledby="about-praxis-flow-title">
      <h2 id="about-praxis-flow-title">{title}</h2>
      <ol className="about-praxis-flow-list">
        {steps.map((step) => (
          <li key={step.title}>
            <strong>{step.title}</strong>
            <span>{step.description}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
