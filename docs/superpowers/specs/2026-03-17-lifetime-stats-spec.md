# Spec: Lifetime Stats + Topic Mastery Map

**Date**: 2026-03-17
**Status**: Approved
**Prerequisite**: Active subscription + test generation flow working (Layers 1-3 complete)

---

## Overview

Track the cumulative number of tests and questions a user has generated, broken down by math topic. Display on the Dashboard as real numbers (replacing the current static "34 Templates / 5 Topics / 3 Levels" row) plus a visual topic mastery map with colored progress bars. This creates investment psychology — a user who sees "247 questions across 18 tests" feels the subscription is justified. The topic breakdown doubles as a study gap detector: under-practiced topics are visually obvious.

---

## Database Schema

**Table:** `user_stats`

```sql
CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tests_generated INTEGER NOT NULL DEFAULT 0,
    questions_generated INTEGER NOT NULL DEFAULT 0,
    topic_counts JSONB NOT NULL DEFAULT '{}',
    streak_current INTEGER NOT NULL DEFAULT 0,
    streak_best INTEGER NOT NULL DEFAULT 0,
    last_practice_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own stats" ON user_stats
    FOR SELECT USING (auth.uid() = user_id);
```

**Design decisions:**
- **One row per user** (not per user+topic): single read per dashboard load, topic counts stored as JSONB. Simpler upsert, no join needed.
- **`topic_counts` JSONB format:** `{"algebra": 47, "functions": 23, "trigonometry": 15, "calculus": 8, "geometry": 12}`. Keys are Topic enum values (lowercase strings). Missing keys = 0.
- **Streak columns included** (for Practice Streak feature) with safe defaults: `streak_current=0`, `streak_best=0`, `last_practice_date=NULL`. Lifetime Stats ignores these columns. Practice Streak can ship independently.
- **Row creation:** First row is upserted on the user's first test generation. No row = no stats (Dashboard shows zeros).
- **CASCADE on user deletion:** Row deleted automatically when auth user is deleted.
- **RLS:** Users can SELECT their own stats. Backend uses service_role key for writes (INSERT/UPDATE).

---

## Backend Service

**New file:** `backend/app/services/stats.py`

```python
class StatsService:
    def __init__(self) -> None:
        self._supabase = _create_service_client()  # same pattern as billing

    async def record_generation(
        self, user_id: str, question_count: int, topic_counts: dict[str, int]
    ) -> None:
        """Record a test generation. Non-blocking -- errors logged, not raised.

        1. Fetch existing row (or None)
        2. Increment tests_generated + 1, questions_generated + question_count
        3. Merge topic_counts: add new counts to existing counts per topic
        4. Upsert row
        5. On error: log warning, do not raise
        """

    async def get_user_stats(self, user_id: str) -> dict:
        """Get stats for a user. Returns defaults if no row exists.

        SELECT * FROM user_stats WHERE user_id = ?
        If no row: return {tests_generated: 0, questions_generated: 0, topic_counts: {}}
        """
```

**Topic count computation:** Count questions per topic from the actual `TestResponse.questions` list. Each `QuestionResponse` has a `.topic` field. Exact count via `Counter(q.topic for q in response.questions)`.

**Service instantiation:** Module-level singleton `stats_service = StatsService()` (same pattern as `generation_service`, `billing_service`).

**Error handling:** `record_generation` wraps everything in try/except, logs warning on failure. The generation endpoint must never fail because of stats.

---

## API Endpoints

### `GET /api/stats/me` -- Get user's lifetime stats

| Field | Value |
|---|---|
| Method | GET |
| Path | `/api/stats/me` |
| Rate limit | 30/minute |
| Auth | `get_current_user` (not subscription-gated) |
| Response model | `UserStatsResponse` |

**Pydantic response model** (`backend/app/models/stats.py`):
```python
class UserStatsResponse(BaseModel):
    tests_generated: int = 0
    questions_generated: int = 0
    topic_counts: dict[str, int] = Field(default_factory=dict)
    streak_current: int = 0
    streak_best: int = 0
    is_active_today: bool = False
```

**Example response:**
```json
{
  "tests_generated": 18,
  "questions_generated": 247,
  "topic_counts": {
    "algebra": 94,
    "trigonometry": 62,
    "calculus": 38,
    "functions": 31,
    "geometry": 22
  },
  "streak_current": 0,
  "streak_best": 0,
  "is_active_today": false
}
```

