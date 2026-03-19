"""Billing API endpoints -- Stripe checkout, subscription status, webhooks."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import AuthenticatedUser, get_current_user
from app.models.billing import (
    CancelSubscriptionResponse,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionStatus,
)
from app.rate_limiter import limiter
from app.security_logging import log_auth_event
from app.services.billing import (
    BillingError,
    NoActiveSubscriptionError,
    billing_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
@limiter.limit("10/hour")
async def create_checkout_session(
    body: CheckoutSessionRequest,
    request: Request,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    try:
        url = await billing_service.create_checkout_session(
            auth.profile.id, auth.profile.email, body.plan
        )
        client_ip = request.client.host if request.client else ""
        log_auth_event("BILLING_CHECKOUT_CREATED", user_id=auth.profile.id, ip=client_ip)
        return CheckoutSessionResponse(url=url)
    except BillingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to create checkout session")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.get("/subscription-status", response_model=SubscriptionStatus)
@limiter.limit("30/minute")
async def subscription_status(
    request: Request,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    try:
        status = await billing_service.get_subscription_status(auth.profile.id)
        return SubscriptionStatus(**status)
    except Exception:
        logger.exception("Failed to get subscription status")
        raise HTTPException(status_code=500, detail="Failed to get subscription status")


@router.post("/cancel-subscription", response_model=CancelSubscriptionResponse)
@limiter.limit("3/hour")
async def cancel_subscription(
    request: Request,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    try:
        result = await billing_service.cancel_subscription(auth.profile.id)
        client_ip = request.client.host if request.client else ""
        log_auth_event("BILLING_SUBSCRIPTION_CANCELLED", user_id=auth.profile.id, ip=client_ip)
        return CancelSubscriptionResponse(**result)
    except NoActiveSubscriptionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to cancel subscription")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        await billing_service.handle_webhook(payload, signature)
    except BillingError:
        client_ip = request.client.host if request.client else ""
        log_auth_event("BILLING_WEBHOOK_INVALID_SIG", ip=client_ip, success=False)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception:
        logger.exception("Webhook processing error")
        # Return 200 to acknowledge receipt — Stripe retries on non-2xx, which
        # creates retry storms for persistent bugs. Errors are logged above for
        # async investigation. Invalid signatures still return 400 (correct per
        # Stripe docs).
        return {"status": "received"}

    return {"status": "ok"}
