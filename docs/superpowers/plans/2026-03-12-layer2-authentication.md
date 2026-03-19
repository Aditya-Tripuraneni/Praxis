# Layer 2: Authentication — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add authentication to ProblemGenerator so users must register/login before generating tests or downloading PDFs.

**Architecture:** Backend-as-auth-proxy — all auth flows go through FastAPI `/api/auth/*` endpoints wrapping Supabase Auth. Google OAuth is the sole exception (frontend uses Supabase JS for the redirect flow). JWTs are verified on every protected API call. Tokens stored in localStorage.

**Tech Stack:** Supabase Auth, slowapi, httpx (HIBP), @supabase/supabase-js (OAuth only), vitest, @testing-library/react, msw

**Spec:** `docs/superpowers/specs/2026-03-12-layer2-authentication-design.md`

---

## File Map

### New Files (Backend)

| File | Responsibility |
|---|---|
| `backend/app/models/auth.py` | Pydantic request/response models for auth |
| `backend/app/services/auth.py` | Supabase Auth integration + HIBP breached password check |
| `backend/app/api/auth.py` | Auth endpoint route handlers |
| `backend/app/api/dependencies.py` | `get_current_user` FastAPI dependency |
| `backend/app/rate_limiter.py` | Shared slowapi Limiter instance (avoids circular imports) |
| `backend/.env.example` | Template for required environment variables |
| `backend/tests/unit/test_auth_service.py` | Auth service unit tests |
| `backend/tests/integration/test_auth.py` | Auth endpoint integration tests |

### New Files (Frontend)

| File | Responsibility |
|---|---|
| `frontend/src/services/supabase.ts` | Minimal Supabase client (Google OAuth only) |
| `frontend/src/context/AuthContext.tsx` | Auth state provider + useAuth hook |
| `frontend/src/components/Auth/ProtectedRoute.tsx` | Route guard — redirect to login if unauthenticated |
| `frontend/src/components/Auth/GoogleOAuthButton.tsx` | "Sign in with Google" button |
| `frontend/src/components/Auth/PasswordInput.tsx` | Password field with show/hide toggle |
| `frontend/src/components/Auth/EmailVerificationBanner.tsx` | "Didn't receive email? Resend" |
| `frontend/src/pages/Login.tsx` | Login page |
| `frontend/src/pages/Register.tsx` | Registration page |
| `frontend/src/pages/Dashboard.tsx` | Authenticated user dashboard |
| `frontend/src/pages/VerifySuccess.tsx` | Email verification success page |
| `frontend/src/pages/OAuthCallback.tsx` | Google OAuth redirect handler |
| `frontend/.env.example` | Template for required frontend env vars |
| `frontend/vitest.config.ts` | Vitest configuration |
| `frontend/src/test/setup.ts` | Test setup file (jest-dom matchers) |
| `frontend/src/test/mocks/handlers.ts` | MSW request handlers |
| `frontend/src/test/mocks/server.ts` | MSW server setup |
| `frontend/src/__tests__/MathRenderer.test.tsx` | Baseline MathRenderer test |
| `frontend/src/__tests__/Landing.test.tsx` | Baseline Landing page test |
| `frontend/src/__tests__/Login.test.tsx` | Login page tests |
| `frontend/src/__tests__/Register.test.tsx` | Register page tests |
| `frontend/src/__tests__/Dashboard.test.tsx` | Dashboard page tests |
| `frontend/src/__tests__/ProtectedRoute.test.tsx` | ProtectedRoute tests |
| `frontend/src/__tests__/AuthContext.test.tsx` | Auth context tests |

### Modified Files

| File | What Changes |
|---|---|
| `backend/requirements.txt` | Add: supabase, slowapi, httpx, email-validator |
| `backend/app/config.py` | Add Supabase + HIBP settings |
| `backend/app/main.py` | Add auth router, slowapi rate limiter, 429 handler |
| `backend/app/api/tests.py` | Add `get_current_user` dependency to protected endpoints |
| `backend/app/api/pdf.py` | Add `get_current_user` dependency |
| `backend/tests/conftest.py` | Add auth fixtures (mock JWT, authenticated client) |
| `frontend/package.json` | Add @supabase/supabase-js, vitest, testing-library, msw, jsdom |
| `frontend/src/types/index.ts` | Add auth-related TypeScript interfaces |
| `frontend/src/services/api.ts` | Add auth API functions, request/response interceptors |
| `frontend/src/App.tsx` | Wrap in AuthProvider, add auth routes, ProtectedRoute |
| `frontend/src/main.tsx` | Wrap in AuthProvider |
| `.github/workflows/frontend.yml` | Add vitest test step |
| `docker-compose.yml` | Add Supabase env vars to backend + frontend services |

---

## Chunk 1: Frontend Testing Infrastructure (T037)

### Task 1: Install frontend testing dependencies

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install test dependencies**

Run from `PROBLEMGENERATOR/frontend/`:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event msw jsdom
```

- [ ] **Step 2: Verify package.json updated**

Run: `cat frontend/package.json | grep -E "vitest|testing-library|msw|jsdom"`
Expected: all 6 packages appear in devDependencies

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: add frontend testing dependencies (vitest, testing-library, msw, jsdom)"
```

---

### Task 2: Configure vitest

**Files:**
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`
- Modify: `frontend/tsconfig.json`

- [ ] **Step 1: Create vitest config**

Create `frontend/vitest.config.ts`:
```typescript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    globals: true,
    css: true,
  },
});
```

- [ ] **Step 2: Create test setup file**

Create `frontend/src/test/setup.ts`:
```typescript
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 3: Add test script to package.json**

Add to `frontend/package.json` scripts section:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 4: Add vitest types to tsconfig.json**

In `frontend/tsconfig.json`, add `"vitest/globals"` to the `"types"` array inside `compilerOptions`:
```json
"types": ["vitest/globals"]
```

- [ ] **Step 5: Verify vitest runs (no tests yet)**

Run: `cd PROBLEMGENERATOR/frontend && npm test`
Expected: "No test files found" or similar (no error)

- [ ] **Step 6: Commit**

```bash
git add frontend/vitest.config.ts frontend/src/test/setup.ts frontend/package.json frontend/tsconfig.json
git commit -m "chore: configure vitest with jsdom, testing-library setup"
```

---

### Task 3: Set up MSW mock server

**Files:**
- Create: `frontend/src/test/mocks/handlers.ts`
- Create: `frontend/src/test/mocks/server.ts`

- [ ] **Step 1: Create MSW handlers**

Create `frontend/src/test/mocks/handlers.ts`:
```typescript
import { http, HttpResponse } from "msw";

export const handlers = [
  // Topics endpoint (public)
  http.get("/api/tests/topics", () => {
    return HttpResponse.json([
      {
        id: "algebra",
        name: "Algebra",
        subtopics: [{ id: "linear_equations", name: "Linear Equations" }],
        difficulties: ["easy", "medium", "hard"],
        template_count: 5,
      },
    ]);
  }),
];
```

- [ ] **Step 2: Create MSW server**

