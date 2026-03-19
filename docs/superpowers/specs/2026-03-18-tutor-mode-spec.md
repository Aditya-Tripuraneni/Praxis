# Feature Specification: Tutor Mode

**Date**: 2026-03-18
**Status**: Draft — Pending Approval
**Prerequisite**: Layers 1-3 complete, visual redesign ~80%

---

## 1. Database Schema

### 1.1 ALTER TABLE: subscriptions

```sql
ALTER TABLE subscriptions ADD COLUMN plan TEXT NOT NULL DEFAULT 'student';
```

No index needed — the column is read alongside existing queries (no standalone lookups by plan). The `DEFAULT 'student'` handles all existing rows automatically.

### 1.2 NEW TABLE: saved_tests

```sql
CREATE TABLE saved_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    test_name TEXT NOT NULL,
    config JSONB NOT NULL,
    seed INTEGER NOT NULL,
    questions JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT saved_tests_name_length CHECK (char_length(test_name) BETWEEN 1 AND 100)
);

CREATE INDEX idx_saved_tests_user_id ON saved_tests(user_id);

ALTER TABLE saved_tests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own saved tests" ON saved_tests
    FOR SELECT USING (auth.uid() = user_id);
```

**Storage:** ~11 KB per 50-question test (measured). Max 100 per tutor → ~1.1 MB per tutor.

**Column definitions:**
- `id`: UUID PK, auto-generated
- `user_id`: FK to auth.users, cascades on delete
- `test_name`: User-provided label (1-100 chars). NOT unique per user.
- `config`: JSONB — the `GenerateRequest` minus seed: `{ topics: string[], difficulty: string, count: number }`
- `seed`: INTEGER — the concrete seed used for generation (stored separately for clarity)
- `questions`: JSONB — full `QuestionResponse[]` frozen snapshot (decouples from template changes)
- `created_at`: Timestamp, auto-set

### 1.3 NEW ENV VARS

```env
# Replace STRIPE_PRICE_ID with:
STRIPE_STUDENT_PRICE_ID=price_...
STRIPE_TUTOR_PRICE_ID=price_...
```

---

## 2. Data Models

### 2.1 Backend — Pydantic (new/modified)

**`backend/app/models/billing.py` — modified:**

```python
from typing import Literal
from datetime import datetime
from pydantic import BaseModel

class CheckoutSessionRequest(BaseModel):
    plan: Literal["student", "tutor"]

class CheckoutSessionResponse(BaseModel):
    url: str

class SubscriptionStatus(BaseModel):
    status: str  # 'active' | 'past_due' | 'expired' | 'inactive'
    is_active: bool
    current_period_end: datetime | None = None
    plan: str | None = None  # NEW: 'student' | 'tutor' | None
```

**`backend/app/models/saved_tests.py` — new file:**

```python
from datetime import datetime
from pydantic import BaseModel, Field

class SaveTestRequest(BaseModel):
    test_name: str = Field(min_length=1, max_length=100)
    config: dict  # GenerateRequest as dict (topics, difficulty, count)
    seed: int
    questions: list[dict]  # QuestionResponse[] as dicts

class RenameTestRequest(BaseModel):
    test_name: str = Field(min_length=1, max_length=100)

class SavedTestResponse(BaseModel):
    id: str
    test_name: str
    config: dict
    seed: int
    questions: list[dict]
    created_at: datetime

class SavedTestSummary(BaseModel):
    """Lightweight version for list endpoint (no questions)."""
    id: str
    test_name: str
    config: dict
    seed: int
    question_count: int
    created_at: datetime
```

### 2.2 Frontend — TypeScript (new/modified)

**`frontend/src/types/index.ts` — additions:**

```typescript
// Modified
export interface SubscriptionStatus {
  status: string;
  is_active: boolean;
  current_period_end: string | null;
  plan: string | null;  // NEW: 'student' | 'tutor' | null
}

// New
export interface SavedTestSummary {
  id: string;
  test_name: string;
  config: GenerateRequest;
  seed: number;
  question_count: number;
  created_at: string;
}

export interface SavedTest {
  id: string;
  test_name: string;
  config: GenerateRequest;
  seed: number;
  questions: QuestionResponse[];
  created_at: string;
}
```

