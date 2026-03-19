# Tasks: Core Platform - Math Practice Test Generator

**Input**: `specs/001-core-platform/spec.md`, `specs/001-core-platform/plan.md`, `specs/001-core-platform/research.md`
**Prerequisites**: plan.md (required), spec.md (required), research.md (required)

**Total: 85 tasks across 3 layers**

> **API Keys & Secrets**: All third-party API keys (Supabase, Stripe, Google OAuth) must be created by the developer manually on a separate machine. Each setup task documents exactly which keys are needed. Never commit `.env` files to version control.

---

## Layer 1: Core Product (US1 + US2) — No auth, no billing

### Phase 1: Setup

- [ ] T001 Create project root scaffolding: `docker-compose.yml`, `.dockerignore`, `.gitignore`, `.editorconfig`. Docker Compose with backend (Python 3.12, port 8000) and frontend (Node 20, port 5173) services on shared network.

- [ ] T002 [P] Create backend project skeleton: `backend/pyproject.toml` (ruff config), `backend/requirements.txt` (fastapi, uvicorn, sympy, pydantic>=2.0, reportlab, numpy), dev deps (pytest, pytest-asyncio, pytest-cov, httpx, ruff), `backend/Dockerfile` (multi-stage, Python 3.12-slim), `backend/app/main.py` (minimal FastAPI with CORS + health check), `backend/app/config.py` (Pydantic BaseSettings).

- [ ] T003 [P] Create frontend project skeleton: Vite + React + TypeScript init, deps (react-router-dom, katex, axios), `frontend/vite.config.ts` (proxy /api to localhost:8000), `frontend/src/App.tsx` (React Router with placeholder routes), `frontend/Dockerfile` (Node 20-alpine + nginx), minimal CSS reset.

**Checkpoint**: `docker-compose up` starts both services, backend health check responds.

---

### Phase 2: Engine Foundation

- [ ] T004 Define engine types in `backend/app/engine/types.py`: `Difficulty` enum (EASY/MEDIUM/HARD), `Topic` enum, `GeneratedProblem` dataclass (question_latex, answer_latex, topic, difficulty, metadata), `ProblemTemplate` protocol (generate method), `GenerationConfig` dataclass (topics, difficulty, count 5-50, seed).

- [ ] T005 Implement template registry in `backend/app/engine/registry.py`: `TemplateRegistry` class with register/get_templates/get_all_topics methods, module-level singleton, `@register_template` decorator.

- [ ] T006 Implement core generator in `backend/app/engine/generator.py`: `generate_test(config, registry)` function — distributes questions across topics, selects templates with weighted random, silent retry up to 3 attempts per question (FR-026), shuffles output, raises `GenerationError` on total failure.

- [ ] T007 Set up engine public API in `backend/app/engine/__init__.py`: export generate_test, GeneratedProblem, GenerationConfig, Difficulty, Topic, registry.

**Checkpoint**: Engine importable standalone, `from app.engine import generate_test` works.

---

### Phase 3: Engine Topics — Algebra

- [ ] T008 [P] Algebra: Linear equations in `backend/app/engine/topics/algebra.py` — `LinearEquationTemplate` (ax+b=c) and `TwoStepLinearTemplate` (ax+b=cx+d). Backward construction: pick answer x, generate coefficients. Easy/Medium/Hard scaling per FR-025.

- [ ] T009 [P] Algebra: Quadratic equations (append to algebra.py) — `QuadraticFactoringTemplate` (pick roots, expand) and `QuadraticFormulaTemplate` (control discriminant). Easy: integer roots a=1. Medium: a>1. Hard: irrational roots.

- [ ] T010 [P] Algebra: Polynomial operations (append to algebra.py) — `PolynomialAddSubTemplate` and `PolynomialMultiplyTemplate`. Easy: degree 2. Medium: degree 3, mixed signs. Hard: degree 4+, binomial × trinomial.

- [ ] T011 [P] Algebra: Systems of equations (append to algebra.py) — `SystemOf2LinearTemplate`. Backward: pick solution (x,y), generate two equations. Easy: small positive integers. Medium: mixed signs. Hard: fractional solutions.

- [ ] T012 [P] Algebra: Exponents & radicals (append to algebra.py) — `ExponentSimplifyTemplate` and `RadicalSimplifyTemplate`. Backward for radicals: pick simplified form, square to get radicand.

**Checkpoint**: All algebra templates registered, generate problems at all difficulty levels.

---

