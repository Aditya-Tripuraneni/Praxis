import { KpiItem } from "./types";

interface AboutPraxisHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  primaryCtaLabel: string;
  secondaryCtaLabel: string;
  onPrimaryCta: () => void;
  onSecondaryCta: () => void;
  kpis: KpiItem[];
}

export default function AboutPraxisHero({
  eyebrow,
  title,
  description,
  primaryCtaLabel,
  secondaryCtaLabel,
  onPrimaryCta,
  onSecondaryCta,
  kpis,
}: AboutPraxisHeroProps) {
  return (
    <section className="about-praxis-hero" aria-labelledby="about-praxis-title">
      <p className="about-praxis-eyebrow">{eyebrow}</p>
      <h1 id="about-praxis-title" className="about-praxis-title">{title}</h1>
      <p className="about-praxis-lede">{description}</p>

      <div className="about-praxis-cta-row">
        <button type="button" className="btn-primary about-praxis-btn-primary" onClick={onPrimaryCta}>
          {primaryCtaLabel}
        </button>
        <button type="button" className="btn-secondary" onClick={onSecondaryCta}>
          {secondaryCtaLabel}
        </button>
      </div>

      <div className="about-praxis-kpi-row" aria-label="Key platform metrics">
        {kpis.map((kpi) => (
          <article key={kpi.title} className="about-praxis-kpi">
            <strong>{kpi.title}</strong>
            <span>{kpi.description}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