---

## 3. API Endpoints

### 3.1 MODIFIED: `POST /api/billing/create-checkout-session`

**Change:** Now accepts a request body with `plan` field.

| Field | Value |
|-------|-------|
| Method | POST |
| Path | `/api/billing/create-checkout-session` |
| Auth | `get_current_user` |
| Rate limit | 10/hour |
| Request body | `{ "plan": "student" \| "tutor" }` |
| Response | `{ "url": "https://checkout.stripe.com/..." }` |

**Backend logic change:** Map `plan` → `settings.stripe_student_price_id` or `settings.stripe_tutor_price_id`. Store `plan` in Checkout Session metadata and in the `subscriptions` table row.

### 3.2 MODIFIED: `GET /api/billing/subscription-status`

**Change:** Response now includes `plan` field.

| Field | Value |
|-------|-------|
| Response | `{ "status": "active", "is_active": true, "current_period_end": "...", "plan": "tutor" }` |

**Backend logic change:** `get_subscription_status()` reads the `plan` column from the `subscriptions` table and includes it in the return dict.

### 3.3 NEW: `POST /api/saved-tests`

Save a test configuration + questions.

| Field | Value |
|-------|-------|
| Method | POST |
| Path | `/api/saved-tests` |
| Auth | `require_tutor_subscription` (new dependency) |
| Rate limit | 30/minute |
| Request body | `SaveTestRequest` (see model above) |
| Response (201) | `SavedTestSummary` |
| Errors | 400: name too short/long. 403: not a tutor. 409: limit reached (100). |

**Example request:**
```json
{
  "test_name": "Weekly Algebra Quiz",
  "config": { "topics": ["algebra"], "difficulty": "medium", "count": 20 },
  "seed": 1847293,
  "questions": [
    { "id": 1, "question_latex": "Solve for $x$: $3x + 7 = 22$", "answer_latex": "$x = 5$", "topic": "algebra", "difficulty": "medium", "subtopic": "linear_equations", "solution_steps": ["$3x + 7 = 22$", "$3x = 15$", "$x = 5$"] }
  ]
}
```

**Example response (201):**
```json
{
  "id": "a1b2c3d4-...",
  "test_name": "Weekly Algebra Quiz",
  "config": { "topics": ["algebra"], "difficulty": "medium", "count": 20 },
  "seed": 1847293,
  "question_count": 20,
  "created_at": "2026-03-18T14:30:00Z"
}
```

### 3.4 NEW: `GET /api/saved-tests`

List all saved tests for the current tutor (lightweight — no questions).

| Field | Value |
|-------|-------|
| Method | GET |
| Path | `/api/saved-tests` |
| Auth | `require_tutor_subscription` |
| Rate limit | 30/minute |
| Response | `SavedTestSummary[]` (ordered by `created_at` desc) |

### 3.5 NEW: `GET /api/saved-tests/{id}/replay`

Get the full saved test with stored questions (for replay).

| Field | Value |
|-------|-------|
| Method | GET |
| Path | `/api/saved-tests/{id}/replay` |
| Auth | `require_tutor_subscription` |
| Rate limit | 20/minute |
| Response | `SavedTestResponse` (includes full `questions` array) |
| Errors | 404: not found or not owned by user. |

**Side effect:** Records stats + updates streak (same as regular generation).

### 3.6 NEW: `PATCH /api/saved-tests/{id}`

Rename a saved test.

| Field | Value |
|-------|-------|
| Method | PATCH |
| Path | `/api/saved-tests/{id}` |
| Auth | `require_tutor_subscription` |
| Rate limit | 30/minute |
| Request body | `{ "test_name": "New Name" }` |
| Response | `SavedTestSummary` (updated) |
| Errors | 400: name validation. 404: not found / not owned. |

