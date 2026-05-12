# Praxis
Praxis generates math practice tests for students and tutors who need consistent material and tracked progress.

## The Problem
Writing practice sets by hand is slow and uneven. Difficulty drifts, topic coverage shifts, and the same effort has to be repeated every week. Without a shared system, students cannot see how practice connects to progress.

## What Praxis Does
Praxis generates tests from topic and difficulty inputs, producing a repeatable mix that can be recreated from the same configuration and seed.

Each test can be exported as a PDF built from LaTeX, with optional answers and solutions for review or classroom use.

Tutor accounts can save tests and replay them later, keeping assignments consistent across sessions and reducing prep time.

User stats record lifetime test counts, per topic distribution, practice streaks, and recent timer data so progress is visible over time.

Stripe checkout and webhooks keep subscription status aligned with access rules in the API.

## Who It's For
Students get structured practice that stays consistent from one session to the next. They can generate new tests, review answers, and track progress without stitching together separate tools. The result is more time practicing and less time preparing.

Tutors get repeatable materials and a way to reuse proven test sets. They can save configurations, replay them for groups, and monitor how practice volume and topics shift over time. The outcome is less prep and more consistency across learners.

## Subscription Model
Praxis offers a student tier for on-demand test generation and PDF exports, and a tutor tier that unlocks saved tests and replay. Billing and plan changes run through Stripe, and the backend enforces the active tier on gated routes.

## Engineering
The product is direct to use, and the code keeps the same clarity in how responsibilities are separated.

### System Architecture Diagram
```mermaid
graph LR
  subgraph Client
    Browser[User Browser]
    Frontend[React + TypeScript frontend<br/>Vite, KaTeX]
  end
  subgraph "Backend Services"
    API[FastAPI backend<br/>Rate limiting, typed endpoints]
    PDF[PDF pipeline<br/>Tectonic compiler, thread pool]
  end
  subgraph "External Services"
    Supabase[Supabase<br/>Auth, Postgres with RLS, saved tests]
    Stripe[Stripe<br/>Checkout session, webhook handler]
  end
  subgraph Infrastructure
    Nginx[Nginx<br/>Static assets, CSP headers]
    Docker[Docker<br/>Multi-stage builds, backend runs non-root]
  end

  Browser --> Nginx --> Frontend
  Frontend --> API
  API --> Supabase
  API --> Stripe
  API --> PDF
  Docker --> API
  Docker --> Frontend
  Docker --> Nginx
```

### Data Model / Entity Relationships
```mermaid
erDiagram
  "auth.users" {
    uuid id
    text email
    timestamptz created_at
  }
  subscriptions {
    uuid user_id
    text stripe_customer_id
    text stripe_subscription_id
    text plan
    text status
    timestamptz current_period_start
    timestamptz current_period_end
    timestamptz created_at
    timestamptz updated_at
  }
  user_stats {
    uuid user_id
    int tests_generated
    int questions_generated
    jsonb topic_counts
    int streak_current
    int streak_best
    date last_practice_date
    int last_test_duration
    timestamptz created_at
    timestamptz updated_at
  }
  saved_tests {
    uuid id
    uuid user_id
    text test_name
    jsonb config
    int seed
    jsonb questions
    timestamptz created_at
  }

  "auth.users" ||--o| subscriptions : has
  "auth.users" ||--|| user_stats : tracks
  "auth.users" ||--o{ saved_tests : owns
```

