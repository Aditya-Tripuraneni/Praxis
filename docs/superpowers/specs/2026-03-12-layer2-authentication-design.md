# Layer 2: Authentication — Design Specification

**Date**: 2026-03-12
**Status**: Draft — Pending User Approval
**Prerequisite**: Layer 1 complete (except T037 frontend tests, addressed in Phase 0)
**Spec Reference**: `specs/001-core-platform/spec.md` (US3, FR-001, FR-002, FR-019–FR-024)
**Task Range**: T037 (from Layer 1) + T100–T120

---

## 1. Overview

Add authentication to ProblemGenerator so users must register and log in before generating tests or downloading PDFs. This layer wraps around the already-working Layer 1 (generation + preview + PDF) without modifying the math engine or PDF service.

**What changes:**
- Backend gets auth endpoints, JWT verification middleware, and password security checks
- Frontend gets login/register pages, auth context, protected routes, and token management
- All `/api/tests/*` and `/api/tests/*/pdf` endpoints become protected

**What doesn't change:**
- Math engine (`backend/app/engine/`) — untouched
- PDF service — untouched
- Test generation service — untouched (tests remain anonymous/ephemeral)
- Landing page — remains public

---

## 2. Architecture Decisions

### 2.1 Backend as Auth Proxy (Decision Q2 — Option A)

All auth operations flow through the backend's `/api/auth/*` endpoints. The frontend never talks to Supabase Auth directly (with one exception — see 2.2).

**Rationale:**
- Single source of truth for auth logic (password policy, breached check, error normalization)
- Supabase service role key stays server-side
- Easier to swap auth providers later — frontend only knows your API
- Clean middleware stacking for Layer 3 billing (`get_current_user` → `require_active_subscription`)

**Flow (email/password):**
```
Frontend → POST /api/auth/signup → Backend → Supabase Auth → DB
Frontend → POST /api/auth/login  → Backend → Supabase Auth → tokens returned
Frontend → GET  /api/tests/*     → Backend (verify JWT) → Engine → Response
```

### 2.2 Google OAuth via Supabase JS (Decision Q3 — Option B)

The OAuth redirect flow runs through Supabase JS on the frontend. This is the sole exception to the "backend as proxy" rule.

**Rationale:**
- Supabase JS handles OAuth popups/redirects natively and reliably
- The redirect dance (frontend → Google consent → redirect back) is browser-side by nature
- Security is not compromised: the resulting JWT is still verified by the backend on every subsequent API call

**Flow (Google OAuth):**
```
Frontend → Supabase JS signInWithOAuth() → Google consent screen →
  redirect to frontend callback → Supabase issues JWT →
  Frontend stores tokens → sends JWT to backend on API calls →
  Backend verifies JWT
```

### 2.3 Token Storage — localStorage (Decision Q7 — Option A)

Access and refresh tokens are stored in `localStorage`.

**Rationale:**
- Persists across page refreshes, tab closes, and new tabs
- 15-minute access token + 7-day refresh token make session management smooth
- httpOnly cookies (Option B) would cause cross-origin issues between Vercel and Render
- In-memory (Option C) would log users out on every page refresh — unacceptable UX
- XSS risk is low: app has no user-generated content, and tokens are short-lived

**Token lifecycle:**
1. Login → backend returns `{ access_token, refresh_token, expires_in, user }`
2. Frontend stores both in `localStorage`
3. Every API call → attach `Authorization: Bearer <access_token>` header
4. Access token expires (15 min) → frontend calls `POST /api/auth/refresh` with refresh token
5. Refresh token expires (7 days) → user must log in again
6. Logout → clear localStorage, call `POST /api/auth/logout`

### 2.4 Tests Remain Anonymous (Decision Q5 — Option A)

Auth protects endpoints but generated tests are not associated with user IDs. The in-memory cache remains keyed by `test_id` only.