### 3.7 NEW: `DELETE /api/saved-tests/{id}`

Delete a saved test.

| Field | Value |
|-------|-------|
| Method | DELETE |
| Path | `/api/saved-tests/{id}` |
| Auth | `require_tutor_subscription` |
| Rate limit | 30/minute |
| Response (200) | `{ "message": "Saved test deleted" }` |
| Errors | 404: not found / not owned. |

---

## 4. Stripe Changes

### 4.1 New Env Vars

```python
# backend/app/config.py — replace stripe_price_id with:
stripe_student_price_id: str = ""
stripe_tutor_price_id: str = ""
```

The old `stripe_price_id` is removed. The `BillingService.__init__` validation updates accordingly.

### 4.2 Price Mapping

```python
# In billing.py service
PLAN_PRICES: dict[str, str] = {
    "student": settings.stripe_student_price_id,
    "tutor": settings.stripe_tutor_price_id,
}
```

### 4.3 Checkout Flow Change

`create_checkout_session(user_id, email, plan)`:
1. Look up price_id from `PLAN_PRICES[plan]`
2. Store `plan` in the subscription row (column value)
3. Store `plan` in Stripe Checkout Session metadata
4. Create session with the mapped price_id

### 4.4 Webhook Change — `_handle_checkout_completed`

After activating the subscription, also set the `plan` column:

```python
plan = session_data.get("metadata", {}).get("plan", "student")
# Include in the upsert: "plan": plan
```

### 4.5 Webhook Change — `_handle_subscription_updated`

When Stripe updates a subscription, derive the plan from the price_id on the subscription items:

```python
items = sub_data.get("items", {}).get("data", [])
if items:
    price_id = items[0].get("price", {}).get("id")
    if price_id == settings.stripe_tutor_price_id:
        plan = "tutor"
    else:
        plan = "student"
    # Include in the update: "plan": plan
```

This handles edge cases where a subscription is modified externally in the Stripe Dashboard.

### 4.6 Your Actions (Stripe Dashboard)

**When:** At the start of Phase 4 implementation, before any code is deployed.

**Steps (I will provide context7-sourced instructions at that time):**
1. Log into Stripe Dashboard (test mode)
2. Navigate to Products → Create Product
3. Name: "ProblemGenerator Tutor", Description: "Tutor plan with saved tests"
4. Add Price: $12.99 CAD, Recurring, Monthly
5. Copy the new `price_id` (starts with `price_`)
6. Rename existing product to "ProblemGenerator Student" (for clarity)
7. Copy the existing Student `price_id`
8. Update `backend/.env`:
   - Remove: `STRIPE_PRICE_ID=...`
   - Add: `STRIPE_STUDENT_PRICE_ID=price_existing...`
   - Add: `STRIPE_TUTOR_PRICE_ID=price_new...`

### 4.7 Your Actions (Supabase Dashboard)

**Steps:**
1. Open Supabase Dashboard → SQL Editor
2. Run: `ALTER TABLE subscriptions ADD COLUMN plan TEXT NOT NULL DEFAULT 'student';`
3. Run: The full `CREATE TABLE saved_tests` SQL from Section 1.2
4. Verify both in Table Editor

---

## 5. Frontend Changes

### 5.1 `SubscriptionContext.tsx` — Modified

- `SubscriptionStatus` now has `plan: string | null`
- Context exposes `plan` alongside `isSubscribed`
- `subscribe()` changes to `subscribe(plan: 'student' | 'tutor')`
- `isTutor` derived: `plan === 'tutor' && isSubscribed`

```typescript
interface SubscriptionContextType {
  subscription: SubscriptionStatus | null;
  isSubscribed: boolean;
  isLoading: boolean;
  plan: string | null;        // NEW
  isTutor: boolean;           // NEW: convenience derived
  subscribe: (plan: 'student' | 'tutor') => Promise<void>;  // CHANGED: accepts plan
  cancelSub: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}
```

### 5.2 `api.ts` — Modified/New Functions

