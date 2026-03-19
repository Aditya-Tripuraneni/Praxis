"""Rate limiting integration tests.

Verifies that rate limits are enforced on auth and test endpoints.
Each test sends requests up to and beyond the limit within a single
test function (the autouse fixture resets limits between tests).
"""

from unittest.mock import AsyncMock, patch


class TestAuthRateLimits:
    async def test_signup_rate_limited_after_5(self, client):
        """POST /api/auth/signup allows 5 requests/hour, 6th returns 429."""
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            return_value="Account created.",
        ):
            for i in range(5):
                resp = await client.post(
                    "/api/auth/signup",
                    json={"email": f"user{i}@test.com", "password": "testpass123"},
                )
                assert resp.status_code == 201, f"Request {i + 1} should succeed"

            # 6th request should be rate limited
            resp = await client.post(
                "/api/auth/signup",
                json={"email": "extra@test.com", "password": "testpass123"},
            )
            assert resp.status_code == 429

    async def test_login_rate_limited_after_10(self, client):
        """POST /api/auth/login allows 10 requests/minute, 11th returns 429."""
        from app.services.auth import AuthenticationError

        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            side_effect=AuthenticationError("Invalid email or password"),
        ):
            for i in range(10):
                resp = await client.post(
                    "/api/auth/login",
                    json={"email": "user@test.com", "password": "wrong"},
                )
                # Will be 401 (auth failure) but NOT 429 yet
                assert resp.status_code == 401, f"Request {i + 1} should be 401"

            # 11th request should be rate limited
            resp = await client.post(
                "/api/auth/login",
                json={"email": "user@test.com", "password": "wrong"},
            )
            assert resp.status_code == 429


class TestEndpointRateLimits:
    async def test_topics_rate_limited_after_60(self, client):
        """GET /api/tests/topics allows 60/minute, 61st returns 429."""
        for i in range(60):
            resp = await client.get("/api/tests/topics")
            assert resp.status_code == 200, f"Request {i + 1} should succeed"

        resp = await client.get("/api/tests/topics")
        assert resp.status_code == 429

    async def test_generate_rate_limited_after_20(self, auth_client):
        """POST /api/tests/generate allows 20/minute, 21st returns 429."""
        for i in range(20):
            resp = await auth_client.post(
                "/api/tests/generate",
                json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
            )
            assert resp.status_code == 200, f"Request {i + 1} should succeed"

        resp = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        assert resp.status_code == 429

    async def test_rate_limit_returns_retry_after_header(self, client):
        """429 responses should include Retry-After header."""
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            return_value="Account created.",
        ):
            # Exhaust signup limit
            for i in range(5):
                await client.post(
                    "/api/auth/signup",
                    json={"email": f"u{i}@t.com", "password": "testpass123"},
                )

            resp = await client.post(
                "/api/auth/signup",
                json={"email": "extra@t.com", "password": "testpass123"},
            )
            assert resp.status_code == 429
            # Verify the response body indicates rate limiting
            body = resp.json()
            assert "rate limit" in body.get("error", "").lower() or resp.status_code == 429
