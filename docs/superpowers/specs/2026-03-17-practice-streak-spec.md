# Spec: Practice Streak

**Date**: 2026-03-17
**Status**: Approved
**Prerequisite**: Active subscription + test generation flow working (Layers 1-3 complete)
**Shared table**: `user_stats` (defined in lifetime-stats-spec.md)

---

## Overview

Track consecutive days a user generates at least one test. Display a prominent streak counter on the Dashboard with a Lucide `Flame` SVG icon featuring an animated fiery glow (multi-layered orange/amber/gold CSS drop-shadows that pulse like lava). The streak resets when a day is missed. This leverages loss aversion -- the same mechanism that makes Duolingo's streak its most powerful retention feature. A student with a 14-day streak will open the app on day 15 just to avoid losing it. Zero additional infrastructure cost.

---

## Database Schema

Uses the SAME `user_stats` table from the Lifetime Stats spec. The streak columns are:

```sql
-- Part of user_stats table:
streak_current INTEGER NOT NULL DEFAULT 0,
streak_best INTEGER NOT NULL DEFAULT 0,
last_practice_date DATE,
```

**If Lifetime Stats ships first:** These columns already exist with safe defaults.
**If Practice Streak ships first:** Create the full `user_stats` table. Lifetime Stats columns (`tests_generated`, `questions_generated`, `topic_counts`) have defaults and won't interfere.

**Timezone:** All date comparisons use UTC. `last_practice_date` stores the UTC date of last generation.

---

## Backend Service

