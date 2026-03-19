"""Stats endpoint integration tests.

All tests mock the StatsService to avoid live Supabase connections.
Tests verify HTTP request/response behavior of the stats endpoint.
"""

from unittest.mock import AsyncMock, patch

from app.services.stats import StatsService

# =========================================================================
# GET /api/stats/me
# =========================================================================


class TestStatsEndpoint:
    async def test_get_stats_requires_auth(self, client):
        """401 without authentication."""
        response = await client.get("/api/stats/me")
        assert response.status_code == 401

    async def test_get_stats_returns_defaults(self, auth_client):
        """Authenticated user with no stats row gets defaults."""
        with patch.object(
            StatsService,
            "get_user_stats",
            new_callable=AsyncMock,
            return_value=StatsService._defaults(),
        ):
            response = await auth_client.get("/api/stats/me")

        assert response.status_code == 200
        data = response.json()
        assert data["tests_generated"] == 0
        assert data["questions_generated"] == 0
        assert data["topic_counts"] == {}
        assert data["streak_current"] == 0
        assert data["streak_best"] == 0
        assert data["is_active_today"] is False

    async def test_get_stats_includes_timer_duration(self, auth_client):
        """Stats response includes last_test_duration field."""
        mock_data = {
            **StatsService._defaults(),
            "last_test_duration": 1425,
        }
        with patch.object(
            StatsService,
            "get_user_stats",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            response = await auth_client.get("/api/stats/me")

        assert response.status_code == 200
        assert response.json()["last_test_duration"] == 1425

    async def test_get_stats_timer_null_by_default(self, auth_client):
        """Stats response has null last_test_duration when no timer saved."""
        with patch.object(
            StatsService,
            "get_user_stats",
            new_callable=AsyncMock,
            return_value=StatsService._defaults(),
        ):
            response = await auth_client.get("/api/stats/me")

        assert response.status_code == 200
        assert response.json()["last_test_duration"] is None

    async def test_get_stats_returns_data(self, auth_client):
        """Returns real stats when row exists."""
        mock_data = {
            "tests_generated": 18,
            "questions_generated": 247,
            "topic_counts": {"algebra": 100, "trig": 147},
            "streak_current": 5,
            "streak_best": 12,
            "is_active_today": True,
        }
        with patch.object(
            StatsService,
            "get_user_stats",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            response = await auth_client.get("/api/stats/me")

        assert response.status_code == 200
        data = response.json()
        assert data["tests_generated"] == 18
        assert data["questions_generated"] == 247
        assert data["topic_counts"] == {
            "algebra": 100,
            "trig": 147,
        }
        assert data["streak_current"] == 5
        assert data["streak_best"] == 12
        assert data["is_active_today"] is True

    async def test_get_stats_inactive_today(self, auth_client):
        """Returns is_active_today=False when not practiced today."""
        mock_data = {
            "tests_generated": 10,
            "questions_generated": 100,
            "topic_counts": {"algebra": 100},
            "streak_current": 0,
            "streak_best": 5,
            "is_active_today": False,
        }
        with patch.object(
            StatsService,
            "get_user_stats",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            response = await auth_client.get("/api/stats/me")

        assert response.status_code == 200
        data = response.json()
        assert data["is_active_today"] is False
        assert data["streak_current"] == 0

    async def test_get_stats_service_error_returns_defaults(self, auth_client):
        """Service returning defaults on error still yields 200."""
        with patch.object(
            StatsService,
            "get_user_stats",
            new_callable=AsyncMock,
            return_value=StatsService._defaults(),
        ):
            response = await auth_client.get("/api/stats/me")

        assert response.status_code == 200
        data = response.json()
        assert data["tests_generated"] == 0
        assert data["is_active_today"] is False


# =========================================================================
# PUT /api/stats/timer
# =========================================================================


class TestTimerEndpoint:
    async def test_save_timer_valid(self, auth_client):
        """Valid duration returns 200 with saved=true."""
        with patch.object(
            StatsService,
            "save_timer_duration",
            new_callable=AsyncMock,
        ):
            response = await auth_client.put(
                "/api/stats/timer",
                json={"duration": 300},
            )
        assert response.status_code == 200
        assert response.json()["saved"] is True

    async def test_save_timer_no_auth(self, client):
        """401 without authentication."""
        response = await client.put(
            "/api/stats/timer",
            json={"duration": 300},
        )
        assert response.status_code == 401

    async def test_save_timer_zero(self, auth_client):
        """Duration of 0 returns 422 (must be > 0)."""
        response = await auth_client.put(
            "/api/stats/timer",
            json={"duration": 0},
        )
        assert response.status_code == 422

    async def test_save_timer_negative(self, auth_client):
        """Negative duration returns 422."""
        response = await auth_client.put(
            "/api/stats/timer",
            json={"duration": -5},
        )
        assert response.status_code == 422

    async def test_save_timer_too_large(self, auth_client):
        """Duration over 86400 returns 422."""
        response = await auth_client.put(
            "/api/stats/timer",
            json={"duration": 86401},
        )
        assert response.status_code == 422

    async def test_save_timer_missing_body(self, auth_client):
        """Missing duration field returns 422."""
        response = await auth_client.put(
            "/api/stats/timer",
            json={},
        )
        assert response.status_code == 422

    async def test_save_timer_max_valid(self, auth_client):
        """Duration of exactly 86400 is accepted."""
        with patch.object(
            StatsService,
            "save_timer_duration",
            new_callable=AsyncMock,
        ):
            response = await auth_client.put(
                "/api/stats/timer",
                json={"duration": 86400},
            )
        assert response.status_code == 200

    async def test_save_timer_service_error(self, auth_client):
        """Service error returns 500."""
        with patch.object(
            StatsService,
            "save_timer_duration",
            new_callable=AsyncMock,
            side_effect=RuntimeError("DB error"),
        ):
            response = await auth_client.put(
                "/api/stats/timer",
                json={"duration": 300},
            )
        assert response.status_code == 500
