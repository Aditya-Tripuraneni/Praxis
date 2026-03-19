"""Stats service -- tracks lifetime generation stats and practice streaks.

All Supabase calls wrapped in asyncio.to_thread() to avoid blocking
the event loop.
Stats recording is non-blocking: errors are logged, never raised to
callers.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta, timezone

import httpx
from supabase import Client, ClientOptions, create_client

from app.config import settings

logger = logging.getLogger(__name__)


def _create_service_client() -> Client | None:
    """Create Supabase client with service role key."""
    if settings.supabase_url and settings.supabase_service_role_key:
        options = ClientOptions(httpx_client=httpx.Client(timeout=120, verify=True))
        return create_client(settings.supabase_url, settings.supabase_service_role_key, options)
    return None


class StatsService:
    """Tracks per-user generation stats and practice streaks."""

    def __init__(self) -> None:
        self._supabase = _create_service_client()

    @property
    def supabase(self) -> Client:
        if self._supabase is None:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._supabase

    async def record_generation(
        self,
        user_id: str,
        question_count: int,
        topic_counts: dict[str, int],
    ) -> None:
        """Record a test generation event. Non-blocking."""
        try:
            await self._do_record_generation(user_id, question_count, topic_counts)
        except Exception:
            logger.warning(
                "Failed to record generation stats for user %s",
                user_id,
                exc_info=True,
            )

    async def _do_record_generation(
        self,
        user_id: str,
        question_count: int,
        topic_counts: dict[str, int],
    ) -> None:
        # 1. Fetch existing row
        existing = await asyncio.to_thread(
            lambda: (
                self.supabase.table("user_stats")
                .select("tests_generated, questions_generated, topic_counts")
                .eq("user_id", user_id)
                .execute()
            )
        )

        if existing.data:
            row = existing.data[0]
            new_tests = row["tests_generated"] + 1
            new_questions = row["questions_generated"] + question_count
            # Merge topic counts
            old_topics = row.get("topic_counts") or {}
            merged = dict(old_topics)
            for topic, count in topic_counts.items():
                merged[topic] = merged.get(topic, 0) + count

            await asyncio.to_thread(
                lambda: (
                    self.supabase.table("user_stats")
                    .update(
                        {
                            "tests_generated": new_tests,
                            "questions_generated": new_questions,
                            "topic_counts": merged,
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    .eq("user_id", user_id)
                    .execute()
                )
            )
        else:
            # First generation -- insert new row
            await asyncio.to_thread(
                lambda: (
                    self.supabase.table("user_stats")
                    .insert(
                        {
                            "user_id": user_id,
                            "tests_generated": 1,
                            "questions_generated": question_count,
                            "topic_counts": topic_counts,
                        }
                    )
                    .execute()
                )
            )

    async def update_streak(self, user_id: str) -> None:
        """Update practice streak. Non-blocking."""
        try:
            await self._do_update_streak(user_id)
        except Exception:
            logger.warning(
                "Failed to update streak for user %s",
                user_id,
                exc_info=True,
            )

    async def _do_update_streak(self, user_id: str) -> None:
        today = datetime.now(timezone.utc).date()

        existing = await asyncio.to_thread(
            lambda: (
                self.supabase.table("user_stats")
                .select("streak_current, streak_best, last_practice_date")
                .eq("user_id", user_id)
                .execute()
            )
        )

        if not existing.data:
            # First ever -- insert with streak = 1
            now_iso = datetime.now(timezone.utc).isoformat()
            await asyncio.to_thread(
                lambda: (
                    self.supabase.table("user_stats")
                    .upsert(
                        {
                            "user_id": user_id,
                            "streak_current": 1,
                            "streak_best": 1,
                            "last_practice_date": today.isoformat(),
                            "updated_at": now_iso,
                        }
                    )
                    .execute()
                )
            )
            return

        row = existing.data[0]
        last_date_str = row.get("last_practice_date")
        streak_current = row.get("streak_current", 0)
        streak_best = row.get("streak_best", 0)

        if last_date_str:
            last_date = date.fromisoformat(last_date_str)
            if last_date == today:
                return  # Already counted today
            elif last_date == today - timedelta(days=1):
                streak_current += 1  # Consecutive day
            else:
                streak_current = 1  # Gap -- reset
        else:
            streak_current = 1  # No previous date

        streak_best = max(streak_current, streak_best)

        await asyncio.to_thread(
            lambda: (
                self.supabase.table("user_stats")
                .update(
                    {
                        "streak_current": streak_current,
                        "streak_best": streak_best,
                        "last_practice_date": today.isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("user_id", user_id)
                .execute()
            )
        )

    async def save_timer_duration(self, user_id: str, duration: int) -> None:
        """Save most recent test timer duration. Upserts into user_stats."""
        await asyncio.to_thread(
            lambda: (
                self.supabase.table("user_stats")
                .upsert(
                    {
                        "user_id": user_id,
                        "last_test_duration": duration,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    on_conflict="user_id",
                )
                .execute()
            )
        )

    async def get_user_stats(self, user_id: str) -> dict:
        """Get stats for a user. Returns defaults if no row exists."""
        try:
            result = await asyncio.to_thread(
                lambda: (
                    self.supabase.table("user_stats").select("*").eq("user_id", user_id).execute()
                )
            )
        except Exception:
            logger.warning(
                "Failed to fetch stats for user %s",
                user_id,
                exc_info=True,
            )
            return self._defaults()

        if not result.data:
            return self._defaults()

        row = result.data[0]
        today = datetime.now(timezone.utc).date()
        last_date_str = row.get("last_practice_date")
        is_active = False
        if last_date_str:
            last_date = date.fromisoformat(last_date_str)
            is_active = last_date == today

        return {
            "tests_generated": row.get("tests_generated", 0),
            "questions_generated": row.get("questions_generated", 0),
            "topic_counts": row.get("topic_counts") or {},
            "streak_current": row.get("streak_current", 0),
            "streak_best": row.get("streak_best", 0),
            "is_active_today": is_active,
            "last_test_duration": row.get("last_test_duration"),
        }

    @staticmethod
    def _defaults() -> dict:
        return {
            "tests_generated": 0,
            "questions_generated": 0,
            "topic_counts": {},
            "streak_current": 0,
            "streak_best": 0,
            "is_active_today": False,
            "last_test_duration": None,
        }


stats_service = StatsService()
