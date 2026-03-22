import { useNavigate } from 'react-router-dom';
import { BookOpen, Target, FileDown, ChevronRight, Check } from 'lucide-react';
import PraxisLogo from '../components/Brand/PraxisLogo';
import { APP_NAME } from '../components/Brand/brand';

/* ── Hero ─────────────────────────────────────────────────────────── */

const heroStyle: React.CSSProperties = {
  textAlign: 'center',
  padding: 'var(--space-11) var(--space-4) var(--space-9)',
  background: 'linear-gradient(135deg, #134e4a 0%, #0f766e 50%, #0d9488 100%)',
  marginTop: 'calc(-1 * var(--space-8))',
};

const titleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-5xl)',
  fontWeight: 800,
  color: '#ffffff',
  marginBottom: 'var(--space-4)',
  lineHeight: 1.15,
};

const taglineStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-lg)',
  color: '#99f6e4',
  marginBottom: 'var(--space-3)',
  lineHeight: 1.6,
  maxWidth: '520px',
  marginLeft: 'auto',
  marginRight: 'auto',
};

const subtitleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-sm)',
  color: '#ccfbf1',
  marginBottom: 'var(--space-8)',
  lineHeight: 1.6,
};

/* ── Feature cards ────────────────────────────────────────────────── */

const featuresStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  gap: 'var(--space-7)',
  marginTop: 'var(--space-10)',
  flexWrap: 'wrap',
  padding: '0 var(--space-4)',
};

const featureCardStyle: React.CSSProperties = {
  maxWidth: '260px',
  textAlign: 'center',
  padding: 'var(--space-7)',
  background: '#ffffff',
  boxShadow: 'var(--shadow-card)',
  borderRadius: 'var(--radius-lg)',
};

const featureTitleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-lg)',
  fontWeight: 700,
  color: 'var(--color-primary-900)',
  marginBottom: 'var(--space-2)',
};

const featureDescStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-sm)',
  color: 'var(--text-secondary)',
  lineHeight: 1.7,
};

const iconCircleBase: React.CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: 12,
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: 'var(--space-4)',
};

/* ── How it works ─────────────────────────────────────────────────── */

const howSectionStyle: React.CSSProperties = {
  marginTop: 'var(--space-10)',
  padding: 'var(--space-7)',
  maxWidth: 600,
  marginLeft: 'auto',
  marginRight: 'auto',
  background: '#ffffff',
  boxShadow: 'var(--shadow-card)',
  border: '1px solid var(--color-primary-200)',
  borderRadius: 'var(--radius-lg)',
  textAlign: 'center',
};

const howLabelStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xs)',
  fontWeight: 700,
  color: 'var(--color-primary-600)',
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  marginBottom: 'var(--space-5)',
};

const stepsRowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: 'var(--space-4)',
};

const stepCircleStyle: React.CSSProperties = {
  width: 36,
  height: 36,
  borderRadius: '50%',
  background: 'var(--color-primary-500)',
  color: '#ffffff',
  fontWeight: 700,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: 'var(--font-size-sm)',
  margin: '0 auto',
};

const stepLabelStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-sm)',
  color: 'var(--text-secondary)',
  fontWeight: 500,
  marginTop: 'var(--space-2)',
};

/* ── Pricing ──────────────────────────────────────────────────────── */

const pricingLabelStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xs)',
  fontWeight: 700,
  color: 'var(--color-primary-600)',
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  marginBottom: 'var(--space-4)',
};

const priceStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-4xl)',
  fontWeight: 800,
  color: 'var(--color-primary-900)',
  lineHeight: 1.2,
};

const priceSubStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-sm)',
  color: 'var(--text-secondary)',
  marginBottom: 'var(--space-5)',
};

const pricingFeaturesStyle: React.CSSProperties = {
  textAlign: 'left',
  maxWidth: 340,
  margin: '0 auto var(--space-6)',
};

const pricingFeatureStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--space-2)',
  marginBottom: 'var(--space-2)',
  fontSize: 'var(--font-size-sm)',
  color: 'var(--text-primary)',
};

/* ── Page wrapper ─────────────────────────────────────────────────── */

const pageStyle: React.CSSProperties = {
  paddingBottom: 'var(--space-11)',
};

/* ── Component ────────────────────────────────────────────────────── */