**Extends `StatsService`** from Lifetime Stats (or stands alone if that hasn't shipped):

```python
async def update_streak(self, user_id: str) -> None:
    """Update practice streak on test generation.
    Non-blocking -- errors logged, not raised.

    Logic:
    1. Fetch existing row (last_practice_date, streak_current, streak_best)
    2. today = datetime.now(timezone.utc).date()
    3. If last_practice_date == today: return (already counted)
    4. If last_practice_date == today - 1 day: streak_current += 1
    5. Else: streak_current = 1 (reset)
    6. streak_best = max(streak_current, streak_best)
    7. last_practice_date = today
    8. Upsert row
    """

async def get_streak(self, user_id: str) -> dict:
    """Get streak data.
    Returns: {streak_current, streak_best, is_active_today}
    is_active_today = (last_practice_date == date.today() UTC)
    """
```

**Timezone decision: UTC.** All comparisons use `datetime.now(timezone.utc).date()`. A student's "day" boundary is midnight UTC, not their local midnight. Rationale:
- Consistent, server-authoritative, requires no client timezone
- Edge case: US student practicing at 11pm EST has practice counted for next UTC day
- This is acceptable -- the streak still works correctly for consecutive UTC days

**Recording hook:** Same location as Lifetime Stats -- inside `POST /api/tests/generate`:

```python
try:
    await stats_service.record_generation(user_id, count, topic_counts)
    await stats_service.update_streak(user_id)
except Exception:
    logger.warning("Failed to record stats/streak", exc_info=True)
```

---

## API Endpoints

### `GET /api/stats/me` -- Extended response (same endpoint as Lifetime Stats)

Streak fields added to `UserStatsResponse`:

```python
class UserStatsResponse(BaseModel):
    tests_generated: int = 0
    questions_generated: int = 0
    topic_counts: dict[str, int] = Field(default_factory=dict)
    streak_current: int = 0
    streak_best: int = 0
    is_active_today: bool = False
```

`is_active_today` is computed server-side: `last_practice_date == date.today()` (UTC).

**Example response:**
```json
{
  "tests_generated": 18,
  "questions_generated": 247,
  "topic_counts": {"algebra": 94, "trigonometry": 62},
  "streak_current": 7,
  "streak_best": 14,
  "is_active_today": true
}
```

---

## Frontend Types

**Update `UserStats` in `types/index.ts`:**
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

No new function needed -- `getUserStats()` from Lifetime Stats fetches the full response including streak fields.

---

## Frontend Context

Same `StatsContext` from Lifetime Stats. Streak data is part of the `stats` object.

---

## Frontend UI

### Animated Flame Glow (CSS in index.css)

New CSS classes for the streak flame icon. The animation creates a multi-layered orange/amber/gold pulsing glow effect -- like lava shifting inside a flame.

```css
/* -----------------------------------------------------------------------
   Streak Flame Animation
   ----------------------------------------------------------------------- */
@keyframes fire-glow {
  0%, 100% {
    filter: drop-shadow(0 0 3px rgba(249, 115, 22, 0.5))
            drop-shadow(0 0 6px rgba(245, 158, 11, 0.3))
            drop-shadow(0 0 2px rgba(234, 88, 12, 0.2));
  }
  33% {
    filter: drop-shadow(0 0 5px rgba(245, 158, 11, 0.6))
            drop-shadow(0 0 10px rgba(249, 115, 22, 0.4))
            drop-shadow(0 0 3px rgba(251, 191, 36, 0.3));
  }
  66% {
    filter: drop-shadow(0 0 4px rgba(234, 88, 12, 0.5))
            drop-shadow(0 0 8px rgba(249, 115, 22, 0.35))
            drop-shadow(0 0 2px rgba(245, 158, 11, 0.25));
  }
}

.flame-active {
  color: #f97316;
  animation: fire-glow 2.5s ease-in-out infinite;
}

.flame-inactive {
  color: var(--text-muted);
}

@media (prefers-reduced-motion: reduce) {
  .flame-active {
    animation: none;
    filter: drop-shadow(0 0 4px rgba(249, 115, 22, 0.5));
  }
}
```

**Glow layers explained:**
- Layer 1 (inner): deep orange `rgba(234, 88, 12)` -- the hot core
- Layer 2 (middle): standard orange `rgba(249, 115, 22)` -- the body of the flame
- Layer 3 (outer): amber/gold `rgba(245, 158, 11)` and `rgba(251, 191, 36)` -- the outer heat shimmer

The three keyframe stops (0%/33%/66%) shift which layer is brightest, creating the illusion of internal movement -- like lava flowing inside the flame. The 2.5s cycle is slow enough to feel organic, not frantic.

### Streak display card

Placed between the subscription card and the stats row on the subscribed Dashboard view.

```
+----------------------------------------------------+
|  [Flame SVG]  7 day streak           [Trophy] Best: 14 |
|                                                     |
|  [o][o][o][o][o][o][*]                              |
|   (7 dots: 6 filled, 1 = today, glowing)            |
+----------------------------------------------------+
```

**Flame icon:** Lucide `Flame` component, 24px size, `fill="currentColor"` (solid, not outline). Apply `.flame-active` class when `is_active_today` is true, `.flame-inactive` when false.

**Streak number:** `font-size: var(--font-size-2xl)`, `font-weight: 800`, `color: var(--color-primary-900)`.

**"day streak" label:** `font-size: var(--font-size-sm)`, `color: var(--text-secondary)`.

**Best streak:** Right-aligned. Lucide `Trophy` icon (16px, `color: var(--color-accent-400)`). "Best: {N} days" in `font-size: var(--font-size-sm)`, `color: var(--text-secondary)`.

**7-day dot visualization:** Row of 7 circles (8px diameter):
- Filled dots: `background: var(--color-accent-400)` for practiced days
- Empty dots: `background: transparent`, `border: 1.5px solid var(--color-stone-300)`
- Rightmost dot (today): if `is_active_today`, filled with `var(--color-accent-500)` + subtle glow. If not, empty.
- Number of filled dots = `min(streak_current, 7)` (rightmost N dots filled)

**Zero streak state:** "Start your streak" text, Lucide `Flame` with `.flame-inactive` class (muted, no glow), no dots.

**Card styling:** Full width. `background: var(--bg-card)`, `box-shadow: var(--shadow-card)`, `border-radius: var(--radius-md)`, `padding: var(--space-5)`.

**Accessibility:**
- Flame icon: `aria-hidden="true"` (decorative)
- Trophy icon: `aria-hidden="true"` (decorative)
- Streak number: `aria-label="{N} day practice streak"`
- Dots: `aria-hidden="true"` (decorative, number is authoritative)

---

## Data Flow

### Recording (test generation):
1. User generates a test -> `POST /api/tests/generate`
2. After successful generation: `stats_service.update_streak(user_id)`
3. Reads `last_practice_date` from `user_stats`
4. Compares with `datetime.now(timezone.utc).date()`
5. Updates `streak_current`, `streak_best`, `last_practice_date`
6. Upserts row

### Display (Dashboard load):
1. `StatsContext` -> `GET /api/stats/me`
2. `stats_service.get_user_stats()` reads row, computes `is_active_today`
3. Returns `UserStatsResponse` including streak data
4. Dashboard renders streak card from `useStats().stats`

---

## Testing Plan

### Backend unit tests (extend `test_stats_service.py`):
1. `test_update_streak_first_practice` -- No existing row -> streak_current=1, streak_best=1
2. `test_update_streak_consecutive_day` -- last_practice = yesterday -> streak_current increments
3. `test_update_streak_same_day` -- last_practice = today -> no change
4. `test_update_streak_gap_resets` -- last_practice = 3 days ago -> streak_current=1
5. `test_update_streak_best_preserved` -- New streak < existing best -> best unchanged
6. `test_update_streak_new_best` -- New streak > existing best -> best updated
7. `test_update_streak_error_does_not_raise` -- Supabase error -> logged, not raised

### Backend integration tests:
1. `test_stats_response_includes_streak_fields` -- GET /api/stats/me has streak_current, streak_best, is_active_today
2. `test_generate_updates_streak` -- Generate test, then GET stats -> streak_current >= 1

### Frontend tests:
1. Update MSW mock for `/api/stats/me` to include streak fields
2. `test_streak_card_shows_count` -- Verify "7" and "day streak" text render
3. `test_streak_card_shows_best` -- Verify "Best: 14 days" renders
4. `test_streak_zero_shows_start_message` -- Mock streak_current=0 -> "Start your streak"
5. `test_flame_has_active_class` -- When is_active_today=true, flame element has `.flame-active` class

---

## Acceptance Criteria

1. Given a user who generates their first test ever, when they view the Dashboard, then streak shows 1 and `is_active_today` is true.
2. Given a user with a 7-day streak who generates a test today, when they view the Dashboard, then streak shows 8.
3. Given a user with a 7-day streak who misses a day, when they generate a test, then streak resets to 1.
4. Given a user who generates multiple tests in one day, when they view the Dashboard, then streak is still counted as 1 for that day.
5. Given a user with streak_best=14 and streak_current=7, when streak resets, then streak_best remains 14.
6. Given the Dashboard, when the streak card renders, then the Flame icon is a Lucide SVG (not a text emoji).
7. Given `is_active_today=true`, when the Dashboard renders, then the flame icon has the `.flame-active` animated glow.
8. Given `is_active_today=false`, when the Dashboard renders, then the rightmost dot is unfilled and flame has `.flame-inactive`.
9. Given the flame animation, when `prefers-reduced-motion` is set, then the animation is disabled and a static glow is shown instead.

---

## Edge Cases

| Edge case | Handling |
|---|---|
| First-time user | `update_streak` upserts with streak_current=1, streak_best=1, last_practice_date=today. |
| Practice right before UTC midnight | Counted for current UTC day. Post-midnight = next day = streak continues. |
| Subscription lapses | User can't generate -> streak breaks naturally. On re-subscribe, resets to 1. |
| Account deletion | `ON DELETE CASCADE` removes row. |
| Concurrent requests | Both read streak=5/yesterday, both write streak=6/today. Result correct. |
| Stats fetch fails | Dashboard shows streak as 0 / "--". |
| Very long streaks | INTEGER handles up to 2^31. No upper bound. |

---

## Scope Boundary

**IN scope:** `update_streak` + streak fields in `get_user_stats`, streak fields in `UserStatsResponse`, streak card on Dashboard (Flame + Trophy Lucide SVG icons, animated fire-glow, dot visualization), `.flame-active` / `.flame-inactive` CSS classes with `@keyframes fire-glow`, recording in generate endpoint, tests.

**OUT of scope:** Streak freeze/pause, streak notifications, streak on non-Dashboard pages, timezone selection per user, Daily Challenge integration.

**FUTURE:** Streak freeze (1 skip/week), milestone celebrations (7/30/100 day badges), header streak counter, push notifications.