### Phase 4: Engine Topics — Functions, Trig, Calculus

- [ ] T013 [P] Functions: Evaluation & composition in `backend/app/engine/topics/functions.py` — `FunctionEvalTemplate` (f(a) for linear/quadratic/rational) and `FunctionCompositionTemplate` (f(g(a))).

- [ ] T014 [P] Functions: Domain & inverse (append to functions.py) — `DomainTemplate` (rational/radical domain) and `InverseFunctionTemplate` (linear/rational inverse). LaTeX uses interval/set notation.

- [ ] T015 [P] Trigonometry: Unit circle & evaluation in `backend/app/engine/topics/trigonometry.py` — `TrigEvalTemplate` (sin/cos/tan at standard angles) and `InverseTrigTemplate` (arcsin/arccos/arctan). Backward: pick angle, compute trig value.

- [ ] T016 [P] Trigonometry: Identities & equations (append to trigonometry.py) — `TrigSimplifyTemplate` (Pythagorean/double-angle) and `TrigEquationTemplate` (solve sin(x)=a on [0,2π)). Easy: single identity. Hard: multi-step.

- [ ] T017 [P] Calculus: Limits & derivatives in `backend/app/engine/topics/calculus.py` — `LimitTemplate` (direct sub, 0/0 form, rationalization) and `DerivativeBasicTemplate` (power rule, sum/difference).

- [ ] T018 [P] Calculus: Chain rule & integrals (append to calculus.py) — `ChainRuleTemplate` (nested functions) and `BasicIntegralTemplate` (power rule, simple u-sub). Backward for integrals: pick antiderivative, differentiate.

**Checkpoint**: All 4 topic modules (algebra, functions, trig, calculus) with ~20 template classes total, all generating valid LaTeX + answers.

---

### Phase 5: Backend API

- [ ] T019 Define Pydantic request/response models in `backend/app/models/test.py` and `backend/app/models/template.py`: `GenerateRequest` (topics, difficulty, count, seed), `QuestionResponse` (id, question_latex, answer_latex, topic, difficulty), `TestResponse` (test_id UUID, questions, created_at, config), `TopicInfo` (id, name, subtopics, difficulties).

- [ ] T020 Implement test generation service in `backend/app/services/test_service.py`: `TestService` class — maps request to GenerationConfig, calls engine, maps to response, caches result in memory (LRU, 1hr TTL, max 100 entries) for PDF retrieval.

- [ ] T021 Create API endpoints in `backend/app/api/tests.py`: `POST /api/tests/generate` (validate + generate + return), `GET /api/topics` (registry info), `GET /api/tests/{test_id}` (retrieve from cache). Wire routers into main.py.

- [ ] T022 Create PDF endpoint in `backend/app/api/pdf.py`: `GET /api/tests/{test_id}/pdf` — retrieve test from cache, call PdfService, return StreamingResponse with application/pdf. Query param `include_answers` (default true).

**Checkpoint**: API endpoints respond, can generate tests and retrieve them via curl.

---

### Phase 6: PDF Generation

- [ ] T023 Implement PDF service in `backend/app/services/pdf_service.py`: ReportLab-based — A4 layout, 1-inch margins, header (title, date), numbered question list with rendered LaTeX, separate "Answer Key" page, page numbers in footer.

- [ ] T024 Implement LaTeX-to-image renderer in `backend/app/services/latex_renderer.py`: `render_latex_to_image(latex_str, font_size)` using matplotlib mathtext renderer, memory-cached (LRU), target <8s for 50 questions.

**Checkpoint**: PDF downloads contain properly rendered math questions + answer key on separate pages.

---

### Phase 7: Frontend

- [ ] T025 [P] Build layout shell: `frontend/src/components/Layout/` (Header, Footer, Layout), update App.tsx with routes wrapped in Layout. Header: app title + nav links. Basic CSS.

- [ ] T026 [P] Build API service layer: `frontend/src/services/api.ts` + `frontend/src/types/index.ts` — TypeScript interfaces mirroring backend models, axios functions (fetchTopics, generateTest, getTest, downloadPdf), timeout config.

- [ ] T027 [P] Build KaTeX math renderer: `frontend/src/components/MathRenderer/` — accepts latex string, renders via KaTeX renderToString, displayMode toggle, error fallback (raw LaTeX in monospace), React.memo + useMemo.

- [ ] T028 Build landing page: `frontend/src/pages/Landing.tsx` — hero section, tagline, "Get Started" button → /generate, feature bullets.

