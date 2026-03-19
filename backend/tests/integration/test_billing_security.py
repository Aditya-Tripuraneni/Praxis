"""Billing security and rate limiting integration tests.

Verifies rate limits on billing endpoints, webhook security,
and subscription gate enforcement on protected resources.
"""

from unittest.mock import AsyncMock, patch

from app.services.billing import BillingError


class TestBillingRateLimiting:
    async def test_checkout_rate_limited_after_10_per_hour(self, auth_client):
        """POST /api/billing/create-checkout-session allows 10/hour, 11th returns 429."""
        with patch(
            "app.services.billing.billing_service.create_checkout_session",
            new_callable=AsyncMock,
            return_value="https://checkout.stripe.com/test",
        ):
            for i in range(10):
                resp = await auth_client.post(
                    "/api/billing/create-checkout-session", json={"plan": "student"}
                )
                assert resp.status_code == 200, f"Request {i + 1} failed with {resp.status_code}"

            # 11th request should be rate limited
            resp = await auth_client.post(
                "/api/billing/create-checkout-session", json={"plan": "student"}
            )
            assert resp.status_code == 429

    async def test_subscription_status_rate_limited_after_30_per_minute(self, auth_client):
        """GET /api/billing/subscription-status allows 30/minute, 31st returns 429."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={
                "status": "active",
                "is_active": True,
                "current_period_end": "2026-04-13T00:00:00Z",
            },
        ):
            for i in range(30):
                resp = await auth_client.get("/api/billing/subscription-status")
                assert resp.status_code == 200, f"Request {i + 1} failed with {resp.status_code}"

            # 31st request should be rate limited
            resp = await auth_client.get("/api/billing/subscription-status")
            assert resp.status_code == 429

    async def test_cancel_rate_limited_after_3_per_hour(self, auth_client):
        """POST /api/billing/cancel-subscription allows 3/hour, 4th returns 429."""
        with patch(
            "app.services.billing.billing_service.cancel_subscription",
            new_callable=AsyncMock,
            return_value={
                "message": "Subscription will cancel at end of billing period",
                "cancel_at_period_end": True,
            },
        ):
            for i in range(3):
                resp = await auth_client.post("/api/billing/cancel-subscription")
                assert resp.status_code == 200, f"Request {i + 1} failed with {resp.status_code}"

            # 4th request should be rate limited
            resp = await auth_client.post("/api/billing/cancel-subscription")
            assert resp.status_code == 429

    async def test_webhook_not_rate_limited(self, client):
        """POST /api/billing/webhook has no rate limit — 50+ requests all succeed."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
            return_value=None,
        ):
            for i in range(55):
                resp = await client.post(
                    "/api/billing/webhook",
                    content=b'{"test": "payload"}',
                    headers={"stripe-signature": "t=123,v1=abc"},
                )
                assert resp.status_code == 200, (
                    f"Request {i + 1} returned {resp.status_code},"
                    " webhook should never be rate limited"
                )


class TestWebhookSecurity:
    async def test_webhook_rejects_missing_signature(self, client):
        """POST /api/billing/webhook without stripe-signature header returns 400."""
        resp = await client.post(
            "/api/billing/webhook",
            content=b'{"test": "payload"}',
        )
        assert resp.status_code == 400
        assert "Missing stripe-signature header" in resp.json()["detail"]

    async def test_webhook_rejects_invalid_signature(self, client):
        """POST /api/billing/webhook with invalid signature returns 400."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
            side_effect=BillingError("Invalid webhook signature"),
        ):
            resp = await client.post(
                "/api/billing/webhook",
                content=b'{"test": "payload"}',
                headers={"stripe-signature": "t=123,v1=invalid"},
            )
            assert resp.status_code == 400

    async def test_webhook_no_auth_required(self, client):
        """POST /api/billing/webhook succeeds without Authorization header."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = await client.post(
                "/api/billing/webhook",
                content=b'{"test": "payload"}',
                headers={"stripe-signature": "t=123,v1=abc"},
            )
            # No Authorization header, should still succeed
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}

    async def test_webhook_returns_200_on_processing_error(self, client):
        """Webhook returns 200 on generic exceptions to prevent Stripe retry storms."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Unexpected processing error"),
        ):
            resp = await client.post(
                "/api/billing/webhook",
                content=b'{"test": "payload"}',
                headers={"stripe-signature": "t=123,v1=abc"},
            )
            # Return 200 to acknowledge receipt — errors are logged for async investigation
            assert resp.status_code == 200
            assert resp.json()["status"] == "received"


class TestSubscriptionGateSecurity:
    async def test_generate_returns_401_without_auth(self, client):
        """POST /api/tests/generate without auth returns 401."""
        resp = await client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        assert resp.status_code == 401

    async def test_generate_returns_403_without_subscription(self, auth_no_sub_client):
        """POST /api/tests/generate with auth but no subscription returns 403."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={
                "status": "inactive",
                "is_active": False,
                "current_period_end": None,
            },
        ):
            resp = await auth_no_sub_client.post(
                "/api/tests/generate",
                json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
            )
            assert resp.status_code == 403
            assert "Active subscription required" in resp.json()["detail"]

    async def test_pdf_returns_403_without_subscription(self, auth_no_sub_client):
        """GET /api/tests/{test_id}/pdf with auth but no subscription returns 403."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={
                "status": "inactive",
                "is_active": False,
                "current_period_end": None,
            },
        ):
            resp = await auth_no_sub_client.get("/api/tests/some-test-id/pdf")
            assert resp.status_code == 403
            assert "Active subscription required" in resp.json()["detail"]

    async def test_topics_accessible_without_auth(self, client):
        """GET /api/tests/topics is public — no auth required."""
        resp = await client.get("/api/tests/topics")
        assert resp.status_code == 200

    async def test_billing_endpoints_require_auth(self, client):
        """Billing endpoints (except webhook) return 401 without auth."""
        # create-checkout-session
        resp = await client.post("/api/billing/create-checkout-session")
        assert resp.status_code == 401, "create-checkout-session should require auth"

        # subscription-status
        resp = await client.get("/api/billing/subscription-status")
        assert resp.status_code == 401, "subscription-status should require auth"

        # cancel-subscription
        resp = await client.post("/api/billing/cancel-subscription")
        assert resp.status_code == 401, "cancel-subscription should require auth"
