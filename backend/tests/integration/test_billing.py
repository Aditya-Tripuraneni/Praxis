"""Billing endpoint integration tests.

All tests mock the BillingService to avoid live Stripe/Supabase connections.
Tests verify HTTP request/response behavior of billing endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.billing import BillingError, NoActiveSubscriptionError

# ---------------------------------------------------------------------------
# Fixtures (mock_user, auth_client, auth_no_sub_client are in conftest.py)
# ---------------------------------------------------------------------------


@pytest.fixture
async def subscribed_client(mock_user):
    """Test client with mocked authentication AND active subscription.

    Same as auth_client but kept as an explicit alias for billing test clarity.
    """
    from app.api.dependencies import (
        AuthenticatedUser,
        get_current_user,
        require_active_subscription,
    )
    from app.models.auth import UserProfile

    authenticated_user = AuthenticatedUser(
        profile=UserProfile(**mock_user),
        access_token="mock-access-token",
    )

    async def mock_get_current_user():
        return authenticated_user

    async def mock_require_active_subscription():
        return authenticated_user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_active_subscription] = mock_require_active_subscription

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


# =========================================================================
# POST /api/billing/create-checkout-session
# =========================================================================


class TestCreateCheckoutEndpoint:
    async def test_returns_checkout_url(self, auth_client):
        """Authenticated user gets checkout URL."""
        with patch(
            "app.services.billing.billing_service.create_checkout_session",
            new_callable=AsyncMock,
            return_value="https://checkout.stripe.com/test_session",
        ):
            response = await auth_client.post(
                "/api/billing/create-checkout-session",
                json={"plan": "student"},
            )
        assert response.status_code == 200
        assert response.json()["url"] == "https://checkout.stripe.com/test_session"

    async def test_401_without_auth(self, client):
        """No auth -> 401."""
        response = await client.post("/api/billing/create-checkout-session")
        assert response.status_code == 401

    async def test_400_on_billing_error(self, auth_client):
        """BillingError -> 400."""
        with patch(
            "app.services.billing.billing_service.create_checkout_session",
            new_callable=AsyncMock,
            side_effect=BillingError("You already have an active subscription"),
        ):
            response = await auth_client.post(
                "/api/billing/create-checkout-session",
                json={"plan": "student"},
            )
        assert response.status_code == 400
        assert "active subscription" in response.json()["detail"].lower()

    async def test_500_on_unexpected_error(self, auth_client):
        """Unexpected error -> 500."""
        with patch(
            "app.services.billing.billing_service.create_checkout_session",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Something broke"),
        ):
            response = await auth_client.post(
                "/api/billing/create-checkout-session",
                json={"plan": "student"},
            )
        assert response.status_code == 500
        assert "failed to create checkout session" in response.json()["detail"].lower()

    async def test_checkout_with_plan_parameter(self, auth_client):
        """POST with plan='tutor' -> 200 response with checkout URL."""
        with patch(
            "app.services.billing.billing_service.create_checkout_session",
            new_callable=AsyncMock,
            return_value="https://checkout.stripe.com/tutor_session",
        ):
            response = await auth_client.post(
                "/api/billing/create-checkout-session",
                json={"plan": "tutor"},
            )
        assert response.status_code == 200
        assert response.json()["url"] == "https://checkout.stripe.com/tutor_session"


# =========================================================================
# GET /api/billing/subscription-status
# =========================================================================


class TestSubscriptionStatusEndpoint:
    async def test_returns_active_status(self, auth_client):
        """Active subscription -> is_active=True."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={
                "status": "active",
                "is_active": True,
                "current_period_end": "2026-04-12T00:00:00Z",
            },
        ):
            response = await auth_client.get("/api/billing/subscription-status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["is_active"] is True

    async def test_returns_inactive_status(self, auth_client):
        """No subscription -> is_active=False."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={
                "status": "inactive",
                "is_active": False,
                "current_period_end": None,
            },
        ):
            response = await auth_client.get("/api/billing/subscription-status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"
        assert data["is_active"] is False

    async def test_401_without_auth(self, client):
        """No auth -> 401."""
        response = await client.get("/api/billing/subscription-status")
        assert response.status_code == 401


# =========================================================================
# POST /api/billing/cancel-subscription
# =========================================================================


class TestCancelSubscriptionEndpoint:
    async def test_cancels_successfully(self, auth_client):
        """Successful cancel -> 200 with message."""
        with patch(
            "app.services.billing.billing_service.cancel_subscription",
            new_callable=AsyncMock,
            return_value={
                "message": "Subscription will cancel at end of billing period",
                "cancel_at_period_end": True,
            },
        ):
            response = await auth_client.post("/api/billing/cancel-subscription")
        assert response.status_code == 200
        data = response.json()
        assert data["cancel_at_period_end"] is True
        assert "cancel" in data["message"].lower()

    async def test_400_no_active_subscription(self, auth_client):
        """No active subscription -> 400."""
        with patch(
            "app.services.billing.billing_service.cancel_subscription",
            new_callable=AsyncMock,
            side_effect=NoActiveSubscriptionError("No active subscription found"),
        ):
            response = await auth_client.post("/api/billing/cancel-subscription")
        assert response.status_code == 400
        assert "no active subscription" in response.json()["detail"].lower()

    async def test_401_without_auth(self, client):
        """No auth -> 401."""
        response = await client.post("/api/billing/cancel-subscription")
        assert response.status_code == 401


# =========================================================================
# POST /api/billing/webhook
# =========================================================================


class TestWebhookEndpoint:
    async def test_valid_webhook_returns_200(self, client):
        """Valid webhook -> 200."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
        ):
            response = await client.post(
                "/api/billing/webhook",
                content=b'{"type": "checkout.session.completed"}',
                headers={"stripe-signature": "sig_valid_test"},
            )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_missing_signature_returns_400(self, client):
        """No stripe-signature header -> 400."""
        response = await client.post(
            "/api/billing/webhook",
            content=b'{"type": "test"}',
        )
        assert response.status_code == 400
        assert "stripe-signature" in response.json()["detail"].lower()

    async def test_invalid_signature_returns_400(self, client):
        """Invalid signature (BillingError) -> 400."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
            side_effect=BillingError("Invalid webhook signature"),
        ):
            response = await client.post(
                "/api/billing/webhook",
                content=b'{"type": "test"}',
                headers={"stripe-signature": "sig_bad"},
            )
        assert response.status_code == 400
        assert "invalid webhook signature" in response.json()["detail"].lower()

    async def test_processing_error_returns_200(self, client):
        """Generic exception -> 200 (acknowledges receipt to prevent Stripe retry storms)."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Database error"),
        ):
            response = await client.post(
                "/api/billing/webhook",
                content=b'{"type": "test"}',
                headers={"stripe-signature": "sig_test"},
            )
        # Return 200 to acknowledge receipt — errors are logged for async investigation
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    async def test_no_auth_required(self, client):
        """Webhook endpoint does not require authentication."""
        with patch(
            "app.services.billing.billing_service.handle_webhook",
            new_callable=AsyncMock,
        ):
            response = await client.post(
                "/api/billing/webhook",
                content=b'{"type": "test"}',
                headers={"stripe-signature": "sig_test"},
            )
        # Should work without any auth header
        assert response.status_code == 200


