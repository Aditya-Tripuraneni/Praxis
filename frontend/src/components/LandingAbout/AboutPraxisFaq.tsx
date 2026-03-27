import type { FaqItem } from "./types";

interface AboutPraxisFaqProps {
  items: FaqItem[];
}

export default function AboutPraxisFaq({ items }: AboutPraxisFaqProps) {
  return (
    <section className="about-praxis-section about-praxis-faq" aria-labelledby="about-praxis-faq-title">
      <h2 id="about-praxis-faq-title">FAQ</h2>
      {items.map((item) => (
        <details key={item.question}>
          <summary>{item.question}</summary>
          <p className="about-praxis-answer">{item.answer}</p>
        </details>
      ))}
    </section>
  );
}
