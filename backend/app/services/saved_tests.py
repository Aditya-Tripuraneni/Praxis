"""Saved tests service -- CRUD for user-saved test configurations.

All Supabase calls wrapped in asyncio.to_thread() to avoid blocking
the event loop.
"""

import asyncio
import logging

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


class SavedTestLimitError(Exception):
    """User has reached the maximum number of saved tests."""


class SavedTestsService:
    MAX_SAVED_TESTS = 100

    def __init__(self) -> None:
        self._supabase = _create_service_client()

    @property
    def supabase(self) -> Client:
        if self._supabase is None:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._supabase

    async def save_test(
        self,
        user_id: str,
        test_name: str,
        config: dict,
        seed: int,
        questions: list[dict],
    ) -> dict:
        """Save a test. Returns summary dict (no questions). Raises SavedTestLimitError at 100."""
        count = await self._count_user_tests(user_id)
        if count >= self.MAX_SAVED_TESTS:
            raise SavedTestLimitError("Maximum of 100 saved tests reached")

        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("saved_tests")
                .insert(
                    {
                        "user_id": user_id,
                        "test_name": test_name,
                        "config": config,
                        "seed": seed,
                        "questions": questions,
                    }
                )
                .execute()
            )
        )

        row = result.data[0]
        return {
            "id": row["id"],
            "test_name": row["test_name"],
            "config": row["config"],
            "seed": row["seed"],
            "question_count": len(questions),
            "created_at": row["created_at"],
        }

    async def list_tests(self, user_id: str) -> list[dict]:
        """List all saved tests (no questions). Ordered by created_at desc."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("saved_tests")
                .select("id, test_name, config, seed, questions, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
        )

        summaries = []
        for row in result.data:
            summaries.append(
                {
                    "id": row["id"],
                    "test_name": row["test_name"],
                    "config": row["config"],
                    "seed": row["seed"],
                    "question_count": len(row.get("questions") or []),
                    "created_at": row["created_at"],
                }
            )
        return summaries

    async def get_test(self, test_id: str, user_id: str) -> dict | None:
        """Get full saved test with questions. Returns None if not found or not owned."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("saved_tests")
                .select("*")
                .eq("id", test_id)
                .eq("user_id", user_id)
                .execute()
            )
        )

        if not result.data:
            return None
        return result.data[0]

    async def rename_test(self, test_id: str, user_id: str, new_name: str) -> dict | None:
        """Rename. Returns updated summary or None."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("saved_tests")
                .update({"test_name": new_name})
                .eq("id", test_id)
                .eq("user_id", user_id)
                .execute()
            )
        )

        if not result.data:
            return None

        row = result.data[0]
        return {
            "id": row["id"],
            "test_name": row["test_name"],
            "config": row["config"],
            "seed": row["seed"],
            "question_count": len(row.get("questions") or []),
            "created_at": row["created_at"],
        }

    async def delete_test(self, test_id: str, user_id: str) -> bool:
        """Delete. Returns True if deleted."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("saved_tests")
                .delete()
                .eq("id", test_id)
                .eq("user_id", user_id)
                .execute()
            )
        )

        return bool(result.data)

    async def _count_user_tests(self, user_id: str) -> int:
        """Count saved tests for user."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("saved_tests").select("id").eq("user_id", user_id).execute()
            )
        )
        return len(result.data)


saved_tests_service = SavedTestsService()