# =========================================================================
# Subscription gate tests (require_active_subscription dependency)
# =========================================================================


class TestSubscriptionGate:
    async def test_generate_requires_subscription(self, auth_no_sub_client):
        """POST /api/tests/generate without subscription -> 403."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={"status": "inactive", "is_active": False, "current_period_end": None},
        ):
            response = await auth_no_sub_client.post(
                "/api/tests/generate",
                json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
            )
        assert response.status_code == 403
        assert "subscription" in response.json()["detail"].lower()

    async def test_generate_allowed_with_subscription(self, subscribed_client):
        """POST /api/tests/generate with active subscription -> 200."""
        response = await subscribed_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        # The endpoint either returns 200 (if generation_service works) or
        # a non-403 error. The key assertion: subscription gate does NOT block.
        assert response.status_code != 403

    async def test_get_test_requires_subscription(self, auth_no_sub_client):
        """GET /api/tests/{id} without subscription -> 403."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={"status": "inactive", "is_active": False, "current_period_end": None},
        ):
            response = await auth_no_sub_client.get("/api/tests/some-test-id")
        assert response.status_code == 403
        assert "subscription" in response.json()["detail"].lower()

    async def test_pdf_requires_subscription(self, auth_no_sub_client):
        """GET /api/tests/{id}/pdf without subscription -> 403."""
        with patch(
            "app.services.billing.billing_service.get_subscription_status",
            new_callable=AsyncMock,
            return_value={"status": "inactive", "is_active": False, "current_period_end": None},
        ):
            response = await auth_no_sub_client.get("/api/tests/some-test-id/pdf")
        assert response.status_code == 403
        assert "subscription" in response.json()["detail"].lower()

    async def test_topics_does_not_require_subscription(self, client):
        """GET /api/tests/topics is public -- no auth needed."""
        response = await client.get("/api/tests/topics")
        assert response.status_code == 200
