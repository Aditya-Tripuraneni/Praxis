# Praxis

Praxis is a production-ready math practice platform built to turn high‑quality study time into a repeatable, trackable system. It exists because students and educators shouldn’t have to choose between speed and rigor: Praxis generates structured, topic‑balanced tests on demand, packages them into downloadable PDFs, and tracks growth over time — all while staying cleanly deployable as a modern SaaS.

If you’re an engineer, Praxis reads like a disciplined product: a React + TypeScript frontend, a FastAPI backend, strong API boundaries, security‑first defaults, and a deployment story that treats production as a first‑class environment. If you’re a recruiter, it’s a full‑stack application with billing, authentication, and user analytics — and a codebase that’s already built to run in the real world.

## The experience it delivers

Praxis takes a learner from “I need practice” to “I can show measurable progress” in a few minutes:

- Pick topics and difficulty, generate a fresh test, and immediately start working.
- Download a clean PDF of the test (with optional answers and solutions) for offline or classroom use.
- Save tests and replay them later (tutor tier), keeping learning paths consistent.
- Track lifetime counts, per‑topic distribution, and practice streaks.
- Subscribe, upgrade, or cancel seamlessly with Stripe billing.

Behind the scenes, Praxis combines a deterministic test generator with LaTeX‑based PDF rendering, while keeping the user experience responsive through caching and dedicated compute isolation for heavy work.

## Architecture at a glance

- **Frontend:** React 18 + TypeScript + Vite, KaTeX math rendering, routed SPA.
- **Backend:** FastAPI with typed request/response models and rate‑limited endpoints.
- **Data & Auth:** Supabase for auth, user stats, and saved tests.
- **Billing:** Stripe checkout + webhook processing for subscription lifecycle.
- **PDF pipeline:** Tectonic‑powered LaTeX compilation, cached and isolated in its own thread pool.

The result is a stack that’s familiar to engineers but purpose‑built for production reliability.

## Production posture

Praxis is intentionally built like a product you can ship:

- **Multi‑stage Docker builds** with pinned base images for supply‑chain integrity.
- **Non‑root production containers** and explicit runtime hardening.
- **Security headers + CSP** enforced at the edge (Nginx) and in the API.
- **Rate limiting** on auth, billing, and generation routes.
- **Structured security logging** for auth‑related events.
- **Health checks** for both API and frontend containers.
- **Environment‑driven config** for clean separation of dev/test/prod.
- **CI pipelines** that lint, type‑check, test, and build on every PR.

This isn’t just a demo — it’s an application that treats uptime, privacy, and scalability as defaults.

## Environments & deployment story

Praxis ships with distinct development and production behaviors:

- **Local dev:** Docker Compose spins up backend + frontend with hot reload.
- **Production:** Docker builds use hardened images and minimal dependencies.
- **Deployments:** The repository includes a full production deployment guide
  (Supabase + Stripe + Render) in [`docs/production-deployment-guide.md`](docs/production-deployment-guide.md).

The same code runs everywhere; only environment variables change between dev and prod.

## Local development

1. Create a `.env` file in the repo root with:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_JWT_SECRET`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_STUDENT_PRICE_ID`
   - `STRIPE_TUTOR_PRICE_ID`
2. Start the stack:
   ```bash
   docker compose up --build
   ```
3. Frontend: http://localhost:5173  
   Backend health: http://localhost:8000/api/health

## Testing & quality gates

From the repository root:

```bash
make lint
make test-backend
make test-frontend
```

CI runs:
- **Backend:** Ruff linting + pytest with coverage threshold (80%).
- **Frontend:** ESLint, TypeScript type checks, Vitest, and production build.

## Why Praxis exists

Praxis was built to make disciplined practice feel effortless. Educators can generate consistent material without manual authoring, students can practice in a way that feels curated, and the platform’s subscription model keeps the system sustainable. It’s the kind of product that’s both pedagogically useful and technically scalable — a training engine wrapped in a production‑grade SaaS.
