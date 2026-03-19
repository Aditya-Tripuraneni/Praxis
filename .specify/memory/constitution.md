<!--
  Sync Impact Report
  Version change: N/A → 1.3.0
  v1.0.0: Initial constitution with 6 principles
  v1.1.0: Added CI/CD (GitHub Actions)
  v1.2.0: Switched to Supabase Auth, added TypeScript, KaTeX, $5/month, Cloudflare
  v1.3.0: Clarified Principle V for layered development, updated for preview-only UX
  Templates requiring updates:
    - .specify/templates/plan-template.md ⚠ pending (fill on first /speckit.plan)
    - .specify/templates/spec-template.md ⚠ pending (fill on first /speckit.specify)
    - .specify/templates/tasks-template.md ⚠ pending (fill on first /speckit.tasks)
  Follow-up TODOs: None
-->

# ProblemGenerator Constitution

## Core Principles

### I. Algorithmic Generation First

All math question generation MUST be purely algorithmic using structured
templates with randomized parameters. No AI or LLM involvement in question
creation. Every generated question MUST have a deterministic, verifiable
correct answer computed by the same engine that generates the problem.

- Problem templates define the structure; parameters are randomized within
  validated constraints
- The generation engine MUST be a self-contained Python module independent
  of the web framework
- SymPy MUST be used for symbolic math computation and answer verification
- Every problem type MUST define: parameter ranges, generation logic,
  solution logic, and difficulty scaling rules

### II. Test-Verified Math

Math generation and answer computation MUST have comprehensive test
coverage approaching TDD rigor. No problem type ships without tests
proving correctness across parameter ranges.

- Every problem template MUST have unit tests covering: normal cases,
  boundary parameters, and known edge cases
- Answer verification tests MUST confirm the generated answer is correct
  by independent computation (e.g., substituting answer back into equation)
- Regression tests MUST be added for any bug found in generation or solving
- Test coverage for the generation engine MUST be maintained above 90%
- Other application code follows test-after with strong coverage

### III. Separation of Concerns

The system is composed of clearly separated modules that can be developed,
tested, and deployed independently.

- **Generation Engine**: Pure Python library. No web framework dependencies.
  Input: topic + difficulty + params. Output: problem + answer.
- **Backend API**: FastAPI application. Handles auth, billing, PDF generation,
  and orchestrates the generation engine.
- **Frontend**: React SPA. Handles UI, test-taking experience, user flows.
  Communicates with backend via REST API.
- Modules MUST NOT have circular dependencies
- The generation engine MUST be usable without the web stack (importable
  as a library, testable standalone)

### IV. Free-Tier Deployable

The architecture MUST be deployable on free-tier hosting services without
modification. No vendor lock-in to paid cloud providers.

- Frontend deploys to Vercel free tier
- Backend deploys to Render.com or Railway free tier
- Database and auth use Supabase free tier (PostgreSQL + Auth)
- Cloudflare (free tier) in front of all endpoints for DDoS protection
- No reliance on cloud-specific services (AWS Lambda, GCP Cloud Functions, etc.)
- Docker containerization for local development and portability
- Environment configuration via environment variables (12-factor app)

### V. Subscription-Gated Access

In production, all test generation is behind a Stripe-managed paywall
with a single subscription plan. Authentication and billing are
first-class concerns. During development, the implementation follows a
layered approach: Layer 1 (core product) operates without auth or
billing, Layer 2 adds auth, Layer 3 adds Stripe billing.

- User accounts MUST support email/password and Google OAuth via Supabase Auth
- Email verification MUST be required before account activation
- Stripe handles all payment processing; single plan at $5/month
- No free tier or trial: subscription required for test generation
- User data and purchase activity stored in Supabase PostgreSQL
- Auth uses Supabase JWT tokens (access + refresh, 2-token strategy)
- Auth state MUST be verified on every protected API request
- User data MUST be deleted upon account closure (WCAG/privacy compliance)

### VI. Simplicity First

Start with the simplest viable implementation. Add complexity only when
a concrete need arises, not for hypothetical future requirements.

- Python and FastAPI chosen for simplicity and library ecosystem breadth
- YAGNI: do not build features or abstractions before they are needed
- Prefer standard library and well-maintained packages over custom solutions
- Flat project structure until complexity demands nesting
- No microservices: monorepo with clear module boundaries

## Technology Constraints

| Layer          | Technology     | Version   | Notes                          |
|----------------|---------------|-----------|--------------------------------|
| Language       | Python        | 3.12+     | Backend + generation engine    |
| Web Framework  | FastAPI       | Latest    | REST API                       |
| Frontend       | React         | Latest    | SPA, deployed to Vercel        |
| Database + Auth | Supabase     | Free tier | PostgreSQL + Auth + email verification |
| Math Engine    | SymPy         | Latest    | Symbolic computation + LaTeX output |
| PDF Generation | ReportLab or WeasyPrint | Latest | PDF output for tests  |
| Payments       | Stripe        | Latest SDK | $5/month subscription + webhooks |
| Frontend Lang  | TypeScript    | Latest    | Strict typing for React SPA    |
| Math Rendering | KaTeX         | Latest    | LaTeX rendering in browser     |
| Testing        | pytest        | Latest    | With pytest-asyncio            |
| CI/CD          | GitHub Actions | N/A      | Tests + lint on every PR       |
| Containerization | Docker      | Latest    | Local dev + deployment         |

## Development Workflow

### Branch Strategy

- `main` branch is always deployable
- Feature branches created via `/speckit.specify` with auto-numbered naming
- PRs require passing tests before merge

### CI/CD Pipeline

- GitHub Actions MUST run on every pull request to `main`
- CI pipeline MUST execute: linting, formatting check, and full test suite
- PRs MUST NOT be merged with failing CI checks
- CI configuration lives in `.github/workflows/`

### Code Quality Gates

- All code MUST pass linting (ruff) and formatting (ruff format)
- Generation engine changes MUST include tests
- API endpoint changes MUST include integration tests
- No secrets or credentials in code; use environment variables

### Commit Discipline

- Atomic commits: one logical change per commit
- Descriptive commit messages following conventional commits format
- Reference spec-kit task IDs in commits when applicable

## Governance

This constitution defines the non-negotiable principles for the
ProblemGenerator project. All development decisions, code reviews, and
architectural choices MUST comply with these principles.

- Amendments require: documentation of change, rationale, and update to
  this file with version increment
- Version follows semantic versioning (MAJOR.MINOR.PATCH)
- Constitution supersedes ad-hoc decisions; conflicts resolved by
  referring to principles in order (I through VI)

**Version**: 1.3.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-03-11
