"""FastAPI dependencies for authentication and subscription checks."""

import logging

from fastapi import Depends, Header, HTTPException

from app.models.auth import UserProfile
from app.services.auth import InvalidTokenError, auth_service

logger = logging.getLogger(__name__)


class AuthenticatedUser:
    """Bundles user profile with the raw access token (needed for logout)."""

    def __init__(self, profile: UserProfile, access_token: str) -> None:
        self.profile = profile
        self.access_token = access_token


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    """Extract and verify JWT from Authorization header.

    Usage: add `auth: AuthenticatedUser = Depends(get_current_user)` to route.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization[7:]  # Strip "Bearer " prefix

    try:
        user_data = await auth_service.get_user(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    except Exception:
        logger.exception("Unexpected error verifying token")
        raise HTTPException(status_code=401, detail="Not authenticated")

    return AuthenticatedUser(profile=UserProfile(**user_data), access_token=token)


async def require_active_subscription(
    auth: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Require both authentication AND active subscription."""
    from app.services.billing import billing_service

    status = await billing_service.get_subscription_status(auth.profile.id)
    if not status.get("is_active", False):
        raise HTTPException(status_code=403, detail="Active subscription required")
    return auth


async def require_tutor_subscription(
    auth: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Require authentication + active subscription + tutor plan."""
    from app.services.billing import billing_service

    status = await billing_service.get_subscription_status(auth.profile.id)
    if not status.get("is_active", False):
        raise HTTPException(status_code=403, detail="Active subscription required")
    if status.get("plan") != "tutor":
        raise HTTPException(status_code=403, detail="Tutor plan required")
    return auth
