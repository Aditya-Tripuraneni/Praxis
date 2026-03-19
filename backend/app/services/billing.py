"""Billing service -- wraps Stripe and Supabase subscriptions table.

Note: Both Stripe and Supabase Python clients are synchronous. All calls are
wrapped in asyncio.to_thread() to avoid blocking the FastAPI event loop.
"""

import asyncio
import logging
from datetime import datetime, timezone

import httpx
import stripe
from supabase import Client, ClientOptions, create_client

from app.config import settings

logger = logging.getLogger(__name__)


class BillingError(Exception):
    """General billing error."""


class NoActiveSubscriptionError(Exception):
    """User has no active subscription."""


def _create_service_client() -> Client | None:
    """Create Supabase client with service role key (same pattern as auth.py)."""
    if settings.supabase_url and settings.supabase_service_role_key:
        options = ClientOptions(httpx_client=httpx.Client(timeout=120, verify=True))
        return create_client(settings.supabase_url, settings.supabase_service_role_key, options)
    return None


PLAN_PRICES = {
    "student": settings.stripe_student_price_id,
    "tutor": settings.stripe_tutor_price_id,
}


class BillingService:
    """Wraps Stripe billing + Supabase subscriptions table operations."""

    def __init__(self) -> None:
        self._supabase = _create_service_client()
        self._stripe: stripe.StripeClient | None = None
        if settings.stripe_secret_key:
            if not settings.stripe_webhook_secret:
                raise RuntimeError(
                    "STRIPE_SECRET_KEY is set but STRIPE_WEBHOOK_SECRET is missing. "
                    "Both must be configured for billing to work."
                )
            if not settings.stripe_student_price_id:
                logger.warning(
                    "STRIPE_SECRET_KEY is set but STRIPE_STUDENT_PRICE_ID is missing. "
                    "Student checkout will not work until configured."
                )
            if not settings.stripe_tutor_price_id:
                logger.warning(
                    "STRIPE_SECRET_KEY is set but STRIPE_TUTOR_PRICE_ID is missing. "
                    "Tutor checkout will not work until configured."
                )
            self._stripe = stripe.StripeClient(settings.stripe_secret_key)

    @property
    def supabase(self) -> Client:
        """Supabase client for subscription data."""
        if self._supabase is None:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._supabase

    @property
    def stripe_client(self) -> stripe.StripeClient:
        """Stripe client for billing operations."""
        if self._stripe is None:
            raise RuntimeError("Stripe not configured. Set STRIPE_SECRET_KEY.")
        return self._stripe

    async def create_checkout_session(self, user_id: str, email: str, plan: str) -> str:
        """Create a Stripe Checkout Session. Returns the session URL."""
        price_id = PLAN_PRICES.get(plan)
        if not price_id:
            raise BillingError(f"Unknown plan: {plan}")
        # Check for existing customer in subscriptions table
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
            )
        )

        if result.data:
            sub = result.data[0]
            if sub.get("status") == "active":
                raise BillingError("You already have an active subscription")
            stripe_customer_id = sub.get("stripe_customer_id")
        else:
            # Create new Stripe Customer
            customer = await asyncio.to_thread(
                lambda: self.stripe_client.v1.customers.create(
                    {
                        "email": email,
                        "metadata": {"user_id": user_id},
                    }
                )
            )
            stripe_customer_id = customer.id

            # Insert initial subscription row
            await asyncio.to_thread(
                lambda: (
                    self.supabase.table("subscriptions")
                    .insert(
                        {
                            "user_id": user_id,
                            "stripe_customer_id": stripe_customer_id,
                            "status": "inactive",
                            "plan": plan,
                        }
                    )
                    .execute()
                )
            )

        # Create Checkout Session
        session = await asyncio.to_thread(
            lambda: self.stripe_client.v1.checkout.sessions.create(
                {
                    "customer": stripe_customer_id,
                    "line_items": [{"price": price_id, "quantity": 1}],
                    "mode": "subscription",
                    "success_url": (
                        f"{settings.frontend_url}/checkout/success"
                        f"?session_id={{CHECKOUT_SESSION_ID}}"
                    ),
                    "cancel_url": f"{settings.frontend_url}/checkout/cancel",
                    "metadata": {"user_id": user_id, "plan": plan},
                }
            )
        )

        if not session.url:
            raise BillingError("Failed to create checkout session")

        return session.url

    async def get_subscription_status(self, user_id: str) -> dict:
        """Get subscription status for a user."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
            )
        )

        if not result.data:
            return {
                "status": "inactive",
                "is_active": False,
                "current_period_end": None,
                "plan": None,
            }

        sub = result.data[0]
        status = sub.get("status", "inactive")
        return {
            "status": status,
            "is_active": status == "active",
            "current_period_end": sub.get("current_period_end"),
            "plan": sub.get("plan", "student"),
        }

    async def cancel_subscription(self, user_id: str) -> dict:
        """Cancel subscription at end of billing period."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
            )
        )

        if not result.data:
            raise NoActiveSubscriptionError("No active subscription found")

        sub = result.data[0]
        if sub.get("status") != "active":
            raise NoActiveSubscriptionError("No active subscription found")

        stripe_sub_id = sub.get("stripe_subscription_id")
        if not stripe_sub_id:
            raise NoActiveSubscriptionError("No active subscription found")

        # Cancel at period end (not immediately)
        await asyncio.to_thread(
            lambda: self.stripe_client.v1.subscriptions.update(
                stripe_sub_id, {"cancel_at_period_end": True}
            )
        )

        return {
            "message": "Subscription will cancel at end of billing period",
            "cancel_at_period_end": True,
        }

    @staticmethod
    def _to_dict(obj: object) -> dict:
        """Convert a Stripe resource object to a plain dict safely."""
        if hasattr(obj, "to_dict_recursive"):
            return obj.to_dict_recursive()
        return dict(obj)

    @staticmethod
    def _extract_period_dates(data: dict) -> tuple[str | None, str | None]:
        """Extract ISO-formatted period start/end from a Stripe subscription dict."""
        start = data.get("current_period_start")
        end = data.get("current_period_end")
        return (
            datetime.fromtimestamp(start, tz=timezone.utc).isoformat() if start else None,
            datetime.fromtimestamp(end, tz=timezone.utc).isoformat() if end else None,
        )

    async def _retrieve_subscription_data(self, subscription_id: str) -> dict:
        """Retrieve a Stripe subscription as a plain dict."""
        obj = await asyncio.to_thread(
            lambda: self.stripe_client.v1.subscriptions.retrieve(subscription_id)
        )
        return self._to_dict(obj)

    async def handle_webhook(self, payload: bytes, signature: str) -> None:
        """Verify and process a Stripe webhook event."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.stripe_webhook_secret
            )
        except stripe.SignatureVerificationError:
            raise BillingError("Invalid webhook signature")

        event_type = event.type
        logger.info("Stripe webhook received: %s", event_type)

        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
        }

        handler = handlers.get(event_type)
        if handler:
            await handler(event)
        else:
            logger.info("Unhandled webhook event type: %s", event_type)

    async def _handle_checkout_completed(self, event: stripe.Event) -> None:
        """Handle checkout.session.completed -- activate subscription."""
        session_data = self._to_dict(event.data.object)
        customer_id = session_data.get("customer")
        subscription_id = session_data.get("subscription")
        user_id = session_data.get("metadata", {}).get("user_id")
        plan = session_data.get("metadata", {}).get("plan", "student")

        if not user_id or not subscription_id:
            logger.warning("Checkout completed missing user_id or subscription_id")
            return

        # Idempotency guard — skip if already processed
        existing = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .select("stripe_subscription_id")
                .eq("user_id", user_id)
                .execute()
            )
        )
        if existing.data and existing.data[0].get("stripe_subscription_id") == subscription_id:
            logger.info("Checkout already processed for user %s, skipping", user_id)
            return

        sub_data = await self._retrieve_subscription_data(subscription_id)
        period_start, period_end = self._extract_period_dates(sub_data)

        await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .upsert(
                    {
                        "user_id": user_id,
                        "stripe_customer_id": customer_id,
                        "stripe_subscription_id": subscription_id,
                        "status": "active",
                        "current_period_start": period_start,
                        "current_period_end": period_end,
                        "plan": plan,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    on_conflict="user_id",
                )
                .execute()
            )
        )
        logger.info("Subscription activated for user %s", user_id)

    async def _handle_payment_succeeded(self, event: stripe.Event) -> None:
        """Handle invoice.payment_succeeded -- renew subscription."""
        invoice_data = self._to_dict(event.data.object)
        subscription_id = invoice_data.get("subscription")

        if not subscription_id:
            return

        sub_data = await self._retrieve_subscription_data(subscription_id)
        period_start, period_end = self._extract_period_dates(sub_data)

        await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .update(
                    {
                        "status": "active",
                        "current_period_start": period_start,
                        "current_period_end": period_end,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("stripe_subscription_id", subscription_id)
                .execute()
            )
        )
        logger.info("Payment succeeded for subscription %s", subscription_id)

    async def _handle_payment_failed(self, event: stripe.Event) -> None:
        """Handle invoice.payment_failed -- mark subscription as past_due."""
        invoice_data = self._to_dict(event.data.object)
        subscription_id = invoice_data.get("subscription")

        if not subscription_id:
            return

        # Don't downgrade from expired to past_due (out-of-order event)
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .select("status")
                .eq("stripe_subscription_id", subscription_id)
                .execute()
            )
        )
        if result.data and result.data[0].get("status") == "expired":
            logger.info("Subscription %s already expired, skipping past_due", subscription_id)
            return

        await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .update(
                    {
                        "status": "past_due",
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("stripe_subscription_id", subscription_id)
                .execute()
            )
        )
        logger.warning("Payment failed for subscription %s", subscription_id)

    async def _handle_subscription_updated(self, event: stripe.Event) -> None:
        """Handle customer.subscription.updated -- sync status + period."""
        sub_data = self._to_dict(event.data.object)
        subscription_id = sub_data.get("id")
        status = sub_data.get("status")

        if not subscription_id:
            return

        # Derive plan from subscription items
        plan = "student"  # default
        items_data = sub_data.get("items", {})
        if isinstance(items_data, dict):
            items_list = items_data.get("data", [])
        elif isinstance(items_data, list):
            items_list = items_data
        else:
            items_list = []
        if items_list:
            price_id = items_list[0].get("price", {}).get("id", "")
            if price_id == settings.stripe_tutor_price_id:
                plan = "tutor"

        # Map Stripe statuses to our simplified statuses
        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "expired",
            "unpaid": "past_due",
            "incomplete": "inactive",
            "incomplete_expired": "expired",
            "trialing": "active",
        }
        mapped_status = status_map.get(status, "inactive")
        period_start, period_end = self._extract_period_dates(sub_data)

        # Don't override if already in a more terminal state
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .select("status")
                .eq("stripe_subscription_id", subscription_id)
                .execute()
            )
        )
        if result.data:
            current = result.data[0].get("status")
            if current == "expired" and mapped_status != "active":
                logger.info(
                    "Subscription %s is expired, ignoring %s update",
                    subscription_id,
                    mapped_status,
                )
                return

        await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .update(
                    {
                        "status": mapped_status,
                        "current_period_start": period_start,
                        "current_period_end": period_end,
                        "plan": plan,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("stripe_subscription_id", subscription_id)
                .execute()
            )
        )
        logger.info("Subscription %s updated to status %s", subscription_id, mapped_status)

    async def _handle_subscription_deleted(self, event: stripe.Event) -> None:
        """Handle customer.subscription.deleted -- mark as expired."""
        sub_data = self._to_dict(event.data.object)
        subscription_id = sub_data.get("id")

        if not subscription_id:
            return

        await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions")
                .update(
                    {
                        "status": "expired",
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("stripe_subscription_id", subscription_id)
                .execute()
            )
        )
        logger.info("Subscription %s deleted (expired)", subscription_id)

    async def cleanup_user(self, user_id: str) -> None:
        """Cancel subscription and delete Stripe customer for account deletion."""
        result = await asyncio.to_thread(
            lambda: (
                self.supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
            )
        )
        if not result.data:
            return

        sub = result.data[0]
        stripe_sub_id = sub.get("stripe_subscription_id")
        stripe_customer_id = sub.get("stripe_customer_id")

        # Cancel subscription immediately (not at period end)
        if stripe_sub_id:
            try:
                await asyncio.to_thread(
                    lambda: self.stripe_client.v1.subscriptions.cancel(stripe_sub_id)
                )
            except Exception:
                logger.warning("Failed to cancel Stripe subscription %s", stripe_sub_id)

        # Delete customer
        if stripe_customer_id:
            try:
                await asyncio.to_thread(
                    lambda: self.stripe_client.v1.customers.delete(stripe_customer_id)
                )
            except Exception:
                logger.warning("Failed to delete Stripe customer %s", stripe_customer_id)


billing_service = BillingService()