Create `frontend/src/test/mocks/server.ts`:
```typescript
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

- [ ] **Step 3: Wire MSW into test setup**

Update `frontend/src/test/setup.ts`:
```typescript
import "@testing-library/jest-dom/vitest";
import { server } from "./mocks/server";
import { beforeAll, afterEach, afterAll } from "vitest";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/test/
git commit -m "chore: set up MSW mock server for frontend tests"
```

---

### Task 4: Write baseline MathRenderer test

**Files:**
- Create: `frontend/src/__tests__/MathRenderer.test.tsx`

- [ ] **Step 1: Write the test**

Create `frontend/src/__tests__/MathRenderer.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import MathRenderer from "../components/MathRenderer/MathRenderer";

describe("MathRenderer", () => {
  it("renders LaTeX expression", () => {
    render(<MathRenderer latex="$x^2$" />);
    // KaTeX renders into a span with class "katex"
    const katexEl = document.querySelector(".katex");
    expect(katexEl).toBeInTheDocument();
  });

  it("renders plain text when no math delimiters", () => {
    render(<MathRenderer latex="hello world" />);
    expect(screen.getByText("hello world")).toBeInTheDocument();
  });

  it("renders mixed text and math", () => {
    render(<MathRenderer latex="Solve $x + 1 = 2$" />);
    expect(screen.getByText("Solve")).toBeInTheDocument();
    expect(document.querySelector(".katex")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test**

Run: `cd PROBLEMGENERATOR/frontend && npm test -- src/__tests__/MathRenderer.test.tsx`
Expected: 3 tests PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/__tests__/MathRenderer.test.tsx
git commit -m "test: add baseline MathRenderer component tests"
```

---

### Task 5: Write baseline Landing page test

**Files:**
- Create: `frontend/src/__tests__/Landing.test.tsx`

- [ ] **Step 1: Write the test**

Create `frontend/src/__tests__/Landing.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Landing from "../pages/Landing";

describe("Landing", () => {
  it("renders the title", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>
    );
    expect(screen.getByText("ProblemGenerator")).toBeInTheDocument();
  });

  it("renders the Get Started button", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>
    );
    expect(screen.getByRole("button", { name: /get started/i })).toBeInTheDocument();
  });

  it("renders feature sections", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>
    );
    expect(screen.getByText("Topics")).toBeInTheDocument();
    expect(screen.getByText("Difficulty Levels")).toBeInTheDocument();
    expect(screen.getByText("Instant PDF")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test**

Run: `cd PROBLEMGENERATOR/frontend && npm test -- src/__tests__/Landing.test.tsx`
Expected: 3 tests PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/__tests__/Landing.test.tsx
git commit -m "test: add baseline Landing page tests"
```

---

### Task 6: Update frontend CI to run tests

**Files:**
- Modify: `.github/workflows/frontend.yml`

- [ ] **Step 1: Add test step to frontend CI**

In `.github/workflows/frontend.yml`, add after the "Type check" step (after line 35):
```yaml
      - name: Test
        run: npm test
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/frontend.yml
git commit -m "ci: add vitest to frontend CI workflow"
```

---

## Chunk 2: Supabase Setup (T100–T102)

### Task 7: Create .env.example files

**Files:**
- Create: `backend/.env.example`
- Create: `frontend/.env.example`

- [ ] **Step 1: Create backend .env.example**

Create `backend/.env.example`:
```env
# === Supabase ===
# Get these from: https://supabase.com/dashboard → your project → Settings → API
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# === Application ===
CORS_ORIGINS=["http://localhost:5173"]
LOG_LEVEL=info

# === HIBP (HaveIBeenPwned breached password check) ===
HIBP_TIMEOUT_SECONDS=3
HIBP_ENABLED=true
```

- [ ] **Step 2: Create frontend .env.example**

Create `frontend/.env.example`:
```env
# === Supabase (for Google OAuth only) ===
# Get these from: https://supabase.com/dashboard → your project → Settings → API
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# === Backend API ===
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 3: Verify .env is already in .gitignore**

Run: `grep "^\.env$" PROBLEMGENERATOR/.gitignore`
Expected: `.env` found (already present at line 18)

- [ ] **Step 4: Commit**

```bash
git add backend/.env.example frontend/.env.example
git commit -m "chore: add .env.example files for Supabase and HIBP configuration"
```

---

### Task 8: Install backend auth dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add dependencies to requirements.txt**

Add these lines to `backend/requirements.txt` (after line 11, before the blank line):
```
supabase>=2.0
slowapi>=0.1.9
httpx>=0.27
email-validator>=2.0
```

Note: `httpx` was already in `requirements-dev.txt` — it's now a production dependency too (used for HIBP API calls). `email-validator` is required by Pydantic's `EmailStr` type. `python-jose` is NOT needed — Supabase handles JWT verification server-side.

Also add `pytest-timeout>=2.0` to `backend/requirements-dev.txt`:
```
pytest-timeout>=2.0
```

- [ ] **Step 2: Install in venv**

Run: `cd PROBLEMGENERATOR/backend && pip install -r requirements.txt`
Expected: All packages install successfully

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add supabase, slowapi, httpx, email-validator to backend dependencies"
```

---

### Task 9: Install frontend Supabase dependency

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install @supabase/supabase-js**

Run from `PROBLEMGENERATOR/frontend/`:
```bash
npm install @supabase/supabase-js
```

- [ ] **Step 2: Verify**

Run: `cat frontend/package.json | grep supabase`
Expected: `"@supabase/supabase-js": "^2.x.x"` in dependencies

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: add @supabase/supabase-js for Google OAuth"
```

---

### Task 10: Update backend config with Supabase settings

**Files:**
- Modify: `backend/app/config.py`

- [ ] **Step 1: Add Supabase and HIBP settings**

Replace the entire contents of `backend/app/config.py` with:
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "info"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # HIBP breached password check
    hibp_timeout_seconds: int = 3
    hibp_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 2: Verify existing tests still pass**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/ -v --timeout=60`
Expected: All existing tests pass (new settings have defaults so nothing breaks)

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py
git commit -m "feat: add Supabase and HIBP config settings"
```

---

### Task 11: USER ACTION — Create Supabase project and get API keys

**This task is done by the user, not by the agent.**

The user needs to:

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose an organization (or create one)
4. Name the project (e.g., "problemgenerator")
5. Set a database password (save it somewhere safe)
6. Choose a region close to you
7. Click "Create new project" and wait for provisioning

Once the project is created:

1. Go to **Settings → API** (left sidebar)
2. Copy these values into `backend/.env`:
   - **Project URL** → `SUPABASE_URL`
   - **anon public key** → `SUPABASE_ANON_KEY`
   - **service_role secret key** → `SUPABASE_SERVICE_ROLE_KEY`
3. Go to **Settings → API → JWT Settings**
   - Copy **JWT Secret** → `SUPABASE_JWT_SECRET`
4. Copy SUPABASE_URL and SUPABASE_ANON_KEY into `frontend/.env` as well (VITE_ prefix)

Then configure auth providers:

1. Go to **Authentication → Providers**
2. **Email:** Should be enabled by default. Verify:
   - "Enable Email provider" is ON
   - "Confirm email" is ON (require email verification)
3. **Google OAuth** (can be done later if you don't have Google Cloud credentials yet):
   - Enable Google provider
   - Enter Client ID and Client Secret from Google Cloud Console
   - (Detailed instructions will be provided via context7 when we get there)
4. Go to **Authentication → URL Configuration**
   - Set **Site URL**: `http://localhost:5173`
   - Add **Redirect URLs**: `http://localhost:5173/auth/verify-success`, `http://localhost:5173/auth/callback`

---

### Task 12: Update docker-compose with Supabase env vars

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Add Supabase env vars to backend service**

In `docker-compose.yml`, add to the backend service `environment` section (after line 12):
```yaml
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
      - HIBP_ENABLED=${HIBP_ENABLED:-true}
```

- [ ] **Step 2: Add Supabase env vars to frontend service**

In `docker-compose.yml`, add to the frontend service `environment` section (after line 31):
```yaml
      - VITE_SUPABASE_URL=${SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "chore: add Supabase env vars to docker-compose"
```

---

## Chunk 3: Backend Auth — Models + Service (T103, T107)

### Task 13: Create auth Pydantic models

**Files:**
- Create: `backend/app/models/auth.py`

- [ ] **Step 1: Create the models file**

Create `backend/app/models/auth.py`:
```python
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UserProfile(BaseModel):
    id: str
    email: str
    email_verified: bool
    created_at: datetime | None = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    user: UserProfile


class RefreshResponse(BaseModel):
    """Token refresh response — no user field (unlike login)."""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"


class AuthMessage(BaseModel):
    message: str
```

- [ ] **Step 2: Verify imports work**

Run: `cd PROBLEMGENERATOR/backend && python -c "from app.models.auth import SignupRequest, LoginRequest, AuthResponse; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/auth.py
git commit -m "feat: add auth Pydantic models (signup, login, tokens, user profile)"
```

---

### Task 14: Implement auth service — HIBP breached password check

**Files:**
- Create: `backend/app/services/auth.py` (partial — HIBP only first)

- [ ] **Step 1: Write the HIBP unit test**

Create `backend/tests/unit/test_auth_service.py`:
```python
import hashlib
from unittest.mock import AsyncMock, patch

import pytest

from app.services.auth import AuthService


@pytest.fixture
def auth_service():
    """AuthService with no real Supabase connection (for unit tests)."""
    return AuthService()


class TestCheckPasswordBreached:
    """Tests for HIBP k-anonymity password check."""

    @pytest.mark.asyncio
    async def test_breached_password_detected(self, auth_service):
        """A password whose hash suffix appears in the HIBP response is flagged."""
        password = "password123"
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = f"{suffix}:42\r\nABCDE12345:10\r\n"

        with patch("app.services.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await auth_service.check_password_breached(password)
            assert result is True

    @pytest.mark.asyncio
    async def test_safe_password_not_flagged(self, auth_service):
        """A password whose hash suffix does NOT appear is not flagged."""
        password = "my-very-unique-passphrase-xyz-2026"
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        suffix = sha1[5:]

        mock_response = AsyncMock()
        mock_response.status_code = 200
        # Return suffixes that don't match
        mock_response.text = "AAAAAAA1111:5\r\nBBBBBBB2222:3\r\n"

        with patch("app.services.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await auth_service.check_password_breached(password)
            assert result is False

    @pytest.mark.asyncio
    async def test_api_down_returns_false_lenient(self, auth_service):
        """If HIBP API is unreachable, allow signup (lenient mode)."""
        with patch("app.services.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client_cls.return_value = mock_client

            result = await auth_service.check_password_breached("anypassword")
            assert result is False  # lenient — don't block signup

    @pytest.mark.asyncio
    async def test_hibp_disabled_returns_false(self):
        """When HIBP is disabled via config, skip the check."""
        service = AuthService()
        with patch("app.services.auth.settings") as mock_settings:
            mock_settings.hibp_enabled = False
            result = await service.check_password_breached("password123")
            assert result is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/unit/test_auth_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.auth'` (service doesn't exist yet)

- [ ] **Step 3: Create the auth service with HIBP check**

Create `backend/app/services/auth.py`:
```python
"""Authentication service — wraps Supabase Auth and HIBP password checking."""

import hashlib
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when login credentials are invalid or user is unverified."""


class UserExistsError(Exception):
    """Raised when a signup email is already registered."""


class InvalidTokenError(Exception):
    """Raised when a JWT or refresh token is invalid/expired."""


class BreachedPasswordError(Exception):
    """Raised when a password is found in the HIBP breached database."""


class AuthService:
    """Wraps Supabase Auth operations with password security checks."""

    async def check_password_breached(self, password: str) -> bool:
        """Check password against HIBP Pwned Passwords API (k-anonymity).

        Returns True if the password has been found in a data breach.
        Returns False if safe, if HIBP is disabled, or if the API is unreachable
        (lenient mode — never block signups due to third-party outage).
        """
        if not settings.hibp_enabled:
            return False

        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]

        try:
            async with httpx.AsyncClient(
                timeout=settings.hibp_timeout_seconds
            ) as client:
                response = await client.get(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    headers={"User-Agent": "ProblemGenerator-PasswordCheck"},
                )
                response.raise_for_status()

            for line in response.text.splitlines():
                parts = line.split(":")
                if len(parts) == 2 and parts[0].strip() == suffix:
                    return True

            return False

        except Exception:
            logger.warning(
                "HIBP API unreachable — breached password check skipped",
                exc_info=True,
            )
            return False


auth_service = AuthService()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/unit/test_auth_service.py -v`
Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/auth.py backend/tests/unit/test_auth_service.py
git commit -m "feat: add HIBP breached password check with lenient failure mode"
```

---

### Task 15: Implement auth service — Supabase Auth integration

**Files:**
- Modify: `backend/app/services/auth.py`
- Modify: `backend/tests/unit/test_auth_service.py`

- [ ] **Step 1: Write unit tests for Supabase auth methods**

Add to `backend/tests/unit/test_auth_service.py`:
```python
class TestPasswordValidation:
    """Tests for password length validation."""

    def test_password_too_short(self):
        """Passwords under 8 chars should fail Pydantic validation."""
        from app.models.auth import SignupRequest
        with pytest.raises(Exception):  # ValidationError
            SignupRequest(email="test@example.com", password="short")

    def test_password_too_long(self):
        """Passwords over 128 chars should fail Pydantic validation."""
        from app.models.auth import SignupRequest
        with pytest.raises(Exception):  # ValidationError
            SignupRequest(email="test@example.com", password="a" * 129)

    def test_password_valid_length(self):
        """Passwords between 8-128 chars should pass."""
        from app.models.auth import SignupRequest
        req = SignupRequest(email="test@example.com", password="validpass")
        assert req.password == "validpass"

    def test_password_max_length(self):
        """128 chars exactly should pass."""
        from app.models.auth import SignupRequest
        req = SignupRequest(email="test@example.com", password="a" * 128)
        assert len(req.password) == 128
```

- [ ] **Step 2: Run to verify tests pass**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/unit/test_auth_service.py::TestPasswordValidation -v`
Expected: 4 tests PASS

- [ ] **Step 3: Add Supabase methods to auth service**

Update `backend/app/services/auth.py` — add the Supabase client and auth methods after the `AuthService` class definition. Replace the entire file:

```python
"""Authentication service — wraps Supabase Auth and HIBP password checking.

Note: Supabase Python client is synchronous. All Supabase calls are wrapped
in asyncio.to_thread() to avoid blocking the FastAPI event loop.
"""

import asyncio
import hashlib
import logging

import httpx
from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when login credentials are invalid or user is unverified."""


class UserExistsError(Exception):
    """Raised when a signup email is already registered."""


class InvalidTokenError(Exception):
    """Raised when a JWT or refresh token is invalid/expired."""


class BreachedPasswordError(Exception):
    """Raised when a password is found in the HIBP breached database."""


def _create_supabase_client() -> Client | None:
    """Create Supabase client if credentials are configured."""
    if settings.supabase_url and settings.supabase_service_role_key:
        return create_client(settings.supabase_url, settings.supabase_service_role_key)
    return None


class AuthService:
    """Wraps Supabase Auth operations with password security checks."""

    def __init__(self):
        self._client = _create_supabase_client()

    @property
    def client(self) -> Client:
        if self._client is None:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._client

    async def signup(self, email: str, password: str) -> str:
        """Register a new user. Returns success message.

        Anti-enumeration: returns same message whether email is new or exists.
        """
        # Check breached password
        if await self.check_password_breached(password):
            raise BreachedPasswordError(
                "This password has been found in a data breach. "
                "Please choose a different password."
            )

        try:
            await asyncio.to_thread(
                self.client.auth.sign_up, {"email": email, "password": password}
            )
        except Exception as e:
            error_msg = str(e).lower()
            # If user already exists, return same message (anti-enumeration)
            if "already registered" in error_msg or "already exists" in error_msg:
                logger.info("Signup attempt for existing email (suppressed)")
                return "Account created. Please check your email to verify your account."
            raise

        return "Account created. Please check your email to verify your account."

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user. Returns tokens + user profile.

        Always returns generic error for any failure (anti-enumeration).
        """
        try:
            response = await asyncio.to_thread(
                self.client.auth.sign_in_with_password,
                {"email": email, "password": password},
            )
        except Exception:
            raise AuthenticationError("Invalid email or password")

        if not response.session:
            raise AuthenticationError("Invalid email or password")

        user = response.user
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Check email verified
        if not user.email_confirmed_at:
            raise AuthenticationError("Invalid email or password")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in or 900,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None,
                "created_at": str(user.created_at) if user.created_at else None,
            },
        }

    async def refresh(self, refresh_token: str) -> dict:
        """Exchange refresh token for new access token."""
        try:
            response = await asyncio.to_thread(
                self.client.auth.refresh_session, refresh_token
            )
        except Exception:
            raise InvalidTokenError("Invalid or expired refresh token")

        if not response.session:
            raise InvalidTokenError("Invalid or expired refresh token")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in or 900,
            "token_type": "bearer",
        }

    async def logout(self, access_token: str) -> None:
        """Invalidate the current session."""
        try:
            await asyncio.to_thread(self.client.auth.sign_out, access_token)
        except Exception:
            logger.warning("Logout failed (token may already be invalid)")

    async def get_user(self, access_token: str) -> dict:
        """Get user profile from access token."""
        try:
            response = await asyncio.to_thread(
                self.client.auth.get_user, access_token
            )
        except Exception:
            raise InvalidTokenError("Invalid or expired token")

        if not response.user:
            raise InvalidTokenError("Invalid or expired token")

        user = response.user
        return {
            "id": user.id,
            "email": user.email,
            "email_verified": user.email_confirmed_at is not None,
            "created_at": str(user.created_at) if user.created_at else None,
        }

    async def delete_user(self, user_id: str) -> None:
        """Delete a user account (admin operation)."""
        try:
            await asyncio.to_thread(self.client.auth.admin.delete_user, user_id)
        except Exception:
            logger.exception("Failed to delete user %s", user_id)
            raise

    async def resend_verification(self, email: str) -> str:
        """Resend verification email. Anti-enumeration: same message always."""
        try:
            await asyncio.to_thread(
                self.client.auth.resend, {"type": "signup", "email": email}
            )
        except Exception:
            logger.info("Resend verification for unknown email (suppressed)")
        return "If an account exists with this email, a verification link has been sent."

    async def check_password_breached(self, password: str) -> bool:
        """Check password against HIBP Pwned Passwords API (k-anonymity).

        Returns True if the password has been found in a data breach.
        Returns False if safe, if HIBP is disabled, or if the API is unreachable
        (lenient mode — never block signups due to third-party outage).
        """
        if not settings.hibp_enabled:
            return False

        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]

        try:
            async with httpx.AsyncClient(
                timeout=settings.hibp_timeout_seconds
            ) as client:
                response = await client.get(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    headers={"User-Agent": "ProblemGenerator-PasswordCheck"},
                )
                response.raise_for_status()

            for line in response.text.splitlines():
                parts = line.split(":")
                if len(parts) == 2 and parts[0].strip() == suffix:
                    return True

            return False

        except Exception:
            logger.warning(
                "HIBP API unreachable — breached password check skipped",
                exc_info=True,
            )
            return False


auth_service = AuthService()
```

- [ ] **Step 4: Run all auth service tests**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/unit/test_auth_service.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Run ALL existing tests to verify no regressions**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/ -v --timeout=60`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/auth.py backend/tests/unit/test_auth_service.py
git commit -m "feat: add Supabase Auth service (signup, login, refresh, logout, delete, resend)"
```

---

## Chunk 4: Backend Auth — Dependencies + Endpoints + Rate Limiting (T104–T106)

### Task 16: Implement get_current_user dependency

**Files:**
- Create: `backend/app/api/dependencies.py`

- [ ] **Step 1: Create the dependency file**

Create `backend/app/api/dependencies.py`:
```python
"""FastAPI dependencies for authentication."""

import logging

from fastapi import Header, HTTPException

from app.models.auth import UserProfile
from app.services.auth import auth_service, InvalidTokenError

logger = logging.getLogger(__name__)


class AuthenticatedUser:
    """Bundles user profile with the raw access token (needed for logout)."""

    def __init__(self, profile: UserProfile, access_token: str):
        self.profile = profile
        self.access_token = access_token


async def get_current_user(authorization: str = Header(...)) -> AuthenticatedUser:
    """Extract and verify JWT from Authorization header.

    Usage: add `auth: AuthenticatedUser = Depends(get_current_user)` to route.
    Access user via `auth.profile`, raw token via `auth.access_token`.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization[7:]  # Strip "Bearer " prefix

    try:
        user_data = await auth_service.get_user(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    except Exception:
        logger.exception("Unexpected error verifying token")
        raise HTTPException(status_code=401, detail="Not authenticated")

    return AuthenticatedUser(profile=UserProfile(**user_data), access_token=token)
```

- [ ] **Step 2: Verify import works**

Run: `cd PROBLEMGENERATOR/backend && python -c "from app.api.dependencies import get_current_user; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/dependencies.py
git commit -m "feat: add get_current_user FastAPI dependency for JWT verification"
```

---

### Task 17: Create auth endpoints

**Files:**
- Create: `backend/app/api/auth.py`

- [ ] **Step 1: Create the auth router**

Create `backend/app/api/auth.py`:
```python
"""Authentication API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, AuthenticatedUser
from app.models.auth import (
    AuthMessage,
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    ResendVerificationRequest,
    SignupRequest,
    UserProfile,
)
from app.services.auth import (
    AuthenticationError,
    BreachedPasswordError,
    InvalidTokenError,
    auth_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=AuthMessage, status_code=201)
async def signup(request: SignupRequest):
    try:
        message = await auth_service.signup(request.email, request.password)
        return AuthMessage(message=message)
    except BreachedPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Signup failed")
        raise HTTPException(status_code=500, detail="Signup failed")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        result = await auth_service.login(request.email, request.password)
        return AuthResponse(**result)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        logger.exception("Login failed")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(request: RefreshRequest):
    try:
        result = await auth_service.refresh(request.refresh_token)
        return RefreshResponse(**result)
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout", response_model=AuthMessage)
async def logout(auth: AuthenticatedUser = Depends(get_current_user)):
    await auth_service.logout(auth.access_token)
    return AuthMessage(message="Logged out successfully")


@router.get("/me", response_model=UserProfile)
async def me(auth: AuthenticatedUser = Depends(get_current_user)):
    return auth.profile


@router.delete("/account", response_model=AuthMessage)
async def delete_account(auth: AuthenticatedUser = Depends(get_current_user)):
    try:
        await auth_service.delete_user(auth.profile.id)
        return AuthMessage(message="Account deleted successfully")
    except Exception:
        logger.exception("Account deletion failed for user %s", auth.profile.id)
        raise HTTPException(status_code=500, detail="Account deletion failed")


@router.post("/resend-verification", response_model=AuthMessage)
async def resend_verification(request: ResendVerificationRequest):
    message = await auth_service.resend_verification(request.email)
    return AuthMessage(message=message)
```

- [ ] **Step 2: Verify import works**

Run: `cd PROBLEMGENERATOR/backend && python -c "from app.api.auth import router; print(f'Routes: {len(router.routes)}')"`
Expected: `Routes: 7`

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/auth.py
git commit -m "feat: add auth API endpoints (signup, login, refresh, logout, me, delete, resend)"
```

---

### Task 18: Wire auth router + rate limiting into main.py

**Files:**
- Create: `backend/app/rate_limiter.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/auth.py`

- [ ] **Step 1: Create shared rate limiter module**

Create `backend/app/rate_limiter.py` (avoids circular imports between main.py and auth.py):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

- [ ] **Step 2: Update main.py**

Replace the entire contents of `backend/app/main.py` with:
```python
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.pdf import router as pdf_router
from app.api.tests import router as tests_router
from app.config import settings
from app.middleware import TimingMiddleware
from app.rate_limiter import limiter

logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

app = FastAPI(
    title="ProblemGenerator",
    version="0.1.0",
    docs_url="/docs" if settings.log_level == "debug" else None,
    redoc_url="/redoc" if settings.log_level == "debug" else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(tests_router)
app.include_router(pdf_router)
app.include_router(auth_router)

app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": app.version}
```

- [ ] **Step 3: Add rate limits to auth endpoints**

Update `backend/app/api/auth.py` — add rate limiting decorators. Add these imports at the top:
```python
from starlette.requests import Request
from app.rate_limiter import limiter
```

Then add `request: Request` as first parameter and `@limiter.limit()` decorator to each endpoint:

```python
@router.post("/signup", response_model=AuthMessage, status_code=201)
@limiter.limit("5/hour")
async def signup(request: Request, body: SignupRequest):
    ...

@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    ...

@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("30/5 minutes")
async def refresh(request: Request, body: RefreshRequest):
    ...

@router.post("/logout", response_model=AuthMessage)
@limiter.limit("10/minute")
async def logout(request: Request, auth: AuthenticatedUser = Depends(get_current_user)):
    ...

@router.get("/me", response_model=UserProfile)
@limiter.limit("30/minute")
async def me(request: Request, auth: AuthenticatedUser = Depends(get_current_user)):
    ...

@router.delete("/account", response_model=AuthMessage)
@limiter.limit("3/hour")
async def delete_account(request: Request, auth: AuthenticatedUser = Depends(get_current_user)):
    ...

@router.post("/resend-verification", response_model=AuthMessage)
@limiter.limit("3/hour")
async def resend_verification(request: Request, body: ResendVerificationRequest):
    ...
```

Note: slowapi's `limits` library natively supports `"30/5 minutes"` syntax.

- [ ] **Step 3: Run existing tests to verify no regressions**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/ -v --timeout=60`
Expected: All existing tests pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/main.py backend/app/api/auth.py
git commit -m "feat: wire auth router into main app, add slowapi rate limiting"
```

---

### Task 19: Protect existing endpoints with auth

**Files:**
- Modify: `backend/app/api/tests.py`
- Modify: `backend/app/api/pdf.py`

- [ ] **Step 1: Add auth dependency to tests.py**

Update `backend/app/api/tests.py`:
```python
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, AuthenticatedUser
from app.engine.types import GenerationError
from app.models.test import GenerateRequest, TestResponse, TopicInfo
from app.services.generation_service import generation_service

router = APIRouter(prefix="/api/tests", tags=["tests"])


@router.post("/generate", response_model=TestResponse)
def generate_test(
    request: GenerateRequest,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    try:
        return generation_service.generate(request)
    except (ValueError, GenerationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/topics", response_model=list[TopicInfo])
def get_topics():
    """Public endpoint — no auth required."""
    return generation_service.get_topics()


@router.get("/{test_id}", response_model=TestResponse)
def get_test(
    test_id: str,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    result = generation_service.get_test(test_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return result
```

- [ ] **Step 2: Add auth dependency to pdf.py**

In `backend/app/api/pdf.py`, add import at the top:
```python
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user, AuthenticatedUser
```

Update the `download_pdf` function signature to include auth:
```python
@router.get("/{test_id}/pdf")
async def download_pdf(
    test_id: str,
    include_answers: bool = True,
    auth: AuthenticatedUser = Depends(get_current_user),
):
```

- [ ] **Step 3: Update test conftest with auth fixtures**

Update `backend/tests/conftest.py`:
```python
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Unauthenticated test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def mock_user():
    """A mock user profile for testing protected endpoints."""
    return {
        "id": "test-user-id-123",
        "email": "test@example.com",
        "email_verified": True,
        "created_at": "2026-03-12T00:00:00Z",
    }


@pytest.fixture
async def auth_client(mock_user):
    """Test client with mocked authentication.

    Bypasses the real get_current_user dependency so tests don't need
    a live Supabase connection.
    """
    from app.api.dependencies import get_current_user
    from app.models.auth import UserProfile

    async def mock_get_current_user():
        return UserProfile(**mock_user)

    app.dependency_overrides[get_current_user] = mock_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
```

- [ ] **Step 4: Update existing integration tests to use auth_client**

In `backend/tests/integration/test_api.py`, any tests that call `POST /api/tests/generate`, `GET /api/tests/{id}`, or `GET /api/tests/{id}/pdf` need to switch from `client` fixture to `auth_client` fixture.

Also add a test verifying that unauthenticated requests return 401:
```python
async def test_generate_requires_auth(client):
    """Protected endpoints return 401 without authentication."""
    response = await client.post(
        "/api/tests/generate",
        json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
    )
    assert response.status_code == 401


async def test_topics_is_public(client):
    """Topics endpoint remains public."""
    response = await client.get("/api/tests/topics")
    assert response.status_code == 200
```

- [ ] **Step 5: Run all tests**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/ -v --timeout=60`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/tests.py backend/app/api/pdf.py backend/tests/conftest.py backend/tests/integration/test_api.py
git commit -m "feat: protect generation and PDF endpoints with JWT auth dependency"
```

---

## Chunk 5: Frontend Auth — Types, API, Supabase Client (T108, T115)

### Task 20: Add auth types to frontend

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Add auth types**

Append to `frontend/src/types/index.ts`:
```typescript

// === Auth Types ===

export interface UserProfile {
  id: string;
  email: string;
  email_verified: boolean;
  created_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: UserProfile;
}

export interface AuthMessage {
  message: string;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add auth TypeScript interfaces"
```

---

### Task 21: Add auth functions and interceptors to api.ts

**Files:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: Add token storage helpers**

Add at the top of `frontend/src/services/api.ts` (after the imports, before the `client` definition):
```typescript
import type { TopicInfo, GenerateRequest, TestResponse, AuthResponse, AuthMessage, UserProfile } from "../types";

// === Token Storage ===

const TOKEN_KEYS = {
  access: "pg_access_token",
  refresh: "pg_refresh_token",
  expiresAt: "pg_token_expires_at",
} as const;

export function getStoredTokens() {
  return {
    accessToken: localStorage.getItem(TOKEN_KEYS.access),
    refreshToken: localStorage.getItem(TOKEN_KEYS.refresh),
    expiresAt: localStorage.getItem(TOKEN_KEYS.expiresAt),
  };
}

export function storeTokens(accessToken: string, refreshToken: string, expiresIn: number) {
  const expiresAt = String(Date.now() + expiresIn * 1000);
  localStorage.setItem(TOKEN_KEYS.access, accessToken);
  localStorage.setItem(TOKEN_KEYS.refresh, refreshToken);
  localStorage.setItem(TOKEN_KEYS.expiresAt, expiresAt);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEYS.access);
  localStorage.removeItem(TOKEN_KEYS.refresh);
  localStorage.removeItem(TOKEN_KEYS.expiresAt);
}

export function isTokenExpiringSoon(): boolean {
  const expiresAt = localStorage.getItem(TOKEN_KEYS.expiresAt);
  if (!expiresAt) return true;
  // Refresh if less than 2 minutes remaining
  return Date.now() > Number(expiresAt) - 2 * 60 * 1000;
}
```

- [ ] **Step 2: Add request interceptor for auth header**

Add after the `client` creation:
```typescript
// === Request Interceptor — attach Bearer token ===

client.interceptors.request.use((config) => {
  const { accessToken } = getStoredTokens();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});
```

- [ ] **Step 3: Add response interceptor with refresh mutex**

```typescript
// === TypeScript augmentation for retry flag ===
declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

// === Response Interceptor — refresh on 401 with mutex ===

let refreshPromise: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
  const { refreshToken } = getStoredTokens();
  if (!refreshToken) return false;

  try {
    const response = await axios.post("/api/auth/refresh", {
      refresh_token: refreshToken,
    }, { baseURL: client.defaults.baseURL });

    const data = response.data as AuthResponse;
    storeTokens(data.access_token, data.refresh_token, data.expires_in);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Mutex: only one refresh at a time
      if (!refreshPromise) {
        refreshPromise = attemptRefresh().finally(() => {
          refreshPromise = null;
        });
      }

      const success = await refreshPromise;
      if (success) {
        const { accessToken } = getStoredTokens();
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return client(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);
```

- [ ] **Step 4: Add auth API functions**

Add at the end of `api.ts`:
```typescript
// === Auth API ===

export async function authSignup(email: string, password: string): Promise<AuthMessage> {
  const response = await client.post("/auth/signup", { email, password });
  return response.data;
}

export async function authLogin(email: string, password: string): Promise<AuthResponse> {
  const response = await client.post("/auth/login", { email, password });
  return response.data;
}

export async function authRefresh(refreshToken: string): Promise<AuthResponse> {
  const response = await client.post("/auth/refresh", { refresh_token: refreshToken });
  return response.data;
}

export async function authLogout(): Promise<AuthMessage> {
  const response = await client.post("/auth/logout");
  return response.data;
}

export async function authMe(): Promise<UserProfile> {
  const response = await client.get("/auth/me");
  return response.data;
}

export async function authDeleteAccount(): Promise<AuthMessage> {
  const response = await client.delete("/auth/account");
  return response.data;
}

export async function authResendVerification(email: string): Promise<AuthMessage> {
  const response = await client.post("/auth/resend-verification", { email });
  return response.data;
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add auth API functions, request interceptor, 401 refresh with mutex"
```

---

### Task 22: Create Supabase JS client (OAuth only)

**Files:**
- Create: `frontend/src/services/supabase.ts`

- [ ] **Step 1: Create the Supabase client**

Create `frontend/src/services/supabase.ts`:
```typescript
/**
 * Minimal Supabase client — used ONLY for Google OAuth redirect flow.
 * All email/password auth goes through the backend /api/auth/* endpoints.
 */
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function signInWithGoogle() {
  return supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  });
}

export default supabase;
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/services/supabase.ts
git commit -m "feat: add minimal Supabase JS client for Google OAuth only"
```

---

## Chunk 6: Frontend Auth — Context, Components, Pages (T109–T116)

### Task 23: Create AuthContext

**Files:**
- Create: `frontend/src/context/AuthContext.tsx`

- [ ] **Step 1: Create the auth context and provider**

Create `frontend/src/context/AuthContext.tsx`:
```tsx
import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { UserProfile } from "../types";
import {
  authLogin,
  authSignup,
  authLogout,
  authMe,
  authDeleteAccount,
  authResendVerification,
  storeTokens,
  clearTokens,
  getStoredTokens,
} from "../services/api";
import { signInWithGoogle } from "../services/supabase";

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<string>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  deleteAccount: () => Promise<void>;
  resendVerification: (email: string) => Promise<string>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;

  // Validate stored tokens on mount
  useEffect(() => {
    async function checkAuth() {
      const { accessToken } = getStoredTokens();
      if (!accessToken) {
        setIsLoading(false);
        return;
      }

      try {
        const profile = await authMe();
        setUser(profile);
      } catch {
        // Token invalid or expired — interceptor will try refresh.
        // If refresh also fails, tokens are cleared automatically.
        clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    checkAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await authLogin(email, password);
    storeTokens(result.access_token, result.refresh_token, result.expires_in);
    setUser(result.user);
  }, []);

  const register = useCallback(async (email: string, password: string): Promise<string> => {
    const result = await authSignup(email, password);
    return result.message;
  }, []);

  const loginWithGoogleFn = useCallback(async () => {
    const { error } = await signInWithGoogle();
    if (error) {
      throw new Error(error.message);
    }
    // The actual redirect happens — user leaves the page.
    // On return, OAuthCallback page handles token extraction.
  }, []);

  const logoutFn = useCallback(async () => {
    try {
      await authLogout();
    } catch {
      // Even if the API call fails, clear local state
    }
    clearTokens();
    setUser(null);
  }, []);

  const deleteAccountFn = useCallback(async () => {
    await authDeleteAccount();
    clearTokens();
    setUser(null);
  }, []);

  const resendVerificationFn = useCallback(async (email: string): Promise<string> => {
    const result = await authResendVerification(email);
    return result.message;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        register,
        loginWithGoogle: loginWithGoogleFn,
        logout: logoutFn,
        deleteAccount: deleteAccountFn,
        resendVerification: resendVerificationFn,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/context/AuthContext.tsx
git commit -m "feat: add AuthContext with login, register, OAuth, logout, delete account"
```

---

### Task 24: Create auth UI components

**Files:**
- Create: `frontend/src/components/Auth/ProtectedRoute.tsx`
- Create: `frontend/src/components/Auth/GoogleOAuthButton.tsx`
- Create: `frontend/src/components/Auth/PasswordInput.tsx`
- Create: `frontend/src/components/Auth/EmailVerificationBanner.tsx`

- [ ] **Step 1: Create ProtectedRoute**

Create `frontend/src/components/Auth/ProtectedRoute.tsx`:
```tsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: "48px" }} role="status" aria-label="Loading">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  return <>{children}</>;
}
```

- [ ] **Step 2: Create GoogleOAuthButton**

Create `frontend/src/components/Auth/GoogleOAuthButton.tsx`:
```tsx
interface GoogleOAuthButtonProps {
  label?: string;
  onClick: () => void;
  disabled?: boolean;
}

export default function GoogleOAuthButton({
  label = "Sign in with Google",
  onClick,
  disabled = false,
}: GoogleOAuthButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      style={{
        width: "100%",
        padding: "10px 16px",
        border: "1px solid #ddd",
        borderRadius: "6px",
        backgroundColor: "#fff",
        cursor: disabled ? "not-allowed" : "pointer",
        fontSize: "0.95rem",
      }}
    >
      {label}
    </button>
  );
}
```

- [ ] **Step 3: Create PasswordInput**

Create `frontend/src/components/Auth/PasswordInput.tsx`:
```tsx
import { useState } from "react";

interface PasswordInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  minLength?: number;
  maxLength?: number;
}

export default function PasswordInput({
  id,
  label,
  value,
  onChange,
  error,
  minLength = 8,
  maxLength = 128,
}: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div style={{ marginBottom: "16px" }}>
      <label htmlFor={id} style={{ display: "block", marginBottom: "4px", fontWeight: 600 }}>
        {label}
      </label>
      <div style={{ position: "relative" }}>
        <input
          id={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          minLength={minLength}
          maxLength={maxLength}
          required
          aria-describedby={error ? `${id}-error` : undefined}
          style={{
            width: "100%",
            padding: "8px 40px 8px 8px",
            border: error ? "1px solid #d32f2f" : "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "1rem",
          }}
        />
        <button
          type="button"
          onClick={() => setVisible(!visible)}
          aria-label={visible ? "Hide password" : "Show password"}
          style={{
            position: "absolute",
            right: "8px",
            top: "50%",
            transform: "translateY(-50%)",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: "0.85rem",
            color: "#666",
          }}
        >
          {visible ? "Hide" : "Show"}
        </button>
      </div>
      {error && (
        <p id={`${id}-error`} role="alert" style={{ color: "#d32f2f", fontSize: "0.85rem", marginTop: "4px" }}>
          {error}
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create EmailVerificationBanner**

Create `frontend/src/components/Auth/EmailVerificationBanner.tsx`:
```tsx
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

interface EmailVerificationBannerProps {
  email: string;
}

export default function EmailVerificationBanner({ email }: EmailVerificationBannerProps) {
  const { resendVerification } = useAuth();
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  async function handleResend() {
    setStatus("sending");
    try {
      await resendVerification(email);
      setStatus("sent");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div
      role="status"
      aria-live="polite"
      style={{ padding: "12px", backgroundColor: "#f5f5f5", borderRadius: "6px", marginTop: "16px" }}
    >
      <p>Didn't receive the verification email?</p>
      {status === "idle" && (
        <button type="button" onClick={handleResend} style={{ color: "#1976d2", background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}>
          Click to resend
        </button>
      )}
      {status === "sending" && <p>Sending...</p>}
      {status === "sent" && <p>Verification email resent. Check your inbox.</p>}
      {status === "error" && <p style={{ color: "#d32f2f" }}>Failed to resend. Please try again later.</p>}
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Auth/
git commit -m "feat: add auth UI components (ProtectedRoute, GoogleOAuth, PasswordInput, EmailVerification)"
```

---

### Task 25: Create auth pages (Login, Register, Dashboard, VerifySuccess, OAuthCallback)

**Files:**
- Create: `frontend/src/pages/Login.tsx`
- Create: `frontend/src/pages/Register.tsx`
- Create: `frontend/src/pages/Dashboard.tsx`
- Create: `frontend/src/pages/VerifySuccess.tsx`
- Create: `frontend/src/pages/OAuthCallback.tsx`

These pages are substantial — each one should follow the design spec (Section 8.4) and accessibility requirements (Section 8.8). The implementer should build each page with:
- Proper `<label>` elements on all inputs
- `aria-live="polite"` for error/status messages
- Keyboard-accessible interactive elements
- 4.5:1 color contrast

Exact code for each page is implementation-specific and should reference the design spec. Key behaviors per page:

**Login.tsx:** Email/password form, GoogleOAuthButton, link to /register, error display with `aria-live`, redirect to dashboard or `?redirect` param on success. If already authenticated, redirect to /dashboard.

**Register.tsx:** Email/password/confirm form, "Min 8 characters" hint, GoogleOAuthButton, on success show verification message + EmailVerificationBanner. Link to /login. If already authenticated, redirect to /dashboard.

**Dashboard.tsx:** Welcome message, "Generate Test" button, "Sign Out" button, "Delete Account" with confirmation dialog (focus trap, Escape to dismiss).

**VerifySuccess.tsx:** "Email verified!" message, "Go to Login" link.

**OAuthCallback.tsx:** Extract tokens from Supabase URL hash, store in localStorage, redirect to /dashboard. Show error if extraction fails.

- [ ] **Step 1: Create all five page files following the design spec**

- [ ] **Step 2: Verify each page renders without errors**

Run: `cd PROBLEMGENERATOR/frontend && npm run build`
Expected: Build succeeds with no TypeScript errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Login.tsx frontend/src/pages/Register.tsx frontend/src/pages/Dashboard.tsx frontend/src/pages/VerifySuccess.tsx frontend/src/pages/OAuthCallback.tsx
git commit -m "feat: add auth pages (Login, Register, Dashboard, VerifySuccess, OAuthCallback)"
```

---

### Task 26: Update App.tsx and main.tsx with auth routes

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Update main.tsx to wrap in AuthProvider**

Replace `frontend/src/main.tsx`:
```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import ErrorBoundary from "./components/ErrorBoundary";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
);
```

- [ ] **Step 2: Update App.tsx with auth routes**

Replace `frontend/src/App.tsx`:
```tsx
import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Generate from "./pages/Generate";
import Preview from "./pages/Preview";
import VerifySuccess from "./pages/VerifySuccess";
import OAuthCallback from "./pages/OAuthCallback";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/auth/verify-success" element={<VerifySuccess />} />
        <Route path="/auth/callback" element={<OAuthCallback />} />

        {/* Protected routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/generate" element={<ProtectedRoute><Generate /></ProtectedRoute>} />
        <Route path="/preview/:testId" element={<ProtectedRoute><Preview /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App;
```

- [ ] **Step 3: Build to verify**

Run: `cd PROBLEMGENERATOR/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx frontend/src/main.tsx
git commit -m "feat: add auth routes, wrap app in AuthProvider, protect generate/preview"
```

---

## Chunk 7: Testing (T117–T120)

### Task 27: Backend auth integration tests

**Files:**
- Create: `backend/tests/integration/test_auth.py`

- [ ] **Step 1: Write integration tests**

Create `backend/tests/integration/test_auth.py`. Tests should mock the Supabase client to avoid needing a live connection. Key test cases:

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


Note: `asyncio_mode = "auto"` is already set in `pyproject.toml`, so async test methods do not need `@pytest.mark.asyncio` decorators.

class TestSignupEndpoint:
    async def test_signup_valid(self, client):
        """Valid signup returns 201 with success message."""

    async def test_signup_short_password(self, client):
        """Password under 8 chars returns 422 (Pydantic validation)."""

    async def test_signup_long_password(self, client):
        """Password over 128 chars returns 422."""

    async def test_signup_invalid_email(self, client):
        """Invalid email format returns 422."""

    async def test_signup_breached_password(self, client):
        """Breached password returns 400."""


class TestLoginEndpoint:
    async def test_login_valid(self, client):
        """Valid login returns 200 with tokens and user."""

    async def test_login_wrong_password(self, client):
        """Wrong password returns 401 with generic message."""

    async def test_login_nonexistent_email(self, client):
        """Nonexistent email returns 401 with same generic message."""


class TestProtectedEndpoints:
    async def test_generate_requires_auth(self, client):
        """POST /api/tests/generate without auth returns 401."""

    async def test_generate_with_auth(self, auth_client):
        """POST /api/tests/generate with auth returns 200."""

    async def test_topics_is_public(self, client):
        """GET /api/tests/topics is accessible without auth."""

    async def test_pdf_requires_auth(self, client):
        """GET /api/tests/{id}/pdf without auth returns 401."""


class TestMeEndpoint:
    async def test_me_with_auth(self, auth_client):
        """GET /api/auth/me returns user profile."""

    async def test_me_without_auth(self, client):
        """GET /api/auth/me without auth returns 401."""
```

- [ ] **Step 2: Run tests**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/integration/test_auth.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/integration/test_auth.py
git commit -m "test: add auth endpoint integration tests"
```

---

### Task 28: Frontend auth component tests

**Files:**
- Create: `frontend/src/__tests__/Login.test.tsx`
- Create: `frontend/src/__tests__/Register.test.tsx`
- Create: `frontend/src/__tests__/Dashboard.test.tsx`
- Create: `frontend/src/__tests__/ProtectedRoute.test.tsx`
- Create: `frontend/src/__tests__/AuthContext.test.tsx`

- [ ] **Step 1: Add auth MSW handlers**

Update `frontend/src/test/mocks/handlers.ts` — add handlers for auth endpoints:
```typescript
// Auth endpoints
http.post("/api/auth/login", async ({ request }) => {
  const body = await request.json() as { email: string; password: string };
  if (body.email === "test@example.com" && body.password === "validpass123") {
    return HttpResponse.json({
      access_token: "mock-access-token",
      refresh_token: "mock-refresh-token",
      expires_in: 900,
      token_type: "bearer",
      user: { id: "user-1", email: "test@example.com", email_verified: true, created_at: null },
    });
  }
  return HttpResponse.json({ detail: "Invalid email or password" }, { status: 401 });
}),

http.post("/api/auth/signup", () => {
  return HttpResponse.json(
    { message: "Account created. Please check your email to verify your account." },
    { status: 201 }
  );
}),

http.get("/api/auth/me", ({ request }) => {
  const auth = request.headers.get("Authorization");
  if (auth === "Bearer mock-access-token") {
    return HttpResponse.json({ id: "user-1", email: "test@example.com", email_verified: true, created_at: null });
  }
  return HttpResponse.json({ detail: "Not authenticated" }, { status: 401 });
}),

http.post("/api/auth/logout", () => {
  return HttpResponse.json({ message: "Logged out successfully" });
}),
```

- [ ] **Step 2: Write test files**

Each test file should test rendering, user interactions, and API calls using MSW mocks. Key patterns:
- Wrap components in `MemoryRouter` and `AuthProvider` for tests
- Use `userEvent` for form interactions
- Assert on screen text and navigation

- [ ] **Step 3: Run all frontend tests**

Run: `cd PROBLEMGENERATOR/frontend && npm test`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/__tests__/ frontend/src/test/mocks/handlers.ts
git commit -m "test: add frontend auth component and integration tests"
```

---

### Task 29: Backend E2E auth smoke test

**Files:**
- Create: `backend/tests/integration/test_auth_e2e.py`

- [ ] **Step 1: Write E2E test**

Create `backend/tests/integration/test_auth_e2e.py` — tests the full auth flow with mocked Supabase. Key test cases:

```python
class TestFullAuthFlow:
    async def test_signup_login_access_refresh_logout(self, client):
        """Full flow: signup → login → access protected → refresh → logout → 401."""

    async def test_delete_account_flow(self, client):
        """Delete flow: signup → login → delete → 401."""
```

Mock Supabase at the service level to simulate the full flow without a live connection.

- [ ] **Step 2: Run test**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/integration/test_auth_e2e.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/integration/test_auth_e2e.py
git commit -m "test: add E2E auth smoke tests (full signup-to-logout flow)"
```

---

### Task 30: Run full test suite and verify CI

**Files:** None (verification only)

- [ ] **Step 1: Run all backend tests**

Run: `cd PROBLEMGENERATOR/backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing --timeout=60`
Expected: All pass, coverage >= 80%

- [ ] **Step 2: Run all frontend tests**

Run: `cd PROBLEMGENERATOR/frontend && npm test`
Expected: All pass

- [ ] **Step 3: Run linters**

Run: `cd PROBLEMGENERATOR/backend && ruff check app/ && ruff format --check app/`
Run: `cd PROBLEMGENERATOR/frontend && npm run lint`
Expected: No errors

- [ ] **Step 4: Build frontend**

Run: `cd PROBLEMGENERATOR/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 5: Commit any fixes needed**

```bash
git add -A
git commit -m "fix: resolve lint/test issues from Layer 2 integration"
```

---

## Summary

| Chunk | Tasks | What It Covers |
|---|---|---|
| 1 | Tasks 1–6 | Frontend testing infrastructure (vitest, MSW, baseline tests) |
| 2 | Tasks 7–12 | Supabase setup (.env files, dependencies, config, user setup guide) |
| 3 | Tasks 13–15 | Backend auth models + auth service (HIBP + Supabase) |
| 4 | Tasks 16–19 | Backend auth dependency, endpoints, rate limiting, protect existing routes |
| 5 | Tasks 20–22 | Frontend auth types, API functions, interceptors, Supabase client |
| 6 | Tasks 23–26 | Frontend auth context, UI components, pages, routing |
| 7 | Tasks 27–30 | Backend + frontend auth tests, E2E smoke test, CI verification |

**Total: 30 implementation tasks across 7 chunks.**

Each chunk produces a working, committable state. Chunks 1-2 can run in parallel. Chunks 3-4 are sequential (backend). Chunks 5-6 are sequential (frontend) but can run in parallel with chunks 3-4. Chunk 7 depends on all previous chunks.
