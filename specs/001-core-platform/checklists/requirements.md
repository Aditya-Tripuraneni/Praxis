# Specification Quality Checklist: Core Platform - Math Practice Test Generator

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-03-11
**Feature**: specs/001-core-platform/spec.md

## Requirement Completeness

- [x] CHK001 Are all math topic categories explicitly enumerated with specific problem types per category? [Resolved, Spec FR-016 + research.md]
- [x] CHK002 Are question count limits (min/max) and their rationale documented? [Resolved, Spec FR-007: 5-50 questions]
- [x] CHK003 Are difficulty level definitions specified with concrete criteria for what makes a problem Easy vs Medium vs Hard? [Resolved, Spec FR-025: universal scaling framework]
- [x] CHK004 Are subscription plan details (price, billing cycle, what's included) specified? [Resolved, Spec FR-003: $5/month, unlimited generation]
- [x] CHK005 Are password requirements (length, complexity) defined for email/password registration? [Resolved, Spec FR-021: NIST SP 800-63B]
- [x] CHK006 Are the specific OAuth providers documented (Google only, or also GitHub, etc.)? [Resolved, Spec FR-002/FR-019: Google only at launch]

## Requirement Clarity

- [x] CHK007 Is "worked solutions" defined - does it mean step-by-step symbolic solution or just the final answer? [Resolved, Spec FR-011: final answer only]
- [x] CHK008 Is "proper mathematical notation" specified - LaTeX rendering, MathML, images, or specific library? [Resolved, Spec FR-018: KaTeX + SymPy latex()]
- [x] CHK009 Is "unique math problems" quantified - what guarantees uniqueness across tests? [Resolved: statistical uniqueness via randomized parameters, <0.01% collision probability, no dedup tracking needed]
- [x] CHK010 Is the meaning of "difficulty level" defined per topic (e.g., what makes a quadratic equation Hard vs Easy)? [Resolved, Spec FR-025: universal framework applied per topic]

## Requirement Consistency

- [x] CHK011 Are test-taking modes consistent - does the user answer one-at-a-time or all-at-once, and is this defined? [Resolved, Spec FR-010: all questions at once, paper-test style]
- [x] CHK012 Do the PDF formatting requirements align with the web display requirements for math notation? [Resolved — both use SymPy LaTeX output; KaTeX for web, LaTeX-to-PDF for print]
- [x] CHK013 Are the user entities consistent between the auth flow (User Story 1) and the test flow (User Story 2)? [Resolved — single User entity via Supabase Auth]

## Acceptance Criteria Quality

- [x] CHK014 Can "test generation completes in under 5 seconds" be objectively measured? [Resolved — measurable via API response time; target tightened to <3s in SC-009]
- [x] CHK015 Is "100% answer accuracy" verifiable without manual review for all problem types? [Resolved — backward construction + SymPy verification + automated test suite]
- [x] CHK016 Can "different questions at least 95% of the time" be tested with a finite test suite? [Resolved — generate N pairs with same config, compare, verify <5% collision rate]

## Scenario Coverage

- [x] CHK017 Are requirements defined for the user flow when subscription payment fails? [Resolved, Spec FR-022: show error, allow retry]
- [x] CHK018 Are requirements defined for what the unsubscribed user dashboard looks like? [Resolved, Spec FR-004: dashboard explaining app + subscription]
- [x] CHK019 Are requirements for session management (login persistence, token expiry) specified? [Resolved, Spec FR-020: 15-min access token, 7-day refresh token via Supabase]
- [x] CHK020 Are requirements for email verification after registration specified? [Resolved, Spec FR-001/FR-019: required via Supabase Auth]
- [x] CHK021 Are error states defined for when the generation engine fails mid-generation? [Resolved, Spec FR-026: silent retry up to 3 attempts per question before reporting failure]
- [x] CHK022 Are requirements specified for mobile responsiveness of the web interface? [Resolved, Spec FR-010: desktop web only at launch]

## Edge Case Coverage

- [x] CHK023 Is the behavior defined when a user requests more questions than available templates can provide? [Resolved — spec edge cases: inform user, generate max available]
- [x] CHK024 Are concurrent test generation scenarios addressed in requirements? [Resolved — spec edge cases: allowed, each independent]
- [x] CHK025 Is the mid-test subscription expiry scenario fully specified with acceptance criteria? [Resolved — spec edge cases: allow completion, block new generation]
- [x] CHK026 Are Stripe webhook failure/retry scenarios documented with specific handling requirements? [Resolved, Spec FR-028: idempotent handlers, Stripe built-in retry with exponential backoff up to 3 days]

## Non-Functional Requirements

- [x] CHK027 Are performance requirements specified beyond generation time (page load, API response times)? [Resolved, SC-009: pages <1.5s, API <200ms, generation <3s]
- [x] CHK028 Are data retention and deletion requirements specified (GDPR, student data)? [Resolved, Spec FR-023: delete all data on account closure]
- [x] CHK029 Are accessibility requirements (WCAG level) defined for the web interface? [Resolved, Spec FR-024: WCAG 2.1 Level AA]
- [x] CHK030 Are security requirements specified (rate limiting, CSRF, input sanitization)? [Resolved, Spec FR-027: 100 req/min per user via slowapi, CORS, CSRF, input sanitization]
- [x] CHK031 Are backup and data recovery requirements defined for the database? [Resolved: Supabase free tier includes daily automatic backups with 7-day retention]

## Dependencies and Assumptions

- [x] CHK032 Is the assumption of Supabase free-tier PostgreSQL validated against data volume needs? [Resolved — Supabase free: 500MB DB, sufficient for launch scale of ~100 users]
- [x] CHK033 Are Stripe API rate limits and their impact on concurrent users documented? [Resolved: Stripe allows 100 req/s live mode; at 100 concurrent users we'd hit ~1-2 req/s max, not a concern]
- [x] CHK034 Is the assumption of Render.com free tier validated against cold-start latency impact? [Resolved, SC-010: ~30s cold start after 15-min idle accepted and documented]
- [x] CHK035 Are SymPy version compatibility requirements documented? [Resolved: pin to latest stable in requirements.txt, tested via CI, no special compatibility concerns]

## Notes

- **35/35 items resolved** — specification is ready for task breakdown
- Difficulty framework (CHK003/010) defined in FR-025; research.md has per-topic examples
- All user decisions captured in spec FRs and success criteria
- Next step: `/speckit.tasks` to generate implementation task breakdown