```typescript
// MODIFIED — now accepts plan parameter
export async function createCheckoutSession(plan: 'student' | 'tutor'): Promise<CheckoutSessionResponse> {
  const response = await apiClient.post("/billing/create-checkout-session", { plan });
  return response.data;
}

// NEW — saved tests CRUD
export async function getSavedTests(): Promise<SavedTestSummary[]> { ... }
export async function saveTest(data: SaveTestRequest): Promise<SavedTestSummary> { ... }
export async function replaySavedTest(id: string): Promise<SavedTest> { ... }
export async function renameSavedTest(id: string, test_name: string): Promise<SavedTestSummary> { ... }
export async function deleteSavedTest(id: string): Promise<void> { ... }
```

### 5.3 `Dashboard.tsx` — Modified

**Unsubscribed view:** Replace single promo card with two-plan comparison (as in mockup 01):
- Side-by-side Student/Tutor cards
- "Choose Student" → `subscribe('student')`
- "Choose Tutor" → `subscribe('tutor')`

**Subscribed view — tutor only:** Add "SAVED TESTS" section between quick action card and subscription card:
- Search input (client-side filter by name)
- List of saved tests (name, config metadata pills, date, Replay link, Delete button)
- Count display ("N of 100")
- Click "Replay" → navigate to `/saved-test/{id}`

**Subscribed view — student:** No saved tests section. Identical to current dashboard except:
- Banner shows "STUDENT PLAN" badge
- Subscription card shows "Active — Student Plan"

**Both plans:** Subscription card shows plan name ("Active — Tutor Plan" or "Active — Student Plan").

### 5.4 `Preview.tsx` — Modified

**Tutor only:** Add "Save Test" ghost button in summary bar (left of "Download PDF").
- Clicking opens a modal with name input
- On save: `POST /api/saved-tests` with `{ test_name, config, seed, questions }` from current `test` state
- Success toast at bottom center
- Button hidden for students (check `isTutor` from SubscriptionContext)

**Requires seed in TestResponse:** The preview page needs access to `test.config.seed` to pass to the save endpoint. This is available after the seed-always-assigned change to `generation_service.py`.

### 5.5 New Route: `/saved-test/:id`

**New page:** `SavedTestReplay.tsx` (or reuse Preview with a flag)