**Rationale:**
- Tests are ephemeral (30-min TTL, max 100 in cache)
- No persistent user data to clean up on account deletion in Layer 2
- Account deletion = remove Supabase Auth record only
- Associating tests with users adds complexity for zero benefit at this stage

### 2.5 Login Error Messages — Vague (Decision Q8 — Option A)

All login failures return a generic `"Invalid email or password"` message regardless of whether the email exists or the password is wrong.

**Rationale:**
- Prevents user enumeration attacks (attacker can't probe which emails have accounts)
- Industry standard (OWASP Authentication Cheat Sheet)
- Exception: "Please verify your email" is NOT returned — it would confirm the email exists. Instead, signup flow tells users to check their email, and unverified users get the same generic error on login.

---

## 3. Password Security

### 3.1 NIST SP 800-63B Compliance

Password requirements follow NIST guidelines:
- **Minimum 8 characters** — enforced by backend before calling Supabase
- **Maximum 128 characters** — prevents DoS via extremely long password hashing. NIST recommends accepting at least 64; 128 provides ample room.
- **No forced complexity** — no uppercase/symbol/number rules
- **All printable characters allowed** — including spaces, unicode
- **Breached password check** — via HaveIBeenPwned API (see 3.2)
- **No password hints or security questions**

### 3.2 HaveIBeenPwned Integration (Decision Q4)

On signup, the backend checks the password against the HIBP Pwned Passwords API using k-anonymity:

1. SHA-1 hash the password
2. Send first 5 hex characters to `https://api.pwnedpasswords.com/range/{prefix}`
3. Check if the full hash suffix appears in the response
4. If found → reject signup with "This password has been found in a data breach. Please choose a different password."

**Lenient failure mode:** If the HIBP API is unreachable (timeout, 5xx, DNS failure):
- Allow the signup to proceed
- Log a warning: `"HIBP API unreachable — breached password check skipped for signup {email_hash}"`
- Do NOT block users due to a third-party outage

**Check timing:** Signup only. Not checked on login (existing users are not retroactively warned).

**Implementation:**
- HTTP client: `httpx` (async, already a dev dependency)
- Timeout: 3 seconds
- No API key required (HIBP Pwned Passwords API is free and unauthenticated)

---

## 4. Email Verification (Decision Q6 — Option A)

Supabase Auth handles email verification natively. The flow:

1. User signs up via `POST /api/auth/signup`
2. Backend calls Supabase `auth.sign_up()` which triggers a verification email
3. User clicks the link in the email
4. Supabase verifies the email and redirects to a configured URL
5. Redirect target: `{FRONTEND_URL}/auth/verify-success`
6. Frontend shows a "Email verified! You can now log in." page with a link to `/login`

**Configuration required (user sets manually in Supabase Dashboard):**
- Site URL: `{FRONTEND_URL}`
- Redirect URLs: `{FRONTEND_URL}/auth/verify-success`, `{FRONTEND_URL}/auth/callback` (both needed — email verification and Google OAuth respectively)
- Email template: default Supabase template (customizable later)

**Unverified users:**
- Cannot log in — backend checks `email_confirmed_at` in the Supabase user object
- Login attempt by unverified user returns generic "Invalid email or password" (see 2.5)

---

## 5. Auth Rate Limiting (Decision Q9)

Rate limits applied at the FastAPI layer using `slowapi`, providing defense-in-depth on top of Supabase's built-in rate limits.

| Endpoint | Limit | Scope | Response |
|---|---|---|---|
| `POST /api/auth/login` | 10/minute | Per IP | 429 + `Retry-After` header |
| `POST /api/auth/signup` | 5/hour | Per IP | 429 + `Retry-After` header |
| `POST /api/auth/refresh` | 30/5-minutes | Per IP | 429 + `Retry-After` header |
| `POST /api/auth/logout` | 10/minute | Per IP | 429 + `Retry-After` header |
| `GET /api/auth/me` | 30/minute | Per IP | 429 + `Retry-After` header |
| `POST /api/auth/resend-verification` | 3/hour | Per IP | 429 + `Retry-After` header |
| `DELETE /api/auth/account` | 3/hour | Per IP | 429 + `Retry-After` header |

**Per-account lockout:** Deferred to Supabase's built-in protection. Supabase throttles per-user after repeated failures. Adding per-account tracking at the FastAPI layer would require database state (failure count per email) — unnecessary complexity given Supabase already handles it.

**Rationale for limits:**
- Login (10/min): OWASP recommends 5-20/min. 10 allows normal usage but blocks brute force.
- Signup (5/hour): Email sends are the bottleneck. Supabase limits to 2/hour on default SMTP anyway.
- Refresh (30/5-min): Normal usage is 1 refresh per 15 minutes. 30 accommodates multiple tabs/devices.

---

## 6. API Endpoints

### 6.1 New Auth Endpoints

All auth endpoints are under `/api/auth/`.

#### `POST /api/auth/signup`
Create a new account with email and password.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "mysecurepassword"
}
```

**Validation (backend, before calling Supabase):**
- Email: valid format (Pydantic `EmailStr`)
- Password: minimum 8 characters
- Password: not in HIBP breached list (lenient failure mode)

**Success (201):**
```json
{
  "message": "Account created. Please check your email to verify your account."
}
```

**Errors:**
- 400: `"Password must be at least 8 characters"`
- 400: `"This password has been found in a data breach. Please choose a different password."`
- 400: `"Invalid email format"`
- 400: `"Password must not exceed 128 characters"`
- 429: Rate limited

**Anti-enumeration on duplicate email:** If a signup is attempted with an email that already exists, the endpoint returns the same 201 success response (`"Account created. Please check your email to verify your account."`). The existing user receives no new email. This prevents attackers from probing which emails have accounts via the signup endpoint.

#### `POST /api/auth/login`
Log in with email and password.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "mysecurepassword"
}
```

