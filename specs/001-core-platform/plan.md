# Implementation Plan: Core Platform - Math Practice Test Generator

**Branch**: `001-core-platform` | **Date**: 2026-03-11 | **Spec**: specs/001-core-platform/spec.md
**Input**: Feature specification from `specs/001-core-platform/spec.md`

## Summary

Build a web-based math practice test platform where subscribed students
select topics and difficulty, generate algorithmically-created tests with
randomized problems, take tests online, view scores with answer keys, and
download PDF versions. Backend is Python/FastAPI with a standalone SymPy-based
generation engine; frontend is React SPA; data in PostgreSQL; payments via Stripe.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, SymPy, NumPy, slowapi, Stripe SDK, supabase-py, React + TypeScript
**Storage + Auth**: Supabase (PostgreSQL + Auth + email verification)
**Testing**: pytest with pytest-asyncio
**CI/CD**: GitHub Actions (lint + test on every PR)
**Target Platform**: Web (Vercel for frontend, Render.com for backend)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**: Test generation < 3s for 50 questions; PDF generation < 10s; pages < 1.5s; API < 200ms
**Constraints**: Free-tier deployable; no cloud vendor lock-in; Cloudflare for DDoS protection
**Scale/Scope**: ~100 concurrent users at launch; single subscription plan

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Algorithmic Generation First | PASS | SymPy-based engine, no AI/LLM |
| II. Test-Verified Math | PASS | pytest required for all problem types |
| III. Separation of Concerns | PASS | Engine / API / Frontend separated |
| IV. Free-Tier Deployable | PASS | Vercel + Render + Supabase |
| V. Subscription-Gated Access | PASS | Stripe integration, no free tier |
| VI. Simplicity First | PASS | Monorepo, standard stack |

## Project Structure

### Documentation (this feature)

```text
specs/001-core-platform/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Math topics research (~130+ problem types)
├── checklists/          # Requirements quality checklists
│   └── requirements.md  # Spec quality validation
└── tasks.md             # Task breakdown (pending /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── models/              # Pydantic request/response models
│   │   ├── test.py          # Test + question models
│   │   └── template.py      # ProblemTemplate model
│   ├── api/
│   │   ├── auth.py          # Auth endpoints (wraps Supabase Auth)
│   │   ├── billing.py       # Stripe subscription endpoints + webhooks
│   │   ├── tests.py         # Test generation + taking endpoints
│   │   └── pdf.py           # PDF generation endpoint
│   ├── services/
│   │   ├── auth.py          # Supabase Auth integration (JWT verification)
│   │   ├── billing.py       # Stripe service layer ($5/month plan)
│   │   ├── test_service.py  # Test orchestration (calls engine)
│   │   └── pdf_service.py   # PDF generation service
│   └── engine/              # Math generation engine (standalone)
│       ├── __init__.py
│       ├── generator.py     # Core generation orchestrator
│       ├── registry.py      # Problem template registry
│       ├── types.py         # Shared types (Problem, Answer, etc.)
│       └── topics/          # Topic-specific templates
│           ├── algebra.py
│           ├── functions.py
│           ├── trigonometry.py
│           └── calculus.py
├── tests/
│   ├── unit/
│   │   └── engine/          # Generation engine unit tests
│   ├── integration/
│   │   ├── test_auth.py
│   │   ├── test_billing.py
│   │   └── test_generation.py
│   └── conftest.py
├── requirements.txt
├── Dockerfile
└── pyproject.toml

frontend/
├── src/
│   ├── components/
│   │   ├── Layout/          # Header, footer, navigation
│   │   ├── Auth/            # Login, register, OAuth buttons
│   │   ├── TestConfig/      # Topic/difficulty selector
│   │   ├── TestPreview/     # Generated questions display (read-only)
│   │   └── MathRenderer/    # LaTeX/math notation rendering
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Generate.tsx
│   │   └── Preview.tsx
│   ├── services/
│   │   ├── api.ts           # Backend API client
│   │   ├── supabase.ts      # Supabase client + auth state
│   │   └── stripe.ts        # Stripe checkout integration
│   ├── App.tsx
│   └── main.tsx
├── tests/
├── package.json
├── vite.config.ts
└── Dockerfile

.github/
└── workflows/
    ├── backend.yml          # Python lint + test
    └── frontend.yml         # React lint + test + build

docker-compose.yml           # Local development (backend + db + frontend)
```

**Structure Decision**: Web application layout (Option 2) with `backend/`
and `frontend/` separation. The math generation engine lives inside
`backend/app/engine/` as a standalone module with no FastAPI dependencies,
satisfying Constitution Principle III (Separation of Concerns).

**Schema Management**: Database tables managed via Supabase Dashboard
(UI) or Supabase CLI migrations. No ORM migration tool (Alembic) needed.

## Implementation Order

The implementation follows a layered strategy: build the core product
first, then layer on auth and billing. Each layer must be fully testable
independently before the next layer is added.

### Layer 1: Core Product (US1 + US2) — No auth, no billing
- Math generation engine (standalone Python module)
- Backend API for generation + PDF (no auth middleware)
- React frontend: topic selector, question preview with math rendering, PDF download
- **Milestone**: Developer can generate tests, preview questions on screen, download PDFs with answer keys

### Layer 2: Authentication (US3) — No billing
- Supabase Auth integration (email/password + Google OAuth + email verification)
- Protected routes on frontend, JWT verification on backend
- User dashboard with access to generation
- **Milestone**: Users can register, login, and access the test generator

### Layer 3: Billing (US4) — Final layer
- Stripe integration ($5/month subscription)
- Subscription-gated access (unsubscribed users see info dashboard)
- Webhook handlers for subscription lifecycle events
- Cloudflare DDoS protection
- **Milestone**: Full production-ready platform with paywall

## Complexity Tracking

No constitution violations to justify.