- Fetches `GET /api/saved-tests/{id}/replay`
- Renders using the same QuestionList component as Preview
- Summary bar shows "Saved Test: {test_name}" instead of "Test Preview"
- Same controls: include answers, include solutions, download PDF, timer
- No "Save Test" button (it's already saved)
- "Back to Dashboard" link instead of "Generate New Test"

**Implementation choice:** Create a thin wrapper that fetches the saved test, constructs a `TestResponse`-shaped object from the stored data, and passes it to the existing Preview rendering logic. This avoids duplicating the QuestionList/QuestionCard components.

### 5.6 `App.tsx` — Modified

Add route:
```tsx
<Route path="/saved-test/:id" element={
  <ProtectedRoute>
    <SubscriptionGate>
      <SavedTestReplay />
    </SubscriptionGate>
  </ProtectedRoute>
} />
```

---

## 6. Backend Changes (Detail)

### 6.1 `backend/app/config.py` — Modified

```python
# Remove:
stripe_price_id: str = ""

# Add:
stripe_student_price_id: str = ""
stripe_tutor_price_id: str = ""
```

### 6.2 `backend/app/api/dependencies.py` — New Dependency

```python
async def require_tutor_subscription(
    auth: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Require authentication + active subscription + tutor plan."""
    from app.services.billing import billing_service

    status = await billing_service.get_subscription_status(auth.profile.id)
    if not status.get("is_active", False):
        raise HTTPException(status_code=403, detail="Active subscription required")
    if status.get("plan") != "tutor":
        raise HTTPException(status_code=403, detail="Tutor plan required")
    return auth
```

### 6.3 `backend/app/services/saved_tests.py` — New Service

```python
class SavedTestsService:
    """CRUD operations for saved test configurations."""

    MAX_SAVED_TESTS = 100

    async def save_test(self, user_id: str, test_name: str, config: dict, seed: int, questions: list[dict]) -> dict:
        """Save a test. Enforces per-user limit."""
        count = await self._count_user_tests(user_id)
        if count >= self.MAX_SAVED_TESTS:
            raise SavedTestLimitError("Maximum of 100 saved tests reached")
        # Insert row, return summary (without questions)

    async def list_tests(self, user_id: str) -> list[dict]:
        """List all saved tests for a user (no questions, ordered by created_at desc)."""
        # SELECT id, test_name, config, seed, created_at FROM saved_tests WHERE user_id = ? ORDER BY created_at DESC

    async def get_test(self, test_id: str, user_id: str) -> dict | None:
        """Get full saved test including questions. Returns None if not found/not owned."""

    async def rename_test(self, test_id: str, user_id: str, new_name: str) -> dict | None:
        """Rename a saved test. Returns updated summary or None."""

    async def delete_test(self, test_id: str, user_id: str) -> bool:
        """Delete a saved test. Returns True if deleted, False if not found."""

    async def _count_user_tests(self, user_id: str) -> int:
        """Count saved tests for a user."""
```

All methods use `asyncio.to_thread()` for Supabase calls (same pattern as StatsService).

### 6.4 `backend/app/services/generation_service.py` — Modified

**Always assign a concrete seed:**

```python
import random as _random

def generate(self, request: GenerateRequest, user_id: str = "") -> TestResponse:
    # Always assign a concrete seed for reproducibility
    actual_seed = request.seed if request.seed is not None else _random.randint(0, 2**31 - 1)

    topics, subtopics = _parse_topic_selections(request.topics)
    difficulty = Difficulty(request.difficulty)

    config = GenerationConfig(
        topics=topics,
        difficulty=difficulty,
        count=request.count,
        seed=actual_seed,  # Always concrete
        subtopics=subtopics,
    )

    problems = generate_test(config, registry)

    # ... (rest unchanged)

    # Store the actual seed in the response config
    response = TestResponse(
        test_id=test_id,
        questions=questions,
        created_at=datetime.now(timezone.utc),
        config=GenerateRequest(
            topics=request.topics,
            difficulty=request.difficulty,
            count=request.count,
            seed=actual_seed,  # Concrete seed in response
        ),
    )
    # ...
```

### 6.5 `backend/app/services/billing.py` — Modified

Key changes:
- `create_checkout_session(user_id, email, plan)` — accepts `plan` parameter, maps to price_id
- `get_subscription_status()` — returns `plan` field from DB
- `_handle_checkout_completed()` — reads `plan` from session metadata, stores in DB
- `_handle_subscription_updated()` — derives `plan` from price_id in subscription items

### 6.6 `backend/app/api/saved_tests.py` — New Router

```python
router = APIRouter(prefix="/api/saved-tests", tags=["saved-tests"])

@router.post("", status_code=201, response_model=SavedTestSummary)
@router.get("", response_model=list[SavedTestSummary])
@router.get("/{test_id}/replay", response_model=SavedTestResponse)
@router.patch("/{test_id}", response_model=SavedTestSummary)
@router.delete("/{test_id}")
```

All endpoints use `require_tutor_subscription` dependency.

The replay endpoint also records stats + streak:

```python
@router.get("/{test_id}/replay", response_model=SavedTestResponse)
async def replay_saved_test(request, test_id, auth):
    test = await saved_tests_service.get_test(test_id, auth.profile.id)
    if not test:
        raise HTTPException(404)

    # Record stats (non-blocking)
    try:
        topic_dist = Counter(q["topic"] for q in test["questions"])
        await stats_service.record_generation(auth.profile.id, len(test["questions"]), dict(topic_dist))
        await stats_service.update_streak(auth.profile.id)
    except Exception:
        logger.warning("Failed to record replay stats")

    return SavedTestResponse(**test)
```

### 6.7 `backend/app/main.py` — Modified

Register the new router:

```python
from app.api.saved_tests import router as saved_tests_router
app.include_router(saved_tests_router)
```

---

## 7. Migration Strategy

### 7.1 Existing Users

All existing users are students. The `ALTER TABLE subscriptions ADD COLUMN plan TEXT NOT NULL DEFAULT 'student'` handles this automatically. No data migration needed.

### 7.2 Existing Subscriptions

All existing active subscriptions map to `plan = 'student'`. The default value ensures this. The existing `STRIPE_PRICE_ID` becomes `STRIPE_STUDENT_PRICE_ID` — same value, just renamed.

### 7.3 Env Var Transition

The old `STRIPE_PRICE_ID` is removed from `config.py`. The `.env` file is updated:
- Remove: `STRIPE_PRICE_ID=price_xxx`
- Add: `STRIPE_STUDENT_PRICE_ID=price_xxx` (same value)
- Add: `STRIPE_TUTOR_PRICE_ID=price_new` (new Tutor price)

### 7.4 Deployment Order

1. **Supabase:** Run ALTER TABLE + CREATE TABLE (you, manually)
2. **Stripe:** Create Tutor product + price (you, manually)
3. **Backend:** Deploy with new env vars + code changes
4. **Frontend:** Deploy with UI changes

Backend and frontend can deploy simultaneously since the new endpoints are additive (no breaking changes to existing endpoints).

---

## 8. Testing Plan

### 8.1 Backend Unit Tests

**`tests/unit/services/test_saved_tests_service.py`:**
1. `test_save_test_creates_row` — Mock Supabase insert, verify correct data
2. `test_save_test_limit_enforced` — Mock count=100, verify SavedTestLimitError raised
3. `test_list_tests_returns_summaries` — Verify questions are NOT included in list response
4. `test_get_test_returns_full_data` — Verify questions ARE included
5. `test_get_test_wrong_user_returns_none` — IDOR prevention
6. `test_rename_test_updates_name` — Verify UPDATE called with new name
7. `test_delete_test_removes_row` — Verify DELETE called

**`tests/unit/services/test_billing_service.py` (additions):**
8. `test_checkout_session_student_uses_student_price` — Verify correct price_id
9. `test_checkout_session_tutor_uses_tutor_price` — Verify correct price_id
10. `test_subscription_status_includes_plan` — Verify plan field in response
11. `test_checkout_webhook_stores_plan_from_metadata` — Verify plan column set

### 8.2 Backend Integration Tests

**`tests/integration/test_saved_tests.py`:**
12. `test_save_requires_tutor_subscription` — Student user → 403
13. `test_save_requires_auth` — No token → 401
14. `test_save_and_list` — Save a test, list tests, verify it appears
15. `test_save_and_replay_returns_identical_questions` — **Critical:** Save a test, replay it, verify the questions array is byte-for-byte identical to what was saved
16. `test_replay_records_stats` — Replay a test, check stats endpoint shows incremented counts
17. `test_rename_saved_test` — Rename, verify new name in list
18. `test_delete_saved_test` — Delete, verify absent from list
19. `test_cannot_access_other_users_saved_test` — IDOR prevention: save as user A, replay as user B → 404
20. `test_save_limit_100` — Save 100 tests, attempt 101st → 409

**`tests/integration/test_billing.py` (additions):**
21. `test_checkout_with_tutor_plan` — Create session with plan="tutor", verify Stripe price_id
22. `test_subscription_status_returns_plan` — After checkout webhook, status includes plan field

### 8.3 Frontend Tests

**`src/__tests__/Dashboard.test.tsx` (additions):**
23. `test_tutor_dashboard_shows_saved_tests_section` — Mock plan="tutor", verify "SAVED TESTS" section renders
24. `test_student_dashboard_hides_saved_tests` — Mock plan="student", verify no saved tests section
25. `test_unsubscribed_shows_plan_comparison` — Mock isSubscribed=false, verify both plan cards render

**`src/__tests__/Preview.test.tsx` (additions):**
26. `test_tutor_sees_save_button` — Mock isTutor=true, verify "Save Test" button renders
27. `test_student_does_not_see_save_button` — Mock isTutor=false, verify no save button

**`src/__tests__/api.test.ts` (additions):**
28. `test_createCheckoutSession_sends_plan` — Verify plan parameter sent in request body
29. `test_getSavedTests_returns_summaries` — Runtime validator check
30. `test_replaySavedTest_returns_full_questions` — Runtime validator check

### 8.4 Edge Cases

31. **Replay after account deletion cascade:** Saved tests are deleted by `ON DELETE CASCADE` — no orphan data
32. **Subscription lapses:** Tutor whose subscription expires → saved tests endpoints return 403 → tests remain in DB → re-subscribing as tutor restores access
33. **Re-subscribe as student after being tutor:** Saved tests remain in DB but endpoints return 403 (student plan). Data preserved in case they upgrade back.

---

## 9. Scope Boundary

### IN Scope
- `plan` column on subscriptions table
- `saved_tests` table with JSONB questions snapshot
- Two Stripe price IDs (student $5 CAD, tutor $12.99 CAD)
- Plan selection on Dashboard (unsubscribed view)
- Saved tests section on Dashboard (tutor only)
- Save Test button on Preview page (tutor only)
- Replay route `/saved-test/:id`
- `require_tutor_subscription` dependency
- Stats recording on replay
- 100 saved test limit per tutor
- Client-side search/filter on saved tests
- Banner plan badge on Dashboard
- Always-concrete seed in generation_service

### OUT of Scope
- Stripe proration / in-app plan upgrade-downgrade (cancel + re-subscribe for MVP)
- Saved test folders, tags, or categories
- Sharing saved tests between users
- Server-side search / full-text indexing
- Template version tracking / determinism verification
- Saved test export/import
- Tutor-student relationship management
- Test assignment / class features

### FUTURE
- In-app plan upgrade with Stripe proration
- Saved test folders or tags for organization
- Template version hash stored at save time for drift detection
- Sharing saved tests via link
- Bulk operations (delete multiple, export all)

---

## 10. Files Affected Summary

### Backend — New Files
- `backend/app/models/saved_tests.py`
- `backend/app/services/saved_tests.py`
- `backend/app/api/saved_tests.py`
- `backend/tests/unit/services/test_saved_tests_service.py`
- `backend/tests/integration/test_saved_tests.py`

### Backend — Modified Files
- `backend/app/config.py` — new price env vars
- `backend/app/services/billing.py` — plan-aware checkout, webhook, status
- `backend/app/api/billing.py` — accepts plan in checkout request
- `backend/app/api/dependencies.py` — `require_tutor_subscription`
- `backend/app/models/billing.py` — `CheckoutSessionRequest`, `SubscriptionStatus.plan`
- `backend/app/services/generation_service.py` — always-assign seed
- `backend/app/main.py` — register saved_tests router
- `backend/tests/unit/services/test_billing_service.py` — plan-aware tests
- `backend/tests/integration/test_billing.py` — plan-aware tests

### Frontend — New Files
- `frontend/src/pages/SavedTestReplay.tsx`

### Frontend — Modified Files
- `frontend/src/types/index.ts` — new types
- `frontend/src/services/api.ts` — new functions, modified createCheckoutSession
- `frontend/src/context/SubscriptionContext.tsx` — expose plan, isTutor
- `frontend/src/pages/Dashboard.tsx` — plan comparison, saved tests section
- `frontend/src/pages/Preview.tsx` — save test button + modal
- `frontend/src/App.tsx` — new route
- `frontend/src/__tests__/Dashboard.test.tsx` — new tests
- `frontend/src/__tests__/Preview.test.tsx` — new tests
- `frontend/src/__tests__/api.test.ts` — new tests

### Configuration
- `backend/.env` — replace `STRIPE_PRICE_ID` with two new vars
- `backend/.env.example` — same
- `docker-compose.yml` — update env vars