**Success (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "abc123...",
  "expires_in": 900,
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "email_verified": true
  }
}
```

**Errors:**
- 401: `"Invalid email or password"` (covers wrong email, wrong password, and unverified email)
- 429: Rate limited

#### `POST /api/auth/refresh`
Exchange a refresh token for a new access token.

**Request:**
```json
{
  "refresh_token": "abc123..."
}
```

**Success (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "newdef456...",
  "expires_in": 900,
  "token_type": "bearer"
}
```

**Errors:**
- 401: `"Invalid or expired refresh token"`
- 429: Rate limited

#### `POST /api/auth/logout`
Invalidate the current session.

**Request:** No body. Requires `Authorization: Bearer <access_token>` header.

**Success (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Errors:**
- 401: `"Not authenticated"`

#### `GET /api/auth/me`
Get the current authenticated user's profile.

**Request:** No body. Requires `Authorization: Bearer <access_token>` header.

**Success (200):**
```json
{
  "id": "uuid",
  "email": "student@example.com",
  "email_verified": true,
  "created_at": "2026-03-12T10:00:00Z"
}
```

**Errors:**
- 401: `"Not authenticated"`

#### `POST /api/auth/resend-verification`
Resend the email verification link. Shown on the Register success screen if the user didn't receive the email.

**Request:**
```json
{
  "email": "student@example.com"
}
```

**Success (200):**
```json
{
  "message": "If an account exists with this email, a verification link has been sent."
}
```

**Anti-enumeration:** Always returns the same message regardless of whether the email exists. Rate limited to 3/hour per IP.

**Errors:**
- 429: Rate limited

#### `DELETE /api/auth/account`
Delete the user's account and all associated data.

**Request:** No body. Requires `Authorization: Bearer <access_token>` header.

**Behavior:**
1. Delete user from Supabase Auth (using service role key)
2. In Layer 2, no other data exists to clean up (tests are anonymous)
3. In Layer 3, this will also cancel Stripe subscription and delete Stripe customer

**Success (200):**
```json
{
  "message": "Account deleted successfully"
}
```

**Errors:**
- 401: `"Not authenticated"`

### 6.2 Modified Existing Endpoints

These endpoints gain auth protection via a `get_current_user` FastAPI dependency:

| Endpoint | Before (Layer 1) | After (Layer 2) |
|---|---|---|
| `POST /api/tests/generate` | Public | Protected (401 if no valid JWT) |
| `GET /api/tests/{test_id}` | Public | Protected |
| `GET /api/tests/{test_id}/pdf` | Public | Protected |
| `GET /api/tests/topics` | Public | **Stays public** (needed for landing page / unauthenticated browsing) |
| `GET /api/health` | Public | **Stays public** |

---

## 7. Backend Components

### 7.1 New Files

```
backend/
├── app/
│   ├── models/
│   │   └── auth.py              # Pydantic models for auth requests/responses
│   ├── api/
│   │   ├── auth.py              # Auth endpoint handlers
│   │   └── dependencies.py      # get_current_user dependency
│   └── services/
│       └── auth.py              # Supabase Auth integration + HIBP check
```

### 7.2 `backend/app/models/auth.py`

Pydantic models:
- `SignupRequest` — email (EmailStr), password (str, min_length=8, max_length=128)
- `LoginRequest` — email (EmailStr), password (str)
- `RefreshRequest` — refresh_token (str)
- `AuthResponse` — access_token, refresh_token, expires_in, token_type, user
- `UserProfile` — id, email, email_verified, created_at
- `AuthMessage` — message (str)
- `AuthError` — detail (str)

### 7.3 `backend/app/services/auth.py`

Auth service class encapsulating all Supabase Auth operations:

- `signup(email, password)` → validate password length → HIBP check → Supabase `auth.sign_up()` → return message
- `login(email, password)` → Supabase `auth.sign_in_with_password()` → return tokens + user
- `refresh(refresh_token)` → Supabase `auth.refresh_session()` → return new tokens
- `logout(access_token)` → Supabase `auth.sign_out()`
- `get_user(access_token)` → Supabase `auth.get_user()` → return user profile
- `delete_user(user_id)` → Supabase `auth.admin.delete_user()` (service role key)
- `resend_verification(email)` → Supabase `auth.resend()` with type `signup` → triggers new verification email
- `check_password_breached(password)` → SHA-1 hash → HIBP k-anonymity API → bool

**Error handling:** All Supabase errors are caught and normalized into application-specific exceptions (`AuthenticationError`, `UserExistsError`, `InvalidTokenError`). The service never leaks Supabase error details to the API layer.

### 7.4 `backend/app/api/dependencies.py`

FastAPI dependency for JWT verification:

```python
async def get_current_user(authorization: str = Header(...)) -> UserProfile:
    # Extract Bearer token from header
    # Call auth_service.get_user(token)
    # Return UserProfile or raise 401
```

- Extracts `Bearer <token>` from `Authorization` header
- Calls Supabase to verify the JWT and get user info
- Returns `UserProfile` on success
- Raises `HTTPException(401)` on any failure (expired, malformed, revoked)
- Used as a dependency on protected route handlers

### 7.5 `backend/app/api/auth.py`

Route handlers that delegate to the auth service. Each handler:
1. Validates input (via Pydantic models)
2. Calls the auth service
3. Returns normalized response or error

### 7.6 Modifications to Existing Files

**`backend/app/main.py`:**
- Import and include `auth_router` at prefix `/api/auth`
- Import and configure `slowapi` rate limiter (in-memory storage)
- Add 429 exception handler

**`backend/app/config.py`:**
- Add settings: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
- Add settings: `HIBP_TIMEOUT_SECONDS` (default: 3), `HIBP_ENABLED` (default: true)

**`backend/app/api/tests.py`:**
- Add `current_user: UserProfile = Depends(get_current_user)` to `generate_test`, `get_test`, and `get_pdf` handlers
- `get_topics` remains public

**`backend/requirements.txt`:**
- Add: `supabase`, `python-jose[cryptography]`, `slowapi`, `httpx`

---

## 8. Frontend Components

### 8.1 New Files

```
frontend/src/
├── context/
│   └── AuthContext.tsx           # Auth state provider + useAuth() hook
├── pages/
│   ├── Login.tsx                 # Login form page
│   ├── Register.tsx              # Registration form page
│   ├── Dashboard.tsx             # Authenticated user dashboard
│   └── VerifySuccess.tsx         # Email verification success page
├── components/
│   └── Auth/
│       ├── ProtectedRoute.tsx    # Route guard component
│       ├── GoogleOAuthButton.tsx # "Sign in with Google" button
│       ├── PasswordInput.tsx     # Password field with show/hide toggle
│       └── EmailVerificationBanner.tsx # "Didn't receive email? Resend" component
├── services/
│   └── supabase.ts              # Supabase JS client (OAuth only)
```

### 8.2 Auth Context (`AuthContext.tsx`)

Central auth state management:

**State:**
- `user: UserProfile | null`
- `isAuthenticated: boolean`
- `isLoading: boolean` (true during initial token check)

**Actions:**
- `login(email, password)` → call `POST /api/auth/login` → store tokens in localStorage → set user state
- `register(email, password)` → call `POST /api/auth/signup` → return success message (don't auto-login)
- `loginWithGoogle()` → call Supabase JS `signInWithOAuth({ provider: 'google' })` → OAuth flow → on redirect back, extract tokens → store in localStorage → set user state
- `logout()` → call `POST /api/auth/logout` → clear localStorage → clear user state → redirect to `/`
- `deleteAccount()` → call `DELETE /api/auth/account` → clear localStorage → clear user state → redirect to `/`
- `refreshToken()` → call `POST /api/auth/refresh` → update tokens in localStorage

**Initialization (on mount):**
1. Check localStorage for existing tokens
2. If access token exists → call `GET /api/auth/me` to validate
3. If valid → set user state, `isAuthenticated = true`
4. If expired → attempt refresh with stored refresh token
5. If refresh fails → clear localStorage, `isAuthenticated = false`

**Token refresh strategy:**
- Proactive: refresh when access token has < 2 minutes remaining (check `expires_in` stored alongside tokens)
- Reactive: on 401 response, attempt one refresh and retry the original request
- **Refresh mutex:** If multiple API calls receive 401 simultaneously, only the first triggers a refresh. Subsequent 401s await the in-flight refresh result rather than initiating their own. This prevents race conditions where the first refresh invalidates the token and subsequent refreshes fail, causing unnecessary logouts.
- If refresh fails → logout

### 8.3 Supabase JS Client (`supabase.ts`)

Minimal Supabase client used ONLY for Google OAuth:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)

export const signInWithGoogle = () =>
  supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: `${window.location.origin}/auth/callback` }
  })
