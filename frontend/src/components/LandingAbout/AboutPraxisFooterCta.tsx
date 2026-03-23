interface AboutPraxisFooterCtaProps {
  title: string;
  description: string;
  ctaLabel: string;
  onCtaClick: () => void;
}

export default function AboutPraxisFooterCta({ title, description, ctaLabel, onCtaClick }: AboutPraxisFooterCtaProps) {
  return (
    <section className="about-praxis-section about-praxis-footer-cta">
      <div>
        <strong>{title}</strong>
        <p>{description}</p>
      </div>
      <button type="button" className="btn-primary about-praxis-btn-primary" onClick={onCtaClick}>
        {ctaLabel}
      </button>
    </section>
  );
}