### Recording hook -- in existing generate endpoint

Stats are recorded inside `POST /api/tests/generate` in `tests.py`, AFTER successful generation:

```python
@router.post("/generate", response_model=TestResponse)
async def generate_test(request, body, auth):
    response = generation_service.generate(body, user_id=auth.profile.id)

    # Record stats (non-blocking)
    try:
        topic_distribution = Counter(q.topic for q in response.questions)
        await stats_service.record_generation(
            user_id=auth.profile.id,
            question_count=len(response.questions),
            topic_counts=dict(topic_distribution),
        )
    except Exception:
        logger.warning("Failed to record generation stats", exc_info=True)

    return response
```

Note: The endpoint is currently sync (`def generate_test`). It must become `async def` to use `await`.

---

## Frontend Types

**New in `types/index.ts`:**
```typescript
export interface UserStats {
  tests_generated: number;
  questions_generated: number;
  topic_counts: Record<string, number>;
  streak_current: number;
  streak_best: number;
  is_active_today: boolean;
}
```

---

## Frontend API Client

**New in `api.ts`:**
```typescript
export async function getUserStats(): Promise<UserStats> {
  const response = await apiClient.get("/stats/me");
  return validateUserStats(response.data);
}

function validateUserStats(data: unknown): UserStats {
  if (!data || typeof data !== "object") throw new Error("Invalid stats response");
  const d = data as Record<string, unknown>;
  if (typeof d.tests_generated !== "number") throw new Error("Invalid stats");
  if (typeof d.questions_generated !== "number") throw new Error("Invalid stats");
  return d as UserStats;
}
```

---

## Frontend Context

**New file:** `frontend/src/context/StatsContext.tsx`

Following `SubscriptionContext` pattern exactly:

```typescript
interface StatsContextType {
  stats: UserStats | null;
  isLoading: boolean;
  refreshStats: () => Promise<void>;
}
```

- Fetches `getUserStats()` on mount when `isAuthenticated && !authLoading`
- Exposes `stats`, `isLoading`, `refreshStats`
- Custom hook: `useStats()`
- `refreshStats()` called after test generation completes

---

## Frontend UI

### Stats summary cards (replace current static row)

The current static row at Dashboard lines 326-339 shows "34 Templates, 5 Topics, 3 Levels". Replace with real user data:

| Card | Icon (Lucide) | Number | Label |
|---|---|---|---|
| Card 1 | `FileText` (20px, primary-500) | `stats.tests_generated` | Tests Generated |
| Card 2 | `BookOpen` (20px, primary-500) | `stats.questions_generated` | Questions Practiced |

Same `statsRowStyle` and `statCardStyle` from current Dashboard. If `stats` is null or loading, show "--" as placeholder.

### Topic mastery map (new card below stats row)

```
+----------------------------------------------------+
|  PRACTICE DISTRIBUTION              (section label) |
|                                                     |
|  [============================]  Algebra         94 |
|  [==================]           Trigonometry     62 |
|  [=============]                Calculus         38 |
|  [===========]                  Functions        31 |
|  [========]                     Geometry         22 |
+----------------------------------------------------+
```

Each row:
- Colored bar: width = `count / maxCount * 100%`, min-width 4px
- Bar color: `var(--color-topic-{name})` (decorative variant)
- Bar background: `var(--color-stone-100)`
- Bar height: 8px, border-radius: `var(--radius-full)`
- Topic name: `var(--color-topic-{name}-text)`
- Count: right-aligned, `font-weight: 700`
- Sorted by count descending

**Zero state:** "Generate your first test to see your practice breakdown"

**Accessibility:**
- Each bar: `role="meter"`, `aria-valuenow={count}`, `aria-valuemin={0}`, `aria-valuemax={maxCount}`, `aria-label="{Topic}: {count} questions"`
- Section: `aria-label="Practice distribution by topic"`

**Topic color mapping:**
```typescript
const TOPIC_COLORS: Record<string, string> = {
  algebra: 'var(--color-topic-algebra)',
  functions: 'var(--color-topic-functions)',
  geometry: 'var(--color-topic-geometry)',
  trigonometry: 'var(--color-topic-trigonometry)',
  calculus: 'var(--color-topic-calculus)',
};
```