### Request Flow Diagram
```mermaid
sequenceDiagram
  actor User
  participant Frontend
  participant FastAPI
  participant SupabaseAuth
  participant SupabaseDB
  participant TestGen
  participant Stripe
  participant PDF

  Note over Stripe,FastAPI: Stripe webhooks update subscription status out of band

  User->>Frontend: Choose topics and difficulty
  Frontend->>SupabaseAuth: Sign in and get access token
  SupabaseAuth-->>Frontend: JWT access token
  Frontend->>FastAPI: POST /api/tests/generate with config and token
  FastAPI->>SupabaseAuth: Validate token
  SupabaseAuth-->>FastAPI: User identity
  FastAPI->>SupabaseDB: Read subscription status
  SupabaseDB-->>FastAPI: Subscription row
  FastAPI->>TestGen: Generate questions with seed
  TestGen-->>FastAPI: Test payload
  FastAPI-->>Frontend: Test response
  Frontend->>FastAPI: GET /api/tests/{id}/pdf
  FastAPI->>SupabaseDB: Read subscription status
  SupabaseDB-->>FastAPI: Subscription row
  FastAPI->>PDF: Compile LaTeX in thread pool
  PDF-->>FastAPI: PDF bytes
  FastAPI-->>Frontend: PDF response
```

### Deployment Topology
Production serves the frontend as a static site on Vercel or Render, with the backend deployed as a Docker web service on Render. The frontend Docker image uses Nginx for CSP headers when the containerized frontend is used.
```mermaid
graph LR
  subgraph Production
    User[User] --> Vercel[Vercel CDN<br/>Frontend static build]
    Vercel --> Browser[Browser SPA]
    Browser --> Render[Render<br/>FastAPI container]
    Render --> Supabase[Supabase<br/>Auth and Postgres]
    Render --> Stripe[Stripe<br/>Billing]
  end
  subgraph Development
    Dev[Developer] --> Compose[Docker Compose]
    Compose --> DevFrontend[Frontend dev server]
    Compose --> DevAPI[FastAPI dev server]
    DevAPI --> DevSupabase[Supabase dev project]
    DevAPI --> DevStripe[Stripe test mode]
  end
```

### Tech Stack Table
| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite | Renders the SPA, handles routing, and builds static assets. |
| Math rendering | KaTeX | Displays math notation in the browser. |
| Backend API | FastAPI | Serves typed endpoints for generation, billing, and stats. |
| Auth | Supabase Auth | Manages signup, login, and JWT validation. |
| Database | Supabase Postgres with RLS | Stores subscriptions, saved tests, and user stats with row level rules. |
| Billing | Stripe | Creates checkout sessions and handles webhook events. |
| PDF rendering | Tectonic | Compiles LaTeX into PDF responses in a worker thread pool. |
| Web server | Nginx | Serves the containerized frontend and applies CSP headers. |
| Containers | Docker | Builds multi-stage images for dev and production. |
| Local dev | Docker Compose | Runs the frontend and backend together for local work. |
| CI | GitHub Actions | Runs lint, tests, type checks, and frontend builds. |
| Hosting | Vercel, Render | Hosts the frontend build and the FastAPI service. |

### Local Development
Prerequisites: Docker and a `.env` file in the repo root.

Required environment variables:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_STUDENT_PRICE_ID`
- `STRIPE_TUTOR_PRICE_ID`

`SUPABASE_SERVICE_ROLE_KEY` is backend-only. Keep it out of the frontend and never commit it.

Run the stack:
```bash
docker compose up --build
```

Frontend: http://localhost:5173  
Backend health: http://localhost:8000/api/health

### Testing and CI
Local quality gates run through the Makefile. `make lint` runs Ruff and formatting checks for the backend plus a TypeScript type check for the frontend. `make test-backend` runs pytest, and `make test-frontend` runs Vitest.

CI runs Ruff, pytest with an 80% coverage threshold, ESLint, TypeScript type checks, Vitest, and a frontend production build, but no frontend coverage threshold is enforced because Vitest coverage reporting is not wired into CI.

```bash
make lint
make test-backend
make test-frontend
```

### Repository Structure
```
.
├── backend/        FastAPI service
├── frontend/       React SPA
├── docs/           Deployment guide
├── mockups/        UI mockups
├── specs/          Product specs
├── .github/        CI workflows
├── docker-compose.yml  Local stack
├── Makefile        Dev commands
```