```

This client is NOT used for email/password auth, token management, or any other auth operation.

### 8.4 Pages

**Login (`/login`):**
- Email + password form
- "Sign in with Google" button (GoogleOAuthButton)
- Link to Register page
- Error display area (generic "Invalid email or password")
- On success → redirect to Dashboard (or to originally intended URL if redirected from ProtectedRoute)
- Redirect to Dashboard if already authenticated

**Register (`/register`):**
- Email + password + confirm password form
- Password requirements display ("Minimum 8 characters")
- "Sign up with Google" button
- On success → show "Check your email for verification link" message (don't auto-login) with `EmailVerificationBanner` ("Didn't receive the email? Click to resend." — calls `POST /api/auth/resend-verification`)
- Link to Login page
- Redirect to Dashboard if already authenticated

**Dashboard (`/dashboard`):**
- Welcome message with user email
- "Generate New Test" button → `/generate`
- "Sign Out" button
- "Delete Account" button with confirmation modal ("Are you sure? This cannot be undone."). Re-authentication is not required (user already has valid JWT). Deletion is immediate with no grace period. If the API call fails, display an error and allow retry.
- In Layer 3, this page will show subscription status

**Verify Success (`/auth/verify-success`):**
- "Email verified successfully!" message
- "Go to Login" button → `/login`

**OAuth Callback (`/auth/callback`):**
- Handles redirect from Google OAuth
- Extracts session from Supabase URL hash/params
- Stores tokens in localStorage
- Redirects to Dashboard

### 8.5 Protected Route (`ProtectedRoute.tsx`)

Route wrapper component:
1. If `isLoading` → show loading spinner
2. If `isAuthenticated` → render children
3. If not authenticated → redirect to `/login` with `?redirect={current_path}` query param (preserves intended destination)

### 8.6 Route Updates (`App.tsx`)

```
/                         → Landing (public)
/login                    → Login (public, redirects if authenticated)
/register                 → Register (public, redirects if authenticated)
/auth/verify-success      → VerifySuccess (public)
/auth/callback            → OAuth callback handler (public)
/dashboard                → Dashboard (protected)
/generate                 → Generate (protected — existing, wrapped in ProtectedRoute)
/preview/:testId          → Preview (protected — existing, wrapped in ProtectedRoute)
*                         → NotFound (public)
```

### 8.8 Accessibility (FR-024 — WCAG 2.1 Level AA)

All auth UI components must meet WCAG 2.1 Level AA:

- **Forms:** Every input must have an associated `<label>` element (not just placeholder text). Use `htmlFor`/`id` pairing.
- **Error announcements:** Error messages must be announced to screen readers. Use `aria-live="polite"` region or `aria-describedby` on inputs pointing to error text.
- **Color contrast:** Minimum 4.5:1 ratio for normal text, 3:1 for large text (18px+) and UI components (buttons, inputs).
- **Keyboard navigation:** All interactive elements must be reachable and operable via keyboard. Tab order must be logical. Visible focus indicators on all focusable elements.
- **Loading states:** The ProtectedRoute spinner must have `aria-label="Loading"` or equivalent. Dashboard loading state same.
- **Buttons:** GoogleOAuthButton and all action buttons must have accessible names (visible text or `aria-label`).
- **Modals:** Delete account confirmation modal must trap focus, be dismissible with Escape, and return focus to the trigger button on close.
- **Password input:** Show/hide toggle must have `aria-label` that updates with state ("Show password" / "Hide password").

### 8.9 Modifications to Existing Files

**`frontend/src/services/api.ts`:**
- Add auth API functions: `authSignup`, `authLogin`, `authRefresh`, `authLogout`, `authMe`, `authDeleteAccount`, `authResendVerification`
- Add request interceptor: attach `Authorization: Bearer` header from localStorage
- Add response interceptor: on 401, attempt token refresh + retry once, then logout

**`frontend/package.json`:**
- Add: `@supabase/supabase-js`

**`frontend/src/App.tsx`:**
- Wrap app in `AuthProvider`
- Add new routes (login, register, dashboard, verify-success, callback)
- Wrap existing `/generate` and `/preview/:testId` in `ProtectedRoute`

---

## 9. Environment Variables

### 9.1 Backend (`backend/.env`)

```env
# Supabase (user creates keys at https://supabase.com/dashboard)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Existing
CORS_ORIGINS=["http://localhost:5173"]
LOG_LEVEL=info

