"""Unit tests for BillingService.

All Stripe and Supabase calls are mocked -- no external connections needed.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from app.services.billing import BillingError, BillingService, NoActiveSubscriptionError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_supabase_response(data):
    """Create a mock Supabase .execute() response."""
    resp = MagicMock()
    resp.data = data
    return resp


def _make_supabase_chain(response_data):
    """Build a chained mock for table().select().eq().execute()."""
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_eq.execute.return_value = _mock_supabase_response(response_data)
    mock_select.eq.return_value = mock_eq
    mock_table.select.return_value = mock_select
    return mock_table


def _make_supabase_insert_chain():
    """Build a chained mock for table().insert().execute()."""
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_insert.execute.return_value = _mock_supabase_response([])
    mock_table.insert.return_value = mock_insert
    return mock_table


def _make_supabase_upsert_chain():
    """Build a chained mock for table().upsert().execute()."""
    mock_table = MagicMock()
    mock_upsert = MagicMock()
    mock_upsert.execute.return_value = _mock_supabase_response([])
    mock_table.upsert.return_value = mock_upsert
    return mock_table


def _make_supabase_update_chain():
    """Build a chained mock for table().update().eq().execute()."""
    mock_table = MagicMock()
    mock_update = MagicMock()
    mock_eq = MagicMock()
    mock_eq.execute.return_value = _mock_supabase_response([])
    mock_update.eq.return_value = mock_eq
    mock_table.update.return_value = mock_update
    return mock_table


@pytest.fixture
def service():
    """Create a BillingService with mocked Supabase and Stripe clients."""
    with (
        patch("app.services.billing._create_service_client", return_value=MagicMock()),
        patch("app.services.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.stripe_student_price_id = "price_student_test123"
        mock_settings.stripe_tutor_price_id = "price_tutor_test123"
        mock_settings.stripe_webhook_secret = "whsec_test123"
        mock_settings.frontend_url = "http://localhost:5173"
        mock_settings.supabase_url = "https://fake.supabase.co"
        mock_settings.supabase_service_role_key = "fake-service-role-key"

        with patch(
            "app.services.billing.PLAN_PRICES",
            {
                "student": "price_student_test123",
                "tutor": "price_tutor_test123",
            },
        ):
            svc = BillingService()
            # Replace internal clients with mocks
            svc._supabase = MagicMock()
            svc._stripe = MagicMock()
            yield svc


# =========================================================================
# create_checkout_session
# =========================================================================


class TestCreateCheckoutSession:
    async def test_creates_new_customer_and_session(self, service):
        """New user: create Stripe customer, insert row, return checkout URL."""
        # Supabase returns no existing subscription
        select_chain = _make_supabase_chain([])
        insert_chain = _make_supabase_insert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain  # first call: select
            return insert_chain  # second call: insert

        service._supabase.table.side_effect = table_side_effect

        # Stripe customer create
        service._stripe.v1.customers.create.return_value = MagicMock(id="cus_new_123")

        # Stripe checkout session create
        service._stripe.v1.checkout.sessions.create.return_value = MagicMock(
            url="https://checkout.stripe.com/session_new"
        )

        url = await service.create_checkout_session("user-1", "user@test.com", "student")

        assert url == "https://checkout.stripe.com/session_new"
        service._stripe.v1.customers.create.assert_called_once()
        service._stripe.v1.checkout.sessions.create.assert_called_once()

    async def test_uses_existing_customer(self, service):
        """Existing customer with inactive sub: reuse customer, skip create."""
        existing_row = {
            "user_id": "user-1",
            "stripe_customer_id": "cus_existing_456",
            "status": "inactive",
        }
        select_chain = _make_supabase_chain([existing_row])
        service._supabase.table.return_value = select_chain

        service._stripe.v1.checkout.sessions.create.return_value = MagicMock(
            url="https://checkout.stripe.com/session_existing"
        )

        url = await service.create_checkout_session("user-1", "user@test.com", "student")

        assert url == "https://checkout.stripe.com/session_existing"
        # Should NOT have created a new customer
        service._stripe.v1.customers.create.assert_not_called()
        service._stripe.v1.checkout.sessions.create.assert_called_once()

    async def test_rejects_already_active_subscription(self, service):
        """User with active sub gets BillingError."""
        active_row = {
            "user_id": "user-1",
            "stripe_customer_id": "cus_active",
            "status": "active",
        }
        select_chain = _make_supabase_chain([active_row])
        service._supabase.table.return_value = select_chain

        with pytest.raises(BillingError, match="already have an active subscription"):
            await service.create_checkout_session("user-1", "user@test.com", "student")

    async def test_raises_on_missing_session_url(self, service):
        """Stripe session with url=None raises BillingError."""
        select_chain = _make_supabase_chain([])
        insert_chain = _make_supabase_insert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return insert_chain

        service._supabase.table.side_effect = table_side_effect
        service._stripe.v1.customers.create.return_value = MagicMock(id="cus_123")
        service._stripe.v1.checkout.sessions.create.return_value = MagicMock(url=None)

        with pytest.raises(BillingError, match="Failed to create checkout session"):
            await service.create_checkout_session("user-1", "user@test.com", "student")


# =========================================================================
# get_subscription_status
# =========================================================================


class TestGetSubscriptionStatus:
    async def test_returns_active_status(self, service):
        """Active row -> is_active=True."""
        active_row = {
            "user_id": "user-1",
            "status": "active",
            "current_period_end": "2026-04-12T00:00:00Z",
        }
        select_chain = _make_supabase_chain([active_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_subscription_status("user-1")

        assert result["status"] == "active"
        assert result["is_active"] is True
        assert result["current_period_end"] == "2026-04-12T00:00:00Z"

    async def test_returns_inactive_when_no_row(self, service):
        """No subscription row -> inactive, is_active=False."""
        select_chain = _make_supabase_chain([])
        service._supabase.table.return_value = select_chain

        result = await service.get_subscription_status("user-no-sub")

        assert result["status"] == "inactive"
        assert result["is_active"] is False
        assert result["current_period_end"] is None

    async def test_returns_inactive_for_expired(self, service):
        """Expired row -> is_active=False."""
        expired_row = {
            "user_id": "user-1",
            "status": "expired",
            "current_period_end": "2026-01-01T00:00:00Z",
        }
        select_chain = _make_supabase_chain([expired_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_subscription_status("user-1")

        assert result["status"] == "expired"
        assert result["is_active"] is False


# =========================================================================
# cancel_subscription
# =========================================================================


class TestCancelSubscription:
    async def test_cancels_active_subscription(self, service):
        """Active sub with stripe_subscription_id -> calls Stripe cancel at period end."""
        active_row = {
            "user_id": "user-1",
            "status": "active",
            "stripe_subscription_id": "sub_cancel_123",
        }
        select_chain = _make_supabase_chain([active_row])
        service._supabase.table.return_value = select_chain
        service._stripe.v1.subscriptions.update.return_value = MagicMock()

        result = await service.cancel_subscription("user-1")

        assert result["cancel_at_period_end"] is True
        service._stripe.v1.subscriptions.update.assert_called_once_with(
            "sub_cancel_123", {"cancel_at_period_end": True}
        )

    async def test_raises_when_no_subscription(self, service):
        """No subscription row -> NoActiveSubscriptionError."""
        select_chain = _make_supabase_chain([])
        service._supabase.table.return_value = select_chain

        with pytest.raises(NoActiveSubscriptionError):
            await service.cancel_subscription("user-1")

    async def test_raises_when_not_active(self, service):
        """Expired subscription -> NoActiveSubscriptionError."""
        expired_row = {
            "user_id": "user-1",
            "status": "expired",
            "stripe_subscription_id": "sub_expired",
        }
        select_chain = _make_supabase_chain([expired_row])
        service._supabase.table.return_value = select_chain

        with pytest.raises(NoActiveSubscriptionError):
            await service.cancel_subscription("user-1")


# =========================================================================
# handle_webhook
# =========================================================================


class TestHandleWebhook:
    async def test_valid_signature_dispatches_handler(self, service):
        """Valid signature -> event dispatched to correct handler."""
        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"

        with patch("app.services.billing.stripe.Webhook.construct_event", return_value=mock_event):
            with patch.object(
                service, "_handle_checkout_completed", new_callable=AsyncMock
            ) as mock_handler:
                await service.handle_webhook(b"payload", "sig_test")
                mock_handler.assert_called_once_with(mock_event)

    async def test_invalid_signature_raises(self, service):
        """Invalid signature -> BillingError."""
        with patch(
            "app.services.billing.stripe.Webhook.construct_event",
            side_effect=stripe.SignatureVerificationError("bad sig", "sig_header"),
        ):
            with pytest.raises(BillingError, match="Invalid webhook signature"):
                await service.handle_webhook(b"payload", "bad_sig")

    async def test_unknown_event_type_logged(self, service):
        """Unknown event type -> no crash, just logged."""
        mock_event = MagicMock()
        mock_event.type = "some.unknown.event"

        with patch("app.services.billing.stripe.Webhook.construct_event", return_value=mock_event):
            # Should not raise
            await service.handle_webhook(b"payload", "sig_test")


# =========================================================================
# Webhook handlers
# =========================================================================


class TestWebhookHandlers:
    async def test_checkout_completed_activates_subscription(self, service):
        """checkout.session.completed -> upsert subscription with status=active."""
        mock_event = MagicMock()
        session_data = {
            "customer": "cus_123",
            "subscription": "sub_123",
            "metadata": {"user_id": "user-1"},
        }
        mock_event.data.object.to_dict_recursive.return_value = session_data

        # Idempotency check: no existing stripe_subscription_id
        select_chain = _make_supabase_chain([{"stripe_subscription_id": None}])
        upsert_chain = _make_supabase_upsert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain  # idempotency check
            return upsert_chain  # upsert

        service._supabase.table.side_effect = table_side_effect

        # Mock Stripe subscription retrieve
        mock_sub = MagicMock()
        mock_sub.current_period_end = 1712880000  # 2024-04-12T00:00:00Z
        mock_sub.current_period_start = 1710288000  # 2024-03-13T00:00:00Z
        service._stripe.v1.subscriptions.retrieve.return_value = mock_sub

        await service._handle_checkout_completed(mock_event)

        service._stripe.v1.subscriptions.retrieve.assert_called_once_with("sub_123")
        # Verify upsert was called (second table call)
        assert call_count == 2

    async def test_checkout_completed_idempotent(self, service):
        """Already-processed subscription_id -> handler returns early, no Stripe API call."""
        mock_event = MagicMock()
        session_data = {
            "customer": "cus_123",
            "subscription": "sub_123",
            "metadata": {"user_id": "user-1"},
        }
        mock_event.data.object.to_dict_recursive.return_value = session_data

        # Idempotency check: existing row already has this subscription_id
        select_chain = _make_supabase_chain([{"stripe_subscription_id": "sub_123"}])
        service._supabase.table.return_value = select_chain

        await service._handle_checkout_completed(mock_event)

        # Stripe should NOT be called since it was already processed
        service._stripe.v1.subscriptions.retrieve.assert_not_called()

    async def test_payment_succeeded_updates_status(self, service):
        """invoice.payment_succeeded -> update subscription to active."""
        mock_event = MagicMock()
        invoice_data = {
            "subscription": "sub_pay_123",
            "customer": "cus_pay_123",
        }
        mock_event.data.object.to_dict_recursive.return_value = invoice_data

        # Mock Stripe subscription retrieve for period dates
        mock_sub = MagicMock()
        mock_sub.current_period_end = 1712880000
        mock_sub.current_period_start = 1710288000
        service._stripe.v1.subscriptions.retrieve.return_value = mock_sub

        update_chain = _make_supabase_update_chain()
        service._supabase.table.return_value = update_chain

        await service._handle_payment_succeeded(mock_event)

        service._stripe.v1.subscriptions.retrieve.assert_called_once_with("sub_pay_123")
        # Verify update was called with "active"
        update_call_args = update_chain.update.call_args[0][0]
        assert update_call_args["status"] == "active"

    async def test_payment_failed_sets_past_due(self, service):
        """invoice.payment_failed -> update subscription to past_due."""
        mock_event = MagicMock()
        invoice_data = {
            "subscription": "sub_fail_123",
        }
        mock_event.data.object.to_dict_recursive.return_value = invoice_data

        # First call: idempotency check (status is active, not expired)
        select_chain = _make_supabase_chain([{"status": "active"}])
        # Second call: update to past_due
        update_chain = _make_supabase_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service._handle_payment_failed(mock_event)

        update_call_args = update_chain.update.call_args[0][0]
        assert update_call_args["status"] == "past_due"

    async def test_payment_failed_skips_if_already_expired(self, service):
        """invoice.payment_failed -> skip if subscription already expired (out-of-order)."""
        mock_event = MagicMock()
        invoice_data = {
            "subscription": "sub_fail_expired",
        }
        mock_event.data.object.to_dict_recursive.return_value = invoice_data

        # Idempotency check: subscription is already expired
        select_chain = _make_supabase_chain([{"status": "expired"}])
        service._supabase.table.return_value = select_chain

        await service._handle_payment_failed(mock_event)

        # Should NOT have called update (only 1 table call for the select)
        assert service._supabase.table.call_count == 1

    async def test_subscription_updated_maps_status(self, service):
        """customer.subscription.updated with status=canceled -> maps to expired."""
        mock_event = MagicMock()
        sub_data = {
            "id": "sub_updated_123",
            "status": "canceled",
            "current_period_end": 1712880000,
            "current_period_start": 1710288000,
        }
        mock_event.data.object.to_dict_recursive.return_value = sub_data

        # First call: idempotency check (status is active, not expired)
        select_chain = _make_supabase_chain([{"status": "active"}])
        # Second call: update
        update_chain = _make_supabase_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service._handle_subscription_updated(mock_event)

        update_call_args = update_chain.update.call_args[0][0]
        assert update_call_args["status"] == "expired"

    async def test_subscription_updated_skips_if_expired_and_not_active(self, service):
        """customer.subscription.updated -> skip non-active update if already expired."""
        mock_event = MagicMock()
        sub_data = {
            "id": "sub_updated_expired",
            "status": "past_due",
            "current_period_end": 1712880000,
            "current_period_start": 1710288000,
        }
        mock_event.data.object.to_dict_recursive.return_value = sub_data

        # Idempotency check: subscription is already expired
        select_chain = _make_supabase_chain([{"status": "expired"}])
        service._supabase.table.return_value = select_chain

        await service._handle_subscription_updated(mock_event)

        # Should NOT have called update (only 1 table call for the select)
        assert service._supabase.table.call_count == 1

    async def test_subscription_updated_allows_active_even_if_expired(self, service):
        """customer.subscription.updated -> allow reactivation from expired to active."""
        mock_event = MagicMock()
        sub_data = {
            "id": "sub_reactivated",
            "status": "active",
            "current_period_end": 1712880000,
            "current_period_start": 1710288000,
        }
        mock_event.data.object.to_dict_recursive.return_value = sub_data

        # Idempotency check: subscription is expired
        select_chain = _make_supabase_chain([{"status": "expired"}])
        # Second call: update to active (allowed)
        update_chain = _make_supabase_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service._handle_subscription_updated(mock_event)

        # Should have called update (reactivation is allowed)
        update_call_args = update_chain.update.call_args[0][0]
        assert update_call_args["status"] == "active"

    async def test_subscription_deleted_sets_expired(self, service):
        """customer.subscription.deleted -> set status to expired."""
        mock_event = MagicMock()
        sub_data = {
            "id": "sub_deleted_123",
        }
        mock_event.data.object.to_dict_recursive.return_value = sub_data

        update_chain = _make_supabase_update_chain()
        service._supabase.table.return_value = update_chain

        await service._handle_subscription_deleted(mock_event)

        update_call_args = update_chain.update.call_args[0][0]
        assert update_call_args["status"] == "expired"


# =========================================================================
# cleanup_user
# =========================================================================


class TestCleanupUser:
    async def test_cancels_subscription_and_deletes_customer(self, service):
        """User with sub + customer -> both Stripe calls made."""
        sub_row = {
            "user_id": "user-1",
            "stripe_subscription_id": "sub_cleanup_123",
            "stripe_customer_id": "cus_cleanup_123",
        }
        select_chain = _make_supabase_chain([sub_row])
        service._supabase.table.return_value = select_chain

        service._stripe.v1.subscriptions.cancel.return_value = MagicMock()
        service._stripe.v1.customers.delete.return_value = MagicMock()

        await service.cleanup_user("user-1")

        service._stripe.v1.subscriptions.cancel.assert_called_once_with("sub_cleanup_123")
        service._stripe.v1.customers.delete.assert_called_once_with("cus_cleanup_123")

    async def test_no_op_when_no_subscription(self, service):
        """No subscription row -> no Stripe calls."""
        select_chain = _make_supabase_chain([])
        service._supabase.table.return_value = select_chain

        await service.cleanup_user("user-no-sub")

        service._stripe.v1.subscriptions.cancel.assert_not_called()
        service._stripe.v1.customers.delete.assert_not_called()

    async def test_continues_on_stripe_error(self, service):
        """Stripe cancel fails -> customer delete still attempted."""
        sub_row = {
            "user_id": "user-1",
            "stripe_subscription_id": "sub_err_123",
            "stripe_customer_id": "cus_err_123",
        }
        select_chain = _make_supabase_chain([sub_row])
        service._supabase.table.return_value = select_chain

        service._stripe.v1.subscriptions.cancel.side_effect = Exception("Stripe API error")
        service._stripe.v1.customers.delete.return_value = MagicMock()

        await service.cleanup_user("user-1")

        # cancel was attempted and raised
        service._stripe.v1.subscriptions.cancel.assert_called_once_with("sub_err_123")
        # delete was still called despite the cancel error
        service._stripe.v1.customers.delete.assert_called_once_with("cus_err_123")


# =========================================================================
# Plan-aware checkout
# =========================================================================


class TestPlanAwareCheckout:
    async def test_checkout_student_uses_student_price(self, service):
        """plan='student' -> line_items price = stripe_student_price_id."""
        select_chain = _make_supabase_chain([])
        insert_chain = _make_supabase_insert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return insert_chain

        service._supabase.table.side_effect = table_side_effect
        service._stripe.v1.customers.create.return_value = MagicMock(id="cus_stu_1")
        service._stripe.v1.checkout.sessions.create.return_value = MagicMock(
            url="https://checkout.stripe.com/student_session"
        )

        url = await service.create_checkout_session("user-1", "u@t.com", "student")

        assert url == "https://checkout.stripe.com/student_session"
        create_args = service._stripe.v1.checkout.sessions.create.call_args[0][0]
        assert create_args["line_items"] == [{"price": "price_student_test123", "quantity": 1}]

    async def test_checkout_tutor_uses_tutor_price(self, service):
        """plan='tutor' -> line_items price = stripe_tutor_price_id."""
        select_chain = _make_supabase_chain([])
        insert_chain = _make_supabase_insert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return insert_chain

        service._supabase.table.side_effect = table_side_effect
        service._stripe.v1.customers.create.return_value = MagicMock(id="cus_tut_1")
        service._stripe.v1.checkout.sessions.create.return_value = MagicMock(
            url="https://checkout.stripe.com/tutor_session"
        )

        url = await service.create_checkout_session("user-1", "u@t.com", "tutor")

        assert url == "https://checkout.stripe.com/tutor_session"
        create_args = service._stripe.v1.checkout.sessions.create.call_args[0][0]
        assert create_args["line_items"] == [{"price": "price_tutor_test123", "quantity": 1}]

    async def test_checkout_invalid_plan_raises_error(self, service):
        """plan='invalid' -> BillingError raised."""
        with pytest.raises(BillingError, match="Unknown plan: invalid"):
            await service.create_checkout_session("user-1", "u@t.com", "invalid")

    async def test_subscription_status_includes_plan(self, service):
        """Subscription row with plan='tutor' -> returned dict has plan='tutor'."""
        tutor_row = {
            "user_id": "user-1",
            "status": "active",
            "current_period_end": "2026-04-12T00:00:00Z",
            "plan": "tutor",
        }
        select_chain = _make_supabase_chain([tutor_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_subscription_status("user-1")

        assert result["plan"] == "tutor"
        assert result["is_active"] is True

    async def test_checkout_webhook_stores_plan(self, service):
        """checkout.session.completed with plan='tutor' metadata stores plan."""
        mock_event = MagicMock()
        session_data = {
            "customer": "cus_tutor_123",
            "subscription": "sub_tutor_123",
            "metadata": {"user_id": "user-tutor", "plan": "tutor"},
        }
        mock_event.data.object.to_dict_recursive.return_value = session_data

        # Idempotency check: no existing stripe_subscription_id
        select_chain = _make_supabase_chain([{"stripe_subscription_id": None}])
        upsert_chain = _make_supabase_upsert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return upsert_chain

        service._supabase.table.side_effect = table_side_effect

        # Mock Stripe subscription retrieve
        mock_sub = MagicMock()
        mock_sub.current_period_end = 1712880000
        mock_sub.current_period_start = 1710288000
        service._stripe.v1.subscriptions.retrieve.return_value = mock_sub

        await service._handle_checkout_completed(mock_event)

        # Verify the upsert was called with plan='tutor'
        upsert_call_args = upsert_chain.upsert.call_args[0][0]
        assert upsert_call_args["plan"] == "tutor"
        assert upsert_call_args["status"] == "active"
        assert upsert_call_args["user_id"] == "user-tutor"
