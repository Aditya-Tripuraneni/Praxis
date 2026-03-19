# Layer 3: Billing (Stripe) — Implementation Plan

**Date**: 2026-03-13
**Status**: Planned — Pending User Approval
**Prerequisite**: Layer 2 fully complete (auth, OTP verification, security fixes, trig expansion, dedup generator)
**Spec Reference**: `specs/001-core-platform/spec.md` (US4, FR-003, FR-004, FR-022, FR-027, FR-028)
**Task Range**: T200-T223 (24 tasks)

---

## 1. Overview

Add Stripe billing to ProblemGenerator so test generation and PDF download require an active $5/month subscription. This is the final layer — wraps around the already-working product + auth.

**What changes:**
- Backend gets billing service, webhook handlers, subscription-gated middleware
- Frontend gets subscription context, checkout flow, gated dashboard
- Security hardening: CSRF research, CORS production config, Cloudflare docs

**What doesn't change:**
- Math engine — untouched
- Auth flow — untouched (except account deletion cascade adds Stripe cleanup)
- PDF service — untouched

---

## 2. Layer 2 Completion Status

All Layer 2 tasks (T100-T120) are COMPLETE, plus additional work:

| Item | Status |
|---|---|
| Supabase Auth (email/password) | Done |
| OTP email verification (replaced magic links) | Done |
| JWT verification on all protected endpoints | Done |
| Rate limiting on auth + test/PDF endpoints | Done |
| HIBP breached password check | Done |
| Frontend auth (Login, Register, Dashboard, VerifyEmail) | Done |
| Google OAuth | UI disabled (backend wired, needs Google consent screen) |
| Security audit — all critical + high + medium fixes | Done |
| Trig engine expansion (150+ identity variants) | Done |
| Zero-duplicate generator | Done |
| Structured security event logging | Done |
| CSP + HSTS + Permissions-Policy headers | Done |
| IDOR ownership check on tests | Done |
| **Total tests: 405** (277 backend + 128 frontend) | All passing |

### Layer 3 Tasks Already Partially Complete

| Task | Status | What remains |
|---|---|---|
| T214 (rate limiting) | 80% done | Add global 100/min per-user limit, exempt webhook |
| T215 (CORS) | 80% done | Make `allow_origins` from `FRONTEND_URL` env for production |
| T217 (security headers) | 90% done | Update CSP to allow `js.stripe.com` |

---

## 3. Architecture Decisions

### 3.1 Stripe Checkout (Hosted)

Use Stripe's hosted checkout page (not embedded). The user is redirected to Stripe's domain for payment, then back to our app. This:
- Handles PCI compliance (card data never touches our server)
- Handles 3D Secure, Apple Pay, Google Pay automatically
- Reduces frontend complexity

### 3.2 Subscription Table in Supabase

Store subscription state in a `subscriptions` table in the same Supabase PostgreSQL database. Schema:

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id TEXT NOT NULL,
    stripe_subscription_id TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'inactive',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own subscription" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);