# HIBP
HIBP_TIMEOUT_SECONDS=3
HIBP_ENABLED=true
```

### 9.2 Frontend (`frontend/.env`)

```env
# Supabase (for Google OAuth only)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Existing
VITE_API_URL=http://localhost:8000
```

### 9.3 `.env.example` Files

Both `backend/.env.example` and `frontend/.env.example` will be created with placeholder values and comments explaining where to get each key. Actual `.env` files are in `.gitignore`.

**API keys are created by the user only.** When we reach the Supabase setup phase, step-by-step instructions will be provided using context7 for the latest Supabase documentation, including exactly which dashboard pages to visit and what to click.

---

## 10. Testing Strategy

### 10.1 Phase 0 — Frontend Testing Infrastructure (T037)

Set up the testing foundation before any auth work:
- Install: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `msw` (Mock Service Worker), `jsdom`
- Configure: `vitest.config.ts` with jsdom environment, setup file for `@testing-library/jest-dom`
- Write baseline tests for existing components: MathRenderer, TopicSelector, DifficultySelector, Landing page
- Update `frontend.yml` CI workflow to run `vitest`

### 10.2 Backend Auth Tests

**Unit tests (`backend/tests/unit/test_auth_service.py`):**
- `check_password_breached`: found in breach → True, not found → False, API down → False + warning logged
- Password validation: below 8 chars → rejected, 8+ chars → accepted
- `verify_jwt`: valid token → user, expired token → error, malformed → error
- Error normalization: Supabase errors mapped to application exceptions

**Integration tests (`backend/tests/integration/test_auth.py`):**
- Signup: valid → 201, duplicate email → 409, short password → 400, breached password → 400
- Login: valid → 200 + tokens, wrong password → 401, wrong email → 401, unverified → 401
- Refresh: valid → 200 + new tokens, expired refresh → 401
- Me: valid token → 200 + profile, no token → 401, expired token → 401
- Logout: valid → 200, no token → 401
- Delete account: valid → 200, no token → 401
- Protected endpoints: generate/get/pdf return 401 without auth, 200 with valid auth
- Topics endpoint: still accessible without auth
- Rate limiting: login 11 times in 1 minute → 429

**E2E test (`backend/tests/integration/test_auth_e2e.py`):**
- Full flow: signup → verify (simulated) → login → access protected → refresh → logout → verify 401
- Delete account flow: signup → login → delete → verify 401

### 10.3 Frontend Auth Tests

**Component tests (`frontend/tests/`):**
- `Login.test.tsx`: form renders, validation, submit calls API, error display, redirect on success, Google OAuth button
- `Register.test.tsx`: form renders, password requirements display, confirm password match, submit calls API, success message, Google OAuth button
- `Dashboard.test.tsx`: user info displayed, generate button, logout button, delete account with confirmation
- `ProtectedRoute.test.tsx`: shows spinner while loading, renders children when authenticated, redirects when not authenticated
- `AuthContext.test.tsx`: login sets state, logout clears state, token refresh on mount, 401 triggers refresh

All frontend tests use MSW to mock API responses.

---

## 11. Implementation Phases

### Phase 0: Frontend Testing Infrastructure (T037 from Layer 1)
- Set up vitest + testing-library + msw
- Write baseline tests for existing Layer 1 components
- Update CI

### Phase 1: Supabase Setup (T100–T102)
- **USER ACTION REQUIRED**: Create Supabase project, get API keys, configure Auth providers
- Create `.env` and `.env.example` files
- Install backend + frontend dependencies
- Update `backend/app/config.py` with new settings

### Phase 2: Backend Auth (T103–T107)
- Pydantic auth models
- Auth service (Supabase integration + HIBP)
- `get_current_user` dependency
- Auth endpoints
- Wire auth router into main.py
- Add rate limiting with slowapi
- Protect existing endpoints

### Phase 3: Frontend Auth (T108–T116)
- Supabase JS client (OAuth only)
- Auth context + useAuth hook
- Login, Register, Dashboard, VerifySuccess pages
- ProtectedRoute component
- GoogleOAuthButton, PasswordInput components
- Update App.tsx routing
- Update api.ts with auth headers + interceptors

### Phase 4: Testing (T117–T120)
- Backend auth unit tests
- Backend auth integration tests
- Frontend auth component tests
- E2E auth smoke test

### Phase 5: Verification
- Full manual test of all auth flows
- CI passes on all workflows
- Code review

---

## 12. Dependencies Added

### Backend
| Package | Purpose |
|---|---|
| `supabase` | Supabase Python client for Auth operations |
| `python-jose[cryptography]` | JWT decoding/verification |
| `slowapi` | Rate limiting middleware for FastAPI |
| `httpx` | Async HTTP client for HIBP API (already a dev dependency, move to main) |

### Frontend
| Package | Purpose |
|---|---|
| `@supabase/supabase-js` | Google OAuth redirect flow only |
| `vitest` (dev) | Test runner |
| `@testing-library/react` (dev) | Component testing |
| `@testing-library/jest-dom` (dev) | DOM assertion matchers |
| `@testing-library/user-event` (dev) | User interaction simulation |
| `msw` (dev) | API mocking for tests |
| `jsdom` (dev) | Browser environment for tests |

---

## 13. Out of Scope (Layer 3)

These items are explicitly deferred to Layer 3:
- Stripe billing integration
- Subscription-gated access (`require_active_subscription` dependency)
- Subscriptions database table
- Account deletion cascade (cancel Stripe subscription + delete Stripe customer)
- CORS hardening for production domains
- CSRF protection middleware
- Security headers middleware
- Cloudflare DDoS setup
- Global rate limiting (100/min per user) — Layer 2 only adds auth-specific limits

---

## 15. Task Deviations from tasks.md

This design intentionally deviates from several tasks in `specs/001-core-platform/tasks.md` based on decisions made during the brainstorming process:

| Task | Original Description | Deviation | Reason |
|---|---|---|---|
| **T108** | "Frontend talks to Supabase directly for auth" — export signUp, signIn, signOut, getSession, onAuthStateChange | Supabase JS is used ONLY for Google OAuth (`signInWithOAuth`). All email/password auth goes through backend `/api/auth/*` endpoints. | Decision Q2: Backend as auth proxy for centralized control, security, and swappability. |
| **T109** | "AuthProvider with onAuthStateChange subscription" | AuthContext uses localStorage-based state with `GET /api/auth/me` validation on mount. No `onAuthStateChange` (that's a Supabase JS event which won't fire for backend-proxied auth). | Follows from T108 deviation — auth state comes from API responses, not Supabase client events. |
| **T214** (Layer 3) | "Implement rate limiting: add slowapi to requirements" | Auth-specific rate limiting (slowapi) pulled forward into Layer 2. T214 in Layer 3 only needs to add global per-user limits to non-auth endpoints. | Auth endpoints are prime brute-force targets; rate limiting is a security necessity, not a nice-to-have. |
| **T116** | Lists EmailVerificationBanner | Added `POST /api/auth/resend-verification` endpoint (not in original tasks) to support the resend functionality. | Without a resend endpoint, users who don't receive verification emails would be permanently locked out. |
| **Signup 409** | T105 implies distinct "email exists" error | Signup returns identical 201 for new and existing emails (anti-enumeration). | Consistent with the vague-error security posture decided in Q8. |

---

## 14. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Supabase free tier rate limits (2 emails/hour default SMTP) | Blocks testing signup flow | User configures custom SMTP in Supabase or tests with pre-verified accounts |
| Google OAuth requires Google Cloud Console setup | Blocks OAuth testing | Provide step-by-step instructions; email/password works independently |
| HIBP API changes or goes down | Signup blocked | Lenient mode — allow signup, log warning |
| Supabase JS version mismatch | OAuth flow breaks | Pin version in package.json, use context7 for latest docs |
| Cross-origin issues (Vercel + Render) | Auth headers not sent | CORS config already exists; verify `allow_credentials` and `Authorization` header in allowed headers |
