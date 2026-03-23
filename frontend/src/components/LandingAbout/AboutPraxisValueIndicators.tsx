import { ValueIndicator } from "./types";

interface AboutPraxisValueIndicatorsProps {
  items: ValueIndicator[];
}

export default function AboutPraxisValueIndicators({ items }: AboutPraxisValueIndicatorsProps) {
  return (
    <section className="about-praxis-section about-praxis-proof" aria-label="Value indicators">
      {items.map((item) => (
        <article key={item.title} className="about-praxis-proof-node">
          <strong>{item.title}</strong>
          <span>{item.description}</span>
        </article>
      ))}
    </section>
  );
}