```

RLS ensures users can only read their own subscription. Backend uses service_role key to write (via webhook handlers).

### 3.3 Webhook-Driven State Machine

Subscription status is updated ONLY via Stripe webhooks — not by polling or client-side checks. This ensures:
- Single source of truth (Stripe)
- Idempotent processing (FR-028)
- Handles all edge cases (payment retry, card update, cancellation grace period)

**Events handled:**
| Event | Action |
|---|---|
| `checkout.session.completed` | Create subscription record, set status='active' |
| `invoice.payment_succeeded` | Update status='active', update period dates |
| `invoice.payment_failed` | Update status='past_due' |
| `customer.subscription.updated` | Update status + period dates |
| `customer.subscription.deleted` | Update status='expired' |

### 3.4 Subscription Gate (Middleware)

`require_active_subscription` FastAPI dependency, stacked on top of `get_current_user`:

```
Request → get_current_user (verify JWT) → require_active_subscription (check DB) → endpoint
```

Returns 403 "Active subscription required" if no active subscription. Applied to:
- `POST /api/tests/generate`
- `GET /api/tests/{id}`
- `GET /api/tests/{id}/pdf`

NOT applied to:
- `GET /api/tests/topics` (public)
- `GET /api/health` (public)
- `POST /api/billing/*` (checkout, status, cancel — need auth but not subscription)
- `POST /api/billing/webhook` (no auth, no subscription — Stripe signature verification only)

### 3.5 CSRF — Not Needed

Our auth uses `Authorization: Bearer` headers, not cookies. CSRF attacks exploit automatic cookie inclusion. Since our tokens are in localStorage and manually attached via headers, CSRF is not applicable. T216 will be documented as "not needed" with rationale, not implemented.

---

## 4. Phase Breakdown

### Phase 1: Stripe Setup (T200-T202)

**USER ACTIONS REQUIRED:**

1. Create Stripe account at https://dashboard.stripe.com
2. Get test mode API keys:
   - **Publishable key** (`pk_test_...`) — safe for frontend
   - **Secret key** (`sk_test_...`) — backend only
3. Create a Product:
   - Name: "ProblemGenerator Subscription"
   - Price: $5.00/month, recurring, USD
   - Copy the `price_id` (`price_...`)
4. Set up webhook endpoint:
   - URL: `http://localhost:8000/api/billing/webhook` (for local dev, use Stripe CLI forwarding)
   - Events: `checkout.session.completed`, `invoice.payment_succeeded`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copy the webhook signing secret (`whsec_...`)
5. Install Stripe CLI for local webhook forwarding:
   - `stripe listen --forward-to localhost:8000/api/billing/webhook`

**Step-by-step instructions will be provided via context7 for latest Stripe docs.**

**Code changes (me):**
- Update `backend/.env.example` and `frontend/.env.example` with Stripe vars
- Update `backend/app/config.py` with Stripe settings
- Install `stripe` backend dependency
- Install `@stripe/stripe-js` and `@stripe/react-stripe-js` frontend dependencies
- Update `docker-compose.yml` with Stripe env vars

**Environment variables:**
```env
# Backend
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Frontend
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Phase 2: Backend Billing (T203-T208)

**T203 — Subscriptions table:**
- USER creates via Supabase Dashboard (SQL editor)
- I provide exact SQL (see Section 3.2)

**T204 — Billing service** (`backend/app/services/billing.py`):
- `BillingService` class with methods:
  - `create_checkout_session(user_id, email)` → creates Stripe Customer (if needed) + Checkout Session → returns session URL
  - `get_subscription_status(user_id)` → queries Supabase `subscriptions` table → returns SubscriptionStatus
  - `cancel_subscription(user_id)` → calls Stripe `subscription.modify(cancel_at_period_end=True)` → updates DB
  - `handle_webhook(payload, signature)` → verifies Stripe signature → dispatches to event handlers
  - Event handlers: `_handle_checkout_completed`, `_handle_payment_succeeded`, `_handle_payment_failed`, `_handle_subscription_updated`, `_handle_subscription_deleted`
- All handlers are idempotent (check current state before updating)
- Uses Supabase service_role client for DB writes

**T205 — Billing models** (`backend/app/models/billing.py`):
- `CheckoutSessionResponse(url: str)`
- `SubscriptionStatus(status: str, is_active: bool, current_period_end: datetime | None, stripe_subscription_id: str | None)`
- `CancelSubscriptionResponse(message: str, cancel_at_period_end: bool)`

**T206 — Billing endpoints** (`backend/app/api/billing.py`):
- `POST /api/billing/create-checkout-session` — protected (auth required)
- `GET /api/billing/subscription-status` — protected
- `POST /api/billing/cancel-subscription` — protected
- `POST /api/billing/webhook` — unprotected (Stripe signature verification, always return 200)

**T207 — Subscription middleware:**
- Add `require_active_subscription` to `dependencies.py`
- Stack on `/api/tests/generate`, `/api/tests/{id}`, `/api/tests/{id}/pdf`
- Register billing router in `main.py`

**T208 — Account deletion cascade:**
- Modify `auth.py` `delete_user()`:
  1. Get subscription from DB
  2. If active → cancel Stripe subscription immediately
  3. Delete Stripe customer
  4. DB row cleaned by `ON DELETE CASCADE`
  5. Delete Supabase Auth user

### Phase 3: Frontend Billing (T209-T213)

**T209 — Stripe client** (`frontend/src/services/stripe.ts`):
```typescript
import { loadStripe } from "@stripe/stripe-js";
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);
export { stripePromise };
```

**T210 — Subscription context** (`frontend/src/context/SubscriptionContext.tsx`):
- State: `isSubscribed`, `subscription`, `isLoading`
- Fetches `GET /api/billing/subscription-status` on mount and auth change
- Provides `subscribe()` (calls create-checkout-session, redirects to Stripe)
- Provides `cancelSubscription()` (calls cancel endpoint)

**T211 — Dashboard update:**
- If subscribed: generate button + status badge + cancel option
- If not subscribed: explanation + "$5/month Subscribe" button

**T212 — Checkout pages:**
- `/checkout/success` — polls subscription status, shows "Subscribed!" when active
- `/checkout/cancel` — "Checkout cancelled" + retry button

**T213 — Subscription gate:**
- `SubscriptionGate` component wrapping Generate/Preview routes
- Checks `isSubscribed`, redirects to `/dashboard` if not

### Phase 4: Security Hardening (T214-T218)

| Task | Action |
|---|---|
| T214 | Add global per-user rate limit (100/min), exempt webhook |
| T215 | `FRONTEND_URL` env var for CORS origins in production |
| T216 | Document that CSRF is not needed (Bearer token auth) — no code change |
| T217 | Update CSP to allow `js.stripe.com` and `checkout.stripe.com` |
| T218 | Write `docs/cloudflare-setup.md` with free-tier DDoS protection guide |

### Phase 5: Testing (T219-T223)

**T219 — Billing service unit tests:**
- Mock Stripe API calls
- Test checkout session creation, subscription queries, cancel flow
- Test webhook signature verification (valid/invalid)
- Test each event handler (idempotent — send same event twice)

**T220 — Billing endpoint integration tests:**
- Checkout (authenticated/unauthenticated)
- Subscription status (active/none/expired)
- Cancel subscription
- Webhook (valid sig/invalid sig)
- Subscription-gated endpoints (active=200, none=403, unauth=401)

**T221 — Frontend billing tests:**
- Dashboard renders subscribe/generate based on status
- Checkout redirect
- Success/cancel pages
- Subscription gate behavior

**T222 — Security tests:**
- Rate limiting (101 requests → 429)
- CORS (allowed/disallowed origins)
- Security headers present on responses

**T223 — E2E smoke test:**
- Full flow: register → login → no sub (403) → checkout → webhook → active (200) → cancel → webhook → expired (403) → delete account

---

## 5. Agent Architecture

```
Manager (me)
│
├── Phase 1: Setup (sequential — needs user's API keys)
│   └── 1 agent: env config + deps + setup docs (after user provides keys)
│
├── Phase 2: Backend Billing (sequential)
│   ├── Agent A: Models + Service (T205 → T204)
│   └── Agent B: Endpoints + Middleware + Cascade (T206 → T207 → T208)
│
├── Phase 3: Frontend Billing (sequential)
│   ├── Agent C: Stripe client + Subscription context (T209 → T210)
│   └── Agent D: Pages + routing + gate (T211 → T212 → T213)
│
├── Phase 4: Security (1 agent)
│   └── Agent E: Rate limit finalize + CORS + CSP + CSRF doc + Cloudflare doc
│
└── Phase 5: Testing (3 parallel agents)
    ├── Agent F: Backend billing tests (T219 + T220)
    ├── Agent G: Frontend billing tests (T221)
    └── Agent H: Security tests + E2E (T222 + T223)
```

**Parallelism:** Phases 2, 3, 4 can run in parallel after Phase 1. Phase 5 runs after all others.

---

## 6. Research Needed

| Topic | Method | When |
|---|---|---|
| Stripe Checkout Session API (Python) | context7 | Before Phase 2 |
| Stripe webhook signature verification | context7 | Before Phase 2 |
| Stripe CLI local forwarding setup | context7 | Phase 1 (for user instructions) |
| Stripe test mode clock (for subscription lifecycle testing) | context7 | Before Phase 5 |
| CSRF with Bearer tokens (confirmation) | Web search | Phase 4 |
| Supabase table creation via dashboard | context7 | Phase 1 (for user instructions) |

---

## 7. User Actions Summary

Things only the user can do (API key policy):

| When | What to do | I provide |
|---|---|---|
| Phase 1 start | Create Stripe account, get test API keys | Step-by-step instructions via context7 |
| Phase 1 | Create product + $5/month price | Exact dashboard steps |
| Phase 1 | Set up webhook endpoint in Stripe dashboard | URL + event list |
| Phase 1 | Install Stripe CLI | Platform-specific install command |
| Phase 1 | Paste keys into `.env` files | Which keys go where |
| Phase 2 | Create `subscriptions` table in Supabase | Exact SQL to run |

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Stripe webhook delivery delay | User pays but can't access immediately | Success page polls status; webhooks have 3-day retry |
| Stripe test mode limitations | Can't test real card charges | Use Stripe test card numbers (4242...) |
| Supabase free tier connection limits | High concurrent webhook processing | Single connection, sequential processing |
| Render.com cold start after webhook | Webhook times out on first request | Stripe retries; webhook always returns 200 immediately |
| CSRF concern without middleware | Documented as non-issue for Bearer auth | Write explicit rationale document |

---

## 9. Definition of Done

Layer 3 is complete when:
- [ ] Unauthenticated users → redirected to login
- [ ] Authenticated but unsubscribed → see info dashboard + subscribe button
- [ ] Subscribe button → Stripe checkout → payment → active subscription
- [ ] Subscribed users → full access to generate + preview + PDF
- [ ] Cancel subscription → access continues until period end → then blocked
- [ ] Account deletion → cancels Stripe subscription + deletes Stripe customer
- [ ] Webhooks handle all 5 events idempotently
- [ ] Rate limiting at 100/min per user (global)
- [ ] CORS configured for production domain
- [ ] CSP allows Stripe JS
- [ ] Cloudflare setup documented
- [ ] All tests pass (backend + frontend)
- [ ] Manual smoke test with Stripe test cards passes