- [ ] T029 Build test config components: `frontend/src/components/TestConfig/` — TopicSelector (checkboxes from API, min 1 selected), DifficultySelector (radio: Easy/Medium/Hard), QuestionCount (number input 5-50, default 20).

- [ ] T030 Build generate page: `frontend/src/pages/Generate.tsx` — composes TestConfig components, "Generate Test" button with form validation, loading spinner during API call, navigate to /preview/:testId on success, error display with retry.

- [ ] T031 Build test preview components: `frontend/src/components/TestPreview/` — TestHeader (config summary), QuestionCard (number + MathRenderer), QuestionList (scrollable cards with optional answer toggle).

- [ ] T032 Build preview page: `frontend/src/pages/Preview.tsx` — fetch test by testId, compose TestHeader + QuestionList, "Download PDF" button (with include-answers checkbox), "Generate New Test" button, handle 404 (expired test).

**Checkpoint**: Full user flow works — landing → generate → preview → download PDF. No login needed.

---

### Phase 8: Testing

- [ ] T033 [P] Engine unit tests: types, registry, generator in `backend/tests/unit/engine/` — test enum values, GenerationConfig validation, registry register/filter, generator count/seeding/retry/distribution/GenerationError.

- [ ] T034 [P] Engine unit tests: algebra templates in `backend/tests/unit/engine/test_algebra.py` — all algebra templates at all difficulties, verify answer by back-substitution with SymPy, test LaTeX validity, test determinism with seed, test variation across generations.

- [ ] T035 [P] Engine unit tests: functions, trig, calculus in `backend/tests/unit/engine/test_functions.py`, `test_trigonometry.py`, `test_calculus.py` — same pattern as T034, verify derivatives by SymPy diff(), verify domain restrictions, verify trig range.

- [ ] T036 Integration tests: API endpoints in `backend/tests/integration/test_api.py` — health check, topics, generate (valid/invalid), get test (valid/404), PDF (valid/404, with/without answers), performance assertions (<3s generation, <10s PDF).

- [ ] T037 [P] Frontend component tests: `MathRenderer.test.tsx`, `TopicSelector.test.tsx`, `DifficultySelector.test.tsx`, `Generate.test.tsx` — vitest + @testing-library/react + msw, test rendering, validation, API calls, loading states.

**Checkpoint**: >90% engine test coverage, all API integration tests pass.

---

### Phase 9: CI/CD

