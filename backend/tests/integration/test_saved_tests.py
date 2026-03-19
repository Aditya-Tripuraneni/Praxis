"""Integration tests for saved tests API.

All tests mock the SavedTestsService to avoid live Supabase connections.
Tests verify HTTP request/response behavior of saved-tests endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.saved_tests import SavedTestLimitError

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_CONFIG = {"topics": ["algebra"], "difficulty": "easy", "count": 3}

SAMPLE_QUESTIONS = [
    {"topic": "algebra", "question": "Solve x + 1 = 2", "answer": "x = 1"},
    {"topic": "algebra", "question": "Solve 2x = 6", "answer": "x = 3"},
    {"topic": "algebra", "question": "Solve x - 4 = 0", "answer": "x = 4"},
]

SAMPLE_SAVED_SUMMARY = {
    "id": "saved-test-id-aaa",
    "test_name": "My Algebra Test",
    "config": SAMPLE_CONFIG,
    "seed": 42,
    "question_count": 3,
    "created_at": "2026-03-18T10:00:00Z",
}

SAMPLE_SAVED_FULL = {
    "id": "saved-test-id-aaa",
    "test_name": "My Algebra Test",
    "config": SAMPLE_CONFIG,
    "seed": 42,
    "questions": SAMPLE_QUESTIONS,
    "created_at": "2026-03-18T10:00:00Z",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def tutor_client(mock_user):
    """Test client with mocked authentication + tutor subscription.

    Overrides require_tutor_subscription (used by all saved-tests endpoints)
    so tests don't need a live Supabase/Stripe connection.
    """
    from app.api.dependencies import (
        AuthenticatedUser,
        get_current_user,
        require_tutor_subscription,
    )
    from app.models.auth import UserProfile

    authenticated_user = AuthenticatedUser(
        profile=UserProfile(**mock_user),
        access_token="mock-access-token",
    )

    async def mock_get_current_user():
        return authenticated_user

    async def mock_require_tutor():
        return authenticated_user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_tutor_subscription] = mock_require_tutor

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


# =========================================================================
# POST /api/saved-tests — save a test
# =========================================================================


class TestSaveTest:
    async def test_save_requires_auth(self, client):
        """POST /api/saved-tests without auth -> 401."""
        response = await client.post(
            "/api/saved-tests",
            json={
                "test_name": "Test",
                "config": SAMPLE_CONFIG,
                "seed": 42,
                "questions": SAMPLE_QUESTIONS,
            },
        )
        assert response.status_code == 401

    async def test_save_requires_tutor_plan(self, auth_no_sub_client):
        """POST /api/saved-tests without tutor plan -> 403.

        auth_no_sub_client has auth but no subscription override, so
        require_tutor_subscription runs and checks billing_service.
        """
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={
                "status": "active",
                "is_active": True,
                "plan": "student",
                "current_period_end": "2026-04-12T00:00:00Z",
            },
        ):
            response = await auth_no_sub_client.post(
                "/api/saved-tests",
                json={
                    "test_name": "Test",
                    "config": SAMPLE_CONFIG,
                    "seed": 42,
                    "questions": SAMPLE_QUESTIONS,
                },
            )
        assert response.status_code == 403
        assert "tutor" in response.json()["detail"].lower()

    async def test_save_succeeds(self, tutor_client):
        """POST /api/saved-tests with tutor plan -> 201 with summary."""
        with patch(
            "app.services.saved_tests.saved_tests_service.save_test",
            new_callable=AsyncMock,
            return_value=SAMPLE_SAVED_SUMMARY,
        ):
            response = await tutor_client.post(
                "/api/saved-tests",
                json={
                    "test_name": "My Algebra Test",
                    "config": SAMPLE_CONFIG,
                    "seed": 42,
                    "questions": SAMPLE_QUESTIONS,
                },
            )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "saved-test-id-aaa"
        assert data["test_name"] == "My Algebra Test"
        assert data["question_count"] == 3

    async def test_save_limit_reached_returns_409(self, tutor_client):
        """POST /api/saved-tests at 100-test limit -> 409."""
        with patch(
            "app.services.saved_tests.saved_tests_service.save_test",
            new_callable=AsyncMock,
            side_effect=SavedTestLimitError("Maximum of 100 saved tests reached"),
        ):
            response = await tutor_client.post(
                "/api/saved-tests",
                json={
                    "test_name": "Test",
                    "config": SAMPLE_CONFIG,
                    "seed": 42,
                    "questions": SAMPLE_QUESTIONS,
                },
            )
        assert response.status_code == 409
        assert "100" in response.json()["detail"]

    async def test_save_service_error_returns_500(self, tutor_client):
        """Unexpected service error -> 500."""
        with patch(
            "app.services.saved_tests.saved_tests_service.save_test",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Database error"),
        ):
            response = await tutor_client.post(
                "/api/saved-tests",
                json={
                    "test_name": "Test",
                    "config": SAMPLE_CONFIG,
                    "seed": 42,
                    "questions": SAMPLE_QUESTIONS,
                },
            )
        assert response.status_code == 500
        assert "failed to save test" in response.json()["detail"].lower()


# =========================================================================
# GET /api/saved-tests — list saved tests
# =========================================================================


class TestListTests:
    async def test_list_requires_auth(self, client):
        """GET /api/saved-tests without auth -> 401."""
        response = await client.get("/api/saved-tests")
        assert response.status_code == 401

    async def test_list_returns_summaries(self, tutor_client):
        """GET /api/saved-tests -> list of summaries."""
        with patch(
            "app.services.saved_tests.saved_tests_service.list_tests",
            new_callable=AsyncMock,
            return_value=[SAMPLE_SAVED_SUMMARY],
        ):
            response = await tutor_client.get("/api/saved-tests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "saved-test-id-aaa"
        assert data[0]["test_name"] == "My Algebra Test"
        assert data[0]["question_count"] == 3

    async def test_list_empty(self, tutor_client):
        """GET /api/saved-tests with no saved tests -> empty list."""
        with patch(
            "app.services.saved_tests.saved_tests_service.list_tests",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = await tutor_client.get("/api/saved-tests")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_service_error_returns_500(self, tutor_client):
        """Unexpected service error -> 500."""
        with patch(
            "app.services.saved_tests.saved_tests_service.list_tests",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Database error"),
        ):
            response = await tutor_client.get("/api/saved-tests")
        assert response.status_code == 500
        assert "failed to list" in response.json()["detail"].lower()


# =========================================================================
# GET /api/saved-tests/{test_id}/replay — replay a saved test
# =========================================================================


class TestReplayTest:
    async def test_replay_requires_auth(self, client):
        """GET /api/saved-tests/{id}/replay without auth -> 401."""
        response = await client.get("/api/saved-tests/some-id/replay")
        assert response.status_code == 401

    async def test_replay_returns_full_test(self, tutor_client):
        """Replay returns full test with questions array."""
        with (
            patch(
                "app.services.saved_tests.saved_tests_service.get_test",
                new_callable=AsyncMock,
                return_value=SAMPLE_SAVED_FULL,
            ),
            patch(
                "app.services.stats.stats_service.record_generation",
                new_callable=AsyncMock,
            ),
            patch(
                "app.services.stats.stats_service.update_streak",
                new_callable=AsyncMock,
            ),
        ):
            response = await tutor_client.get("/api/saved-tests/saved-test-id-aaa/replay")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "saved-test-id-aaa"
        assert data["test_name"] == "My Algebra Test"
        assert len(data["questions"]) == 3
        assert data["questions"] == SAMPLE_QUESTIONS

    async def test_replay_returns_identical_questions(self, tutor_client):
        """Replayed test contains the exact same questions that were saved."""
        with (
            patch(
                "app.services.saved_tests.saved_tests_service.get_test",
                new_callable=AsyncMock,
                return_value=SAMPLE_SAVED_FULL,
            ),
            patch(
                "app.services.stats.stats_service.record_generation",
                new_callable=AsyncMock,
            ),
            patch(
                "app.services.stats.stats_service.update_streak",
                new_callable=AsyncMock,
            ),
        ):
            response = await tutor_client.get("/api/saved-tests/saved-test-id-aaa/replay")
        data = response.json()
        # Verify each question field matches exactly
        for i, q in enumerate(SAMPLE_QUESTIONS):
            assert data["questions"][i]["topic"] == q["topic"]
            assert data["questions"][i]["question"] == q["question"]
            assert data["questions"][i]["answer"] == q["answer"]

    async def test_replay_not_found_returns_404(self, tutor_client):
        """Replay with nonexistent UUID -> 404."""
        with patch(
            "app.services.saved_tests.saved_tests_service.get_test",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await tutor_client.get(
                "/api/saved-tests/00000000-0000-0000-0000-000000000000/replay"
            )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_replay_records_stats(self, tutor_client):
        """Replay triggers stats recording (record_generation + update_streak)."""
        mock_record = AsyncMock()
        mock_streak = AsyncMock()
        with (
            patch(
                "app.services.saved_tests.saved_tests_service.get_test",
                new_callable=AsyncMock,
                return_value=SAMPLE_SAVED_FULL,
            ),
            patch(
                "app.services.stats.stats_service.record_generation",
                mock_record,
            ),
            patch(
                "app.services.stats.stats_service.update_streak",
                mock_streak,
            ),
        ):
            response = await tutor_client.get("/api/saved-tests/saved-test-id-aaa/replay")
        assert response.status_code == 200
        mock_record.assert_awaited_once_with(
            user_id="test-user-id-123",
            question_count=3,
            topic_counts={"algebra": 3},
        )
        mock_streak.assert_awaited_once_with("test-user-id-123")

    async def test_replay_succeeds_even_if_stats_fail(self, tutor_client):
        """Stats failure is non-blocking -- replay still returns 200."""
        with (
            patch(
                "app.services.saved_tests.saved_tests_service.get_test",
                new_callable=AsyncMock,
                return_value=SAMPLE_SAVED_FULL,
            ),
            patch(
                "app.services.stats.stats_service.record_generation",
                new_callable=AsyncMock,
                side_effect=RuntimeError("Stats DB down"),
            ),
            patch(
                "app.services.stats.stats_service.update_streak",
                new_callable=AsyncMock,
            ),
        ):
            response = await tutor_client.get("/api/saved-tests/saved-test-id-aaa/replay")
        assert response.status_code == 200
        assert response.json()["id"] == "saved-test-id-aaa"


# =========================================================================
# PATCH /api/saved-tests/{test_id} — rename a saved test
# =========================================================================


class TestRenameTest:
    async def test_rename_requires_auth(self, client):
        """PATCH /api/saved-tests/{id} without auth -> 401."""
        response = await client.patch(
            "/api/saved-tests/some-id",
            json={"test_name": "New Name"},
        )
        assert response.status_code == 401

    async def test_rename_succeeds(self, tutor_client):
        """Rename returns updated summary with new name."""
        renamed_summary = {**SAMPLE_SAVED_SUMMARY, "test_name": "Renamed Test"}
        with patch(
            "app.services.saved_tests.saved_tests_service.rename_test",
            new_callable=AsyncMock,
            return_value=renamed_summary,
        ):
            response = await tutor_client.patch(
                "/api/saved-tests/saved-test-id-aaa",
                json={"test_name": "Renamed Test"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["test_name"] == "Renamed Test"
        assert data["id"] == "saved-test-id-aaa"

    async def test_rename_not_found_returns_404(self, tutor_client):
        """Rename nonexistent test -> 404."""
        with patch(
            "app.services.saved_tests.saved_tests_service.rename_test",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await tutor_client.patch(
                "/api/saved-tests/nonexistent-id",
                json={"test_name": "New Name"},
            )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_rename_empty_name_returns_422(self, tutor_client):
        """Empty test_name -> 422 validation error."""
        response = await tutor_client.patch(
            "/api/saved-tests/saved-test-id-aaa",
            json={"test_name": ""},
        )
        assert response.status_code == 422


# =========================================================================
# DELETE /api/saved-tests/{test_id} — delete a saved test
# =========================================================================


class TestDeleteTest:
    async def test_delete_requires_auth(self, client):
        """DELETE /api/saved-tests/{id} without auth -> 401."""
        response = await client.delete("/api/saved-tests/some-id")
        assert response.status_code == 401

    async def test_delete_succeeds(self, tutor_client):
        """Delete returns success message."""
        with patch(
            "app.services.saved_tests.saved_tests_service.delete_test",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = await tutor_client.delete("/api/saved-tests/saved-test-id-aaa")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    async def test_delete_not_found_returns_404(self, tutor_client):
        """Delete nonexistent test -> 404."""
        with patch(
            "app.services.saved_tests.saved_tests_service.delete_test",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = await tutor_client.delete("/api/saved-tests/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_then_replay_returns_404(self, tutor_client):
        """After deletion, replaying the same test returns 404."""
        with patch(
            "app.services.saved_tests.saved_tests_service.get_test",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await tutor_client.get("/api/saved-tests/saved-test-id-aaa/replay")
        assert response.status_code == 404


# =========================================================================
# Save + List integration (multi-step flow)
# =========================================================================


class TestSaveAndListFlow:
    async def test_save_and_list(self, tutor_client):
        """Save a test, then list -- verify the saved test appears."""
        # Step 1: Save
        with patch(
            "app.services.saved_tests.saved_tests_service.save_test",
            new_callable=AsyncMock,
            return_value=SAMPLE_SAVED_SUMMARY,
        ):
            save_response = await tutor_client.post(
                "/api/saved-tests",
                json={
                    "test_name": "My Algebra Test",
                    "config": SAMPLE_CONFIG,
                    "seed": 42,
                    "questions": SAMPLE_QUESTIONS,
                },
            )
        assert save_response.status_code == 201
        saved_id = save_response.json()["id"]

        # Step 2: List
        with patch(
            "app.services.saved_tests.saved_tests_service.list_tests",
            new_callable=AsyncMock,
            return_value=[SAMPLE_SAVED_SUMMARY],
        ):
            list_response = await tutor_client.get("/api/saved-tests")
        assert list_response.status_code == 200
        ids = [t["id"] for t in list_response.json()]
        assert saved_id in ids

        # Verify the summary fields
        saved = next(t for t in list_response.json() if t["id"] == saved_id)
        assert saved["test_name"] == "My Algebra Test"
        assert saved["config"] == SAMPLE_CONFIG
        assert saved["seed"] == 42
        assert saved["question_count"] == 3
