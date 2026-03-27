import { useNavigate } from "react-router-dom";
import {
  AboutPraxisComparison,
  AboutPraxisFaq,
  AboutPraxisFooterCta,
  AboutPraxisHero,
  AboutPraxisStudyFlow,
  AboutPraxisValueIndicators,
  ComparisonContent,
  FaqItem,
  KpiItem,
  StudyStep,
  ValueIndicator,
} from "../components/LandingAbout";
import "../components/LandingAbout/aboutPraxis.css";

const kpis: KpiItem[] = [
  {
    title: "6 topic families",
    description: "Core coverage across algebra, functions, trigonometry, calculus, geometry, and combinatorics.",
  },
  {
    title: "3 difficulty levels",
    description: "Easy, medium, and hard for progressive practice.",
  },
  {
    title: "Instant Preview",
    description: "Preview in-browser before exporting print-ready sets.",
  },
  {
    title: "Written Solutions",
    description: "Method-first feedback, not answer-only output.",
  },
];

const flowSteps: StudyStep[] = [
  {
    title: "Choose topic and difficulty",
    description: "Target weak areas quickly, whether for solo revision or tutor-led practice.",
  },
  {
    title: "Generate a new test each time",
    description: "Create unlimited fresh sets so students practice reasoning, not memorization.",
  },
  {
    title: "Review with written solutions",
    description: "Understand the full method path from setup to final answer.",
  },
  {
    title: "Export and reuse",
    description: "Download print-ready PDFs and build reusable banks for future sessions.",
  },
];

const comparisonContent: ComparisonContent = {
  heading: "The same learner journey, redesigned by Praxis",
  beforeTitle: "Before Praxis",
  afterTitle: "After Praxis",
  beforeItems: [
    "Stale worksheet patterns repeat and confidence drops.",
    "Tutors spend extra prep time rebuilding similar sets.",
    "Answer-only keys do not teach method.",
    "Practice quality feels inconsistent week to week.",
  ],
  afterItems: [
    "Unlimited fresh generation for every study block.",
    "Unlimited question banks for reusable tutoring workflows.",
    "Written solutions speed up correction and review.",
    "Reliable output builds trust across sessions.",
  ],
};

const valueIndicators: ValueIndicator[] = [
  {
    title: "Sample Test Available",
    description: "Visitors can experience the real workflow before signup.",
  },
  {
    title: "Unlimited Generation",
    description: "Create as many new practice sets as needed.",
  },
  {
    title: "Unlimited Question Banks",
    description: "Save, organize, and reuse tests across sessions.",
  },
  {
    title: "Continuous Expansion",
    description: "Topic coverage and problem formats keep growing.",
  },
];

const faqItems: FaqItem[] = [
  {
    question: "Who uses Praxis?",
    answer: "Students preparing for exams, tutors building targeted worksheets, and educators creating consistent practice sets.",
  },
  {
    question: "Do I get steps or only final answers?",
    answer: "Praxis provides written solutions so learners can follow method, not just check correctness.",
  },
  {
    question: "Can I run this repeatedly across weeks?",
    answer: "Yes. Unlimited generation and unlimited question banks are designed for long-term prep.",
  },
  {
    question: "Can I pick specific topics instead of full mixed tests?",
    answer: "Yes. You can target selected topic areas and tailor practice to exactly what needs improvement.",
  },
  {
    question: "How quickly can I create a new worksheet?",
    answer: "Most sets can be generated in seconds, previewed instantly, and exported right away.",
  },
  {
    question: "Is there a public sample before signup?",
    answer: "Yes. Visitors can try a real sample flow to evaluate quality before creating an account.",
  },
  {
    question: "Can tutors save and reuse tests?",
    answer: "Yes. Praxis supports reusable saved tests and organized question banks for recurring sessions.",
  },
  {
    question: "Do you support printed classroom workflows?",
    answer: "Yes. Praxis exports clean, print-ready PDFs with optional answer keys for classroom or tutoring use.",
  },
  {
    question: "Will students see the same questions repeatedly?",
    answer: "Praxis is designed to generate fresh variants so students practice reasoning, not memorization.",
  },
  {
    question: "Can I use Praxis for timed exam practice?",
    answer: "Yes. Praxis supports timed practice workflows so students can train under exam-like conditions.",
  },
  {
    question: "Does Praxis replace my existing teaching process?",
    answer: "No. It fits into your current process by speeding up worksheet creation and solution review.",
  },
  {
    question: "Are new topics still being added?",
    answer: "Yes. Topic coverage and problem formats continue to expand over time.",
  },
  {
    question: "Do I need a separate AI chat subscription to use Praxis?",
    answer: "No. Praxis is a purpose-built practice workflow without requiring a separate chat subscription.",
  },
];

export default function AboutPraxis() {
  const navigate = useNavigate();

  return (
    <section className="about-praxis-page page-enter" aria-label="About Praxis page">
      <div className="about-praxis-container">
        <AboutPraxisHero
          eyebrow="Math Practice for Students, Tutors, and Educators"
          title="Generate fresh, exam-style math practice in seconds."
          description="Praxis helps you select topics, set difficulty, generate unlimited new tests, review written solutions, and export clean PDFs with optional answer keys. Built for reliable daily prep without needing a separate AI chat subscription."
          primaryCtaLabel="Generate Your First Test"
          secondaryCtaLabel="Try Public Sample"
          onPrimaryCta={() => navigate("/generate")}
          onSecondaryCta={() => navigate("/sample-preview")}
          kpis={kpis}
        />

        <AboutPraxisStudyFlow title="How Praxis works in real study flow" steps={flowSteps} />

        <AboutPraxisComparison content={comparisonContent} />

        <AboutPraxisValueIndicators items={valueIndicators} />

        <AboutPraxisFaq items={faqItems} />

        <AboutPraxisFooterCta
          title="Ready to turn weak topics into consistent scores?"
          description="Start with a sample test, then generate your first personalized practice set."
          ctaLabel="Create Account"
          onCtaClick={() => navigate("/register")}
        />
      </div>
    </section>
  );
}