export default function Landing() {
  const navigate = useNavigate();

  return (
    <section className="page-enter" style={pageStyle}>
      {/* Hero */}
      <div className="full-bleed" style={heroStyle}>
        <h1 style={{ ...titleStyle, display: 'flex', justifyContent: 'center' }}>
          <PraxisLogo variant="full" colorScheme="dark" height={56} />
          <span className="sr-only">{APP_NAME}</span>
        </h1>
        <p style={taglineStyle}>
          Generate unlimited math practice tests instantly
        </p>
        <p style={subtitleStyle}>
          6 topics, 3 difficulty levels, instant PDF download
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-4)', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn-primary"
            onClick={() => navigate('/generate')}
          >
            Get Started
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate('/sample-preview')}
          >
            Try a Sample
          </button>
        </div>
      </div>

      {/* Feature cards */}
      <div style={featuresStyle}>
        <div className="stagger-1 animate-fade-in card-hover" style={featureCardStyle}>
          <div
            style={{
              ...iconCircleBase,
              background: 'var(--color-primary-100)',
              color: 'var(--color-primary-700)',
            }}
          >
            <BookOpen size={20} />
          </div>
          <h2 style={featureTitleStyle}>Topics</h2>
          <p style={featureDescStyle}>
            Choose from algebra, functions, geometry, trigonometry, calculus, and combinatorics
          </p>
        </div>

        <div className="stagger-2 animate-fade-in card-hover" style={featureCardStyle}>
          <div
            style={{
              ...iconCircleBase,
              background: 'var(--color-accent-50)',
              color: 'var(--color-accent-600)',
            }}
          >
            <Target size={20} />
          </div>
          <h2 style={featureTitleStyle}>Difficulty Levels</h2>
          <p style={featureDescStyle}>
            Select easy, medium, or hard to match your skill level
          </p>
        </div>

        <div className="stagger-3 animate-fade-in card-hover" style={featureCardStyle}>
          <div
            style={{
              ...iconCircleBase,
              background: '#dbeafe',
              color: '#2563eb',
            }}
          >
            <FileDown size={20} />
          </div>
          <h2 style={featureTitleStyle}>Instant PDF</h2>
          <p style={featureDescStyle}>
            Download a ready-to-print PDF with an optional answer key
          </p>
        </div>
      </div>

      {/* How it works */}
      <div style={howSectionStyle}>
        <div style={howLabelStyle}>HOW IT WORKS</div>
        <div style={stepsRowStyle}>
          <div className="stagger-1 animate-fade-in">
            <div style={stepCircleStyle}>1</div>
            <div style={stepLabelStyle}>Pick topics</div>
          </div>
          <ChevronRight size={20} color="var(--color-stone-300)" />
          <div className="stagger-2 animate-fade-in">
            <div style={stepCircleStyle}>2</div>
            <div style={stepLabelStyle}>Preview test</div>
          </div>
          <ChevronRight size={20} color="var(--color-stone-300)" />
          <div className="stagger-3 animate-fade-in">
            <div style={stepCircleStyle}>3</div>
            <div style={stepLabelStyle}>Download PDF</div>
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div style={{ marginTop: 'var(--space-10)', maxWidth: 700, marginLeft: 'auto', marginRight: 'auto', padding: '0 var(--space-4)' }}>
        <div style={pricingLabelStyle}>CHOOSE YOUR PLAN</div>
        <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', justifyContent: 'center' }}>
          {/* Student */}
          <div className="animate-fade-in card-hover" style={{
            flex: '1 1 280px', maxWidth: 320, background: '#ffffff', borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-card)', padding: 'var(--space-6)',
            border: '2px solid var(--color-accent-500)',
            position: 'relative',
          }}>
            <span style={{
              position: 'absolute', top: -10, right: 'var(--space-4)',
              background: 'var(--color-accent-500)', color: '#fff',
              fontSize: 'var(--font-size-xs)', fontWeight: 600,
              padding: '2px var(--space-3)', borderRadius: 'var(--radius-full)',
            }}>BEST VALUE</span>
            <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, color: 'var(--color-primary-900)', marginBottom: 'var(--space-1)' }}>Student</p>
            <div style={priceStyle}>$4.99<span style={{ fontSize: 'var(--font-size-lg)', fontWeight: 500 }}>/mo</span></div>
            <p style={priceSubStyle}>CAD. Cancel anytime.</p>
            <div style={pricingFeaturesStyle}>
              {[
                'Unlimited test generation',
                '10+ math topics, 130+ problem types',
                'Step-by-step solutions',
                'PDF downloads with answer keys',
                'Practice streak tracking',
              ].map((f) => (
                <div key={f} style={pricingFeatureStyle}>
                  <Check size={16} color="var(--color-primary-500)" style={{ flexShrink: 0 }} />
                  {f}
                </div>
              ))}
            </div>
            <button type="button" className="btn-secondary" style={{ width: '100%' }} onClick={() => navigate('/register')}>
              Get Started
            </button>
          </div>
          {/* Tutor */}
          <div className="animate-fade-in card-hover" style={{
            flex: '1 1 280px', maxWidth: 320, background: '#ffffff', borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-card)', padding: 'var(--space-6)',
            border: '2px solid transparent',
          }}>
            <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, color: 'var(--color-primary-900)', marginBottom: 'var(--space-1)' }}>Tutor</p>
            <div style={priceStyle}>$12.99<span style={{ fontSize: 'var(--font-size-lg)', fontWeight: 500 }}>/mo</span></div>
            <p style={priceSubStyle}>CAD. Cancel anytime.</p>
            <div style={pricingFeaturesStyle}>
              <div style={pricingFeatureStyle}>
                <Check size={16} color="var(--color-primary-500)" style={{ flexShrink: 0 }} />
                Everything in Student, plus:
              </div>
              {[
                'Save up to 100 tests',
                'Name and organize tests',
                'Instant replay of saved tests',
                'Search saved tests by name',
              ].map((f) => (
                <div key={f} style={{ ...pricingFeatureStyle, color: 'var(--color-primary-700)', fontWeight: 500 }}>
                  <Check size={16} color="var(--color-accent-500)" style={{ flexShrink: 0 }} />
                  {f}
                </div>
              ))}
            </div>
            <button type="button" className="btn-primary" style={{ width: '100%' }} onClick={() => navigate('/register')}>
              Get Started
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