- [ ] T038 [P] GitHub Actions backend workflow: `.github/workflows/backend.yml` — trigger on backend/** changes, jobs: ruff lint + format check, pytest with coverage (fail if engine <90%), cache pip deps.

- [ ] T039 [P] GitHub Actions frontend workflow: `.github/workflows/frontend.yml` — trigger on frontend/** changes, jobs: eslint + tsc --noEmit, vitest with coverage, vite build. Cache node_modules.

- [ ] T040 Docker Compose verification + dev scripts: verify docker-compose up works end-to-end, Makefile with `make dev`, `make test-backend`, `make test-frontend`, `make lint`. Backend hot-reload (uvicorn --reload), frontend hot-reload (Vite dev server).

**Layer 1 Checkpoint**: Developer can generate math tests, preview with rendered LaTeX, download PDFs — all without any login or payment. 40 tasks complete.

---
---

## Layer 2: Authentication (US3) — T100 Series

**Prerequisite**: Layer 1 must be fully working before starting Layer 2.

### Supabase Setup

- [ ] T100 Configure Supabase environment: `backend/.env` (SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET), `frontend/.env` (VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY), `.env.example` files for both, update `backend/app/config.py`, add .env to .gitignore. **Keys from**: Supabase Dashboard > Settings > API.

- [ ] T101 Configure Supabase Auth providers (developer does manually): enable email/password, enable Google OAuth, enable email verification, set access token to 900s (15 min), refresh token to 604800s (7 days). **Keys needed**: Google OAuth Client ID/Secret from Google Cloud Console. Deliverable: `docs/supabase-setup.md` with step-by-step instructions.

- [ ] T102 Install Supabase dependencies: add `supabase`, `python-jose[cryptography]` to `backend/requirements.txt`, add `@supabase/supabase-js` to `frontend/package.json`.

---

### Backend Auth

- [ ] T103 Implement auth service in `backend/app/services/auth.py`: Supabase client init, `verify_jwt()` (decode + validate), `get_user_by_id()`, `delete_user()` (FR-023), `check_password_breached()` (HaveIBeenPwned k-anonymity API for NIST SP 800-63B). Typed exceptions.

- [ ] T104 Implement auth dependency in `backend/app/api/dependencies.py`: `get_current_user` FastAPI dependency — extract Bearer token, call verify_jwt, return user or 401. Handle expired tokens with `token_expired` error code.

- [ ] T105 Create auth endpoints in `backend/app/api/auth.py`: `POST /api/auth/signup` (validate password + breached check + Supabase sign_up), `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET /api/auth/me` (protected), `DELETE /api/auth/account` (protected, FR-023).

- [ ] T106 Register auth router in `backend/app/main.py`: include auth_router at /api/auth, add `get_current_user` dependency to /api/tests and /api/pdf routers. Keep /api/health unprotected.

- [ ] T107 Add auth Pydantic models in `backend/app/models/auth.py`: SignupRequest, LoginRequest, RefreshRequest, AuthResponse, UserProfile, AuthError.

---

### Frontend Auth

- [ ] T108 [P] Initialize Supabase client: `frontend/src/services/supabase.ts` — create client, export signUp, signIn, signInWithGoogle, signOut, getSession, onAuthStateChange helpers. Frontend talks to Supabase directly for auth, uses backend with JWT for generation/PDF.

- [ ] T109 [P] Create auth context: `frontend/src/context/AuthContext.tsx` — AuthProvider with onAuthStateChange subscription, stores session/user/loading/isAuthenticated, provides auth functions. Export useAuth() hook. Wrap App in AuthProvider.

- [ ] T110 Build Login page: `frontend/src/pages/Login.tsx` — email/password form, "Sign in with Google" button, link to register, error display, redirect to Dashboard on success. WCAG AA accessible.

- [ ] T111 Build Register page: `frontend/src/pages/Register.tsx` — email/password/confirm form, password requirements display (NIST), calls backend signup (breached check), success state with verification email message, Google signup alternative.

- [ ] T112 Build ProtectedRoute: `frontend/src/components/Auth/ProtectedRoute.tsx` — check isAuthenticated, show spinner if loading, redirect to /login if not authenticated (preserve intended destination).

- [ ] T113 Build Dashboard page: `frontend/src/pages/Dashboard.tsx` — user info, "Generate New Test" button → /generate, "Sign Out" button, "Delete Account" button with confirmation modal (FR-023).

- [ ] T114 Update App routing: add /login, /register routes (public), wrap /generate, /preview, /dashboard in ProtectedRoute, redirect authenticated users from /login to /dashboard, OAuth callback route.

- [ ] T115 Update Generate and Preview pages with auth: modify `api.ts` to auto-attach Authorization: Bearer header from session, handle 401 by attempting token refresh + retry.

- [ ] T116 [P] Build auth UI sub-components: `GoogleOAuthButton.tsx`, `PasswordInput.tsx` (show/hide toggle, length indicator), `EmailVerificationBanner.tsx` (resend link).

---

### Auth Testing

- [ ] T117 [P] Backend auth service unit tests: `backend/tests/unit/test_auth_service.py` — verify_jwt (valid/expired/malformed), check_password_breached (mocked API), password length validation.

- [ ] T118 [P] Backend auth endpoint integration tests: `backend/tests/integration/test_auth.py` — signup, login, refresh, me, delete account, protected endpoints return 401 without auth.

- [ ] T119 [P] Frontend auth flow tests: `frontend/tests/auth.test.tsx` — login/register forms, Google OAuth trigger, ProtectedRoute behavior, session persistence, 401 handling.

- [ ] T120 End-to-end auth smoke test: `backend/tests/integration/test_auth_e2e.py` — full flow: signup → verify → login → access protected → refresh → logout → verify 401. Delete account → verify cleanup.

**Layer 2 Checkpoint**: Users can register, verify email, log in (email or Google), access dashboard, generate tests, download PDFs, and delete their account. All generation/PDF endpoints require authentication. 21 tasks complete.

---
---

## Layer 3: Billing (US4) — T200 Series

**Prerequisite**: Layer 2 must be fully working before starting Layer 3.

### Stripe Setup

- [ ] T200 Configure Stripe environment: add STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_ID to `backend/.env`, VITE_STRIPE_PUBLISHABLE_KEY to `frontend/.env`, update .env.example files and config.py. **Keys from**: Stripe Dashboard > Developers > API keys (use test keys for dev).

- [ ] T201 Create Stripe product and price (developer does manually): product "ProblemGenerator Subscription", price $5/month recurring USD. Record price_id. Deliverable: `docs/stripe-setup.md` with step-by-step instructions including local webhook forwarding with Stripe CLI.

- [ ] T202 Install Stripe dependencies: add `stripe` to `backend/requirements.txt`, add `@stripe/stripe-js`, `@stripe/react-stripe-js` to `frontend/package.json`.

---

### Backend Billing

- [ ] T203 Create subscriptions table (Supabase Dashboard or migration file `backend/supabase/migrations/001_subscriptions.sql`): user_id (FK auth.users ON DELETE CASCADE), stripe_customer_id, stripe_subscription_id (unique), status (active/cancelled/past_due/expired), period dates, RLS enabled.

- [ ] T204 Implement billing service in `backend/app/services/billing.py`: `create_checkout_session()` (create Stripe Customer + Checkout Session, return URL), `get_subscription_status()` (query Supabase), `cancel_subscription()` (Stripe cancel_at_period_end), `handle_webhook_event()` (verify signature, dispatch). Idempotent handlers (FR-028) for checkout.session.completed, invoice.payment_succeeded, invoice.payment_failed, customer.subscription.updated, customer.subscription.deleted.

- [ ] T205 Add billing Pydantic models in `backend/app/models/billing.py`: CheckoutSessionResponse, SubscriptionStatus (with is_active computed), CancelSubscriptionResponse.

- [ ] T206 Create billing endpoints in `backend/app/api/billing.py`: `POST /api/billing/create-checkout-session` (protected), `GET /api/billing/subscription-status` (protected), `POST /api/billing/cancel-subscription` (protected), `POST /api/billing/webhook` (unprotected, Stripe signature verification, always return 200).

- [ ] T207 Register billing router and subscription middleware: include billing_router at /api/billing, create `require_active_subscription` dependency in dependencies.py, add to /api/tests and /api/pdf routers (stacked on auth). Webhook endpoint exempt from auth/subscription middleware.

- [ ] T208 Handle account deletion cascade: modify `backend/app/services/auth.py` delete_user() — cancel Stripe subscription, delete Stripe customer, DB row cleaned by ON DELETE CASCADE (FR-023).

---

### Frontend Billing

- [ ] T209 [P] Initialize Stripe client: `frontend/src/services/stripe.ts` — loadStripe with publishable key, export redirectToCheckout helper.

- [ ] T210 [P] Create subscription context: `frontend/src/context/SubscriptionContext.tsx` — fetch subscription status on mount/auth change, provide isSubscribed/loading/subscribe/cancelSubscription. Export useSubscription() hook.

- [ ] T211 Update Dashboard for subscription gate: modify `frontend/src/pages/Dashboard.tsx` — if subscribed: show generate button + subscription status badge + cancel option. If not subscribed: show app explanation + "$5/month Subscribe" button.

- [ ] T212 Build checkout pages: `frontend/src/pages/CheckoutSuccess.tsx` (subscription activated, auto-refresh status) and `frontend/src/pages/CheckoutCancel.tsx` (checkout cancelled, retry link). Add routes /checkout/success and /checkout/cancel.

- [ ] T213 Add subscription gate: `frontend/src/components/Auth/SubscriptionGate.tsx` — check isSubscribed, redirect to /dashboard if not. Apply to Generate and Preview pages (frontend guard, backend also enforces).

---

### Security Hardening

- [ ] T214 Implement rate limiting: add slowapi to requirements, configure Limiter in main.py (100/minute per user, fallback to IP), add SlowAPIMiddleware, 429 handler with Retry-After. Exempt webhook endpoint.

- [ ] T215 Configure CORS: update CORSMiddleware — allow_origins from FRONTEND_URL env (not * in production), specific methods/headers, allow_credentials true.

- [ ] T216 Implement CSRF protection: add starlette-csrf to requirements, add middleware to main.py, CSRF token in cookie, frontend reads and sends X-CSRF-Token header. Exempt webhook endpoint.

- [ ] T217 Add security headers middleware: X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Strict-Transport-Security, Content-Security-Policy (allow KaTeX, Supabase, Stripe). Validate Pydantic strict types.

- [ ] T218 Write Cloudflare setup documentation: `docs/cloudflare-setup.md` — step-by-step free tier setup: add domain, configure DNS (proxied), SSL Full Strict, Bot Fight Mode, rate limiting rules. Developer configures manually.

---

### Billing Testing

- [ ] T219 [P] Backend billing service unit tests: `backend/tests/unit/test_billing_service.py` — checkout session creation, subscription status queries, cancel flow, webhook signature verification, each event handler, idempotency (duplicate events).

- [ ] T220 [P] Backend billing endpoint integration tests: `backend/tests/integration/test_billing.py` — checkout (auth/unauth), subscription status, cancel, webhook (valid/invalid sig), subscription-gated endpoints (active=200, none=403, unauth=401), account deletion cascade.

- [ ] T221 [P] Frontend billing flow tests: `frontend/tests/billing.test.tsx` — dashboard renders subscribe/generate based on status, checkout redirect, success/cancel pages, subscription gate behavior, cancel flow.

- [ ] T222 [P] Security tests: `backend/tests/integration/test_security.py` — rate limiting (101 requests → 429), CORS (allowed/disallowed origin), CSRF (missing/valid token), security headers present, webhook exempt from CSRF/user rate limit.

- [ ] T223 End-to-end billing smoke test: `backend/tests/integration/test_billing_e2e.py` — full flow: register → login → no sub (403) → checkout → webhook → active (200) → cancel → webhook → expired (403). Delete account → Stripe customer deleted.

**Layer 3 Checkpoint**: Full production-ready platform. Unauthenticated → login. Unsubscribed → info dashboard. Subscribed → generate + PDF. Rate limiting, CORS, CSRF, security headers, Cloudflare documented. 24 tasks complete.

---
---

## Dependencies & Execution Order

### Layer 1 (40 tasks)
```
Phase 1: T001 → T002 ∥ T003
Phase 2: T004 → T005 → T006 → T007 (sequential)
Phase 3: T008 ∥ T009 ∥ T010 ∥ T011 ∥ T012 (all parallel)
Phase 4: T013 ∥ T014 ∥ T015 ∥ T016 ∥ T017 ∥ T018 (all parallel)
Phase 5: T019 → T020 → T021 ∥ T022
Phase 6: T023 → T024 (or parallel)
Phase 7: T025 ∥ T026 ∥ T027, then T028 ∥ T029, then T030 → T031 → T032
Phase 8: T033 ∥ T034 ∥ T035, T036 ∥ T037
Phase 9: T038 ∥ T039, then T040
```

### Layer 2 (21 tasks)
```
Setup:    T100 + T101 + T102 (all first)
Backend:  T107 → T103 → T104 → T105 → T106 (sequential)
Frontend: T108 ∥ T109 ∥ T116, then T110 ∥ T111 ∥ T112 ∥ T113, then T114 → T115
Testing:  T117 ∥ T118 ∥ T119, then T120
```

### Layer 3 (24 tasks)
```
Setup:    T200 + T201 + T202 (all first)
Backend:  T203 → T205 → T204 → T206 → T207, T208 (after T204)
Frontend: T209 ∥ T210, then T211 ∥ T212 → T213
Security: T214 → T215 → T216 → T217, T218 (parallel with all)
Testing:  T219 ∥ T220 ∥ T221 ∥ T222, then T223
```

### Critical Path
```
T001 → T002 → T004 → T005 → T006 → T007 → T008-T018 (parallel) →
T019 → T020 → T021 → T023 → T036 → T040 →
T100 → T103 → T106 → T120 →
T200 → T204 → T207 → T223
```

---

## Summary

| Layer | Phase | Tasks | Range |
|---|---|---|---|
| 1 | Setup | 3 | T001–T003 |
| 1 | Engine Foundation | 4 | T004–T007 |
| 1 | Algebra Topics | 5 | T008–T012 |
| 1 | Functions/Trig/Calc Topics | 6 | T013–T018 |
| 1 | Backend API | 4 | T019–T022 |
| 1 | PDF Generation | 2 | T023–T024 |
| 1 | Frontend | 8 | T025–T032 |
| 1 | Testing | 5 | T033–T037 |
| 1 | CI/CD | 3 | T038–T040 |
| 2 | Supabase Setup | 3 | T100–T102 |
| 2 | Backend Auth | 5 | T103–T107 |
| 2 | Frontend Auth | 9 | T108–T116 |
| 2 | Auth Testing | 4 | T117–T120 |
| 3 | Stripe Setup | 3 | T200–T202 |
| 3 | Backend Billing | 6 | T203–T208 |
| 3 | Frontend Billing | 5 | T209–T213 |
| 3 | Security Hardening | 5 | T214–T218 |
| 3 | Billing Testing | 5 | T219–T223 |
| **Total** | | **85 tasks** | |