---

## Data Flow

### Recording (test generation):
1. User clicks "Generate" on Generate page
2. `POST /api/tests/generate` -> `tests.py:generate_test()`
3. `generation_service.generate()` returns `TestResponse`
4. `Counter(q.topic for q in response.questions)` computes topic distribution
5. `stats_service.record_generation(user_id, count, topic_counts)` -> upserts `user_stats` row
6. Return `TestResponse` to frontend (stats recording is fire-and-forget)

### Display (Dashboard load):
1. User navigates to `/dashboard`
2. `StatsContext` mounts -> `getUserStats()` -> `GET /api/stats/me`
3. `stats.py:get_stats()` -> `stats_service.get_user_stats(user_id)`
4. Supabase `SELECT * FROM user_stats WHERE user_id = ?`
5. Return `UserStatsResponse` -> frontend state
6. Dashboard renders stats cards + topic mastery map from `useStats().stats`

---

## Testing Plan

### Backend unit tests (`tests/unit/services/test_stats_service.py`):
1. `test_record_generation_creates_row` -- Mock Supabase, call record_generation, verify upsert called with correct values
2. `test_record_generation_increments_existing` -- Mock existing row, verify incremented values
3. `test_record_generation_merges_topic_counts` -- Verify JSONB merge logic (existing + new counts)
4. `test_record_generation_error_does_not_raise` -- Mock Supabase error, verify no exception
5. `test_get_user_stats_returns_defaults_when_no_row` -- Mock empty response, verify defaults
6. `test_get_user_stats_returns_existing_data` -- Mock row data, verify correct dict

### Backend integration tests (`tests/integration/test_stats.py`):
1. `test_get_stats_requires_auth` -- 401 without token
2. `test_get_stats_returns_defaults` -- Authenticated, no row -> defaults
3. `test_generate_records_stats` -- Generate a test, then GET stats, verify counts

### Frontend tests (Dashboard.test.tsx modifications):
1. Update MSW handlers to include `/api/stats/me` mock
2. `test_stats_row_shows_real_numbers` -- Verify test/question counts render
3. `test_topic_mastery_map_renders_bars` -- Verify 5 topic bars with correct labels

---

## Acceptance Criteria

1. Given a user who generates a test with 20 algebra questions, when they view the Dashboard, then `tests_generated` shows 1 and `questions_generated` shows 20.
2. Given a user who generates 3 tests, when they view the Dashboard, then cumulative totals and per-topic bars reflect accurate counts.
3. Given a first-time user with no stats, when they view the Dashboard, then stats show 0/0 and mastery map shows placeholder text.
4. Given a stat recording failure during test generation, when the user generates a test, then the test is still returned successfully.
5. Given the topic mastery map, when rendered, then each bar uses the correct `--color-topic-*` CSS token.
6. Given the stats endpoint, when called without authentication, then it returns 401.
7. Given a user who deletes their account, then the `user_stats` row is deleted via CASCADE.

---

## Edge Cases

| Edge case | Handling |
|---|---|
| First-time user (no row) | `get_user_stats` returns defaults. Dashboard shows zeros + placeholder. |
| Multiple tests in one session | Each generation upserts independently. Counts accumulate. |
| Account deletion | `ON DELETE CASCADE` removes row. |
| Subscription lapse and re-subscribe | Stats persist across gaps. Row never deleted except on account deletion. |
| Concurrent generation requests | Supabase row-level locking on upsert. Worst case: slight count race. Acceptable. |
| New topic added to engine | JSONB keys accommodate new topics automatically. |
| Stats API fails on Dashboard load | `useStats()` returns null. Dashboard shows "--" placeholders. |

---

## Scope Boundary

**IN scope:** `user_stats` table SQL, `StatsService`, `GET /api/stats/me`, `UserStatsResponse`, `StatsContext` + `useStats()`, Dashboard UI (stats cards + topic mastery map), recording hook in generate endpoint, tests.

**OUT of scope:** Historical trends, practice streak (separate spec), per-session stats, stats on non-Dashboard pages, admin dashboard.

**FUTURE:** Time-series table for daily/weekly trends, stats on Generate page, export as PDF, comparison against average user.
