import { ComparisonContent } from "./types";

interface AboutPraxisComparisonProps {
  content: ComparisonContent;
}

export default function AboutPraxisComparison({ content }: AboutPraxisComparisonProps) {
  return (
    <section className="about-praxis-section about-praxis-contrast" aria-label="Before and after Praxis">
      <div className="about-praxis-contrast-head">
        <h2>{content.heading}</h2>
      </div>

      <div className="about-praxis-contrast-grid">
        <article className="about-praxis-state before">
          <h3>
            <span className="about-praxis-state-dot" aria-hidden="true" />
            {content.beforeTitle}
          </h3>
          <div className="about-praxis-state-rail">
            {content.beforeItems.map((item) => (
              <div key={item} className="about-praxis-state-item">{item}</div>
            ))}
          </div>
        </article>

        <div className="about-praxis-state-arrow" aria-hidden="true">→</div>

        <article className="about-praxis-state after">
          <h3>
            <span className="about-praxis-state-dot" aria-hidden="true" />
            {content.afterTitle}
          </h3>
          <div className="about-praxis-state-rail">
            {content.afterItems.map((item) => (
              <div key={item} className="about-praxis-state-item">{item}</div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}
