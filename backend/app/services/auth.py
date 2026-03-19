"""Authentication service -- wraps Supabase Auth and HIBP password checking.

Note: Supabase Python client is synchronous. All Supabase calls are wrapped
in asyncio.to_thread() to avoid blocking the FastAPI event loop.
"""

import asyncio
import hashlib
import logging

import httpx
from supabase import Client, ClientOptions, create_client

from app.config import settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when login credentials are invalid or user is unverified."""


class UserExistsError(Exception):
    """Raised when a signup email is already registered."""


class InvalidTokenError(Exception):
    """Raised when a JWT or refresh token is invalid/expired."""


class BreachedPasswordError(Exception):
    """Raised when a password is found in the HIBP breached database."""


def _create_service_client() -> Client | None:
    """Create Supabase client with service role key.

    NOTE: The Supabase Python SDK does not support the newer publishable
    key format (sb_publishable_...) for auth operations like
    sign_in_with_password. All auth operations must use the service role
    key. This is a known SDK limitation — the publishable key works with
    supabase-js (frontend) but not supabase-py (backend).
    """
    if settings.supabase_url and settings.supabase_service_role_key:
        options = ClientOptions(httpx_client=httpx.Client(timeout=120, verify=True))
        return create_client(settings.supabase_url, settings.supabase_service_role_key, options)
    return None


class AuthService:
    """Wraps Supabase Auth operations with password security checks."""

    def __init__(self) -> None:
        self._client = _create_service_client()

    @property
    def client(self) -> Client:
        """Supabase client for all auth operations."""
        if self._client is None:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._client

    async def signup(self, email: str, password: str) -> str:
        """Register a new user. Returns success message.

        Anti-enumeration: returns same message whether email is new or exists.
        """
        if await self.check_password_breached(password):
            raise BreachedPasswordError(
                "This password has been found in a data breach. "
                "Please choose a different password."
            )

        try:
            await asyncio.to_thread(
                self.client.auth.sign_up, {"email": email, "password": password}
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "already registered" in error_msg or "already exists" in error_msg:
                logger.info("Signup attempt for existing email (suppressed)")
                return "Account created. Please check your email to verify your account."
            raise

        return "Account created. Please check your email to verify your account."

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user. Returns tokens + user profile.

        Always returns generic error for any failure (anti-enumeration).
        """
        try:
            response = await asyncio.to_thread(
                self.client.auth.sign_in_with_password,
                {"email": email, "password": password},
            )
        except Exception:
            raise AuthenticationError("Invalid email or password")

        if not response.session:
            raise AuthenticationError("Invalid email or password")

        user = response.user
        if not user:
            raise AuthenticationError("Invalid email or password")

        if not user.email_confirmed_at:
            raise AuthenticationError("Invalid email or password")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in or 900,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None,
                "created_at": str(user.created_at) if user.created_at else None,
            },
        }

    async def refresh(self, refresh_token: str) -> dict:
        """Exchange refresh token for new access token."""
        try:
            response = await asyncio.to_thread(self.client.auth.refresh_session, refresh_token)
        except Exception:
            raise InvalidTokenError("Invalid or expired refresh token")

        if not response.session:
            raise InvalidTokenError("Invalid or expired refresh token")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in or 900,
            "token_type": "bearer",
        }

    async def logout(self, access_token: str) -> None:
        """Invalidate the current session."""
        try:
            await asyncio.to_thread(self.client.auth.sign_out, access_token)
        except Exception:
            logger.warning("Logout failed (token may already be invalid)")

    async def get_user(self, access_token: str) -> dict:
        """Get user profile from access token."""
        try:
            response = await asyncio.to_thread(self.client.auth.get_user, access_token)
        except Exception:
            raise InvalidTokenError("Invalid or expired token")

        if not response.user:
            raise InvalidTokenError("Invalid or expired token")

        user = response.user
        return {
            "id": user.id,
            "email": user.email,
            "email_verified": user.email_confirmed_at is not None,
            "created_at": str(user.created_at) if user.created_at else None,
        }

    async def delete_user(self, user_id: str) -> None:
        """Delete user account — cancels Stripe subscription first."""
        # Cancel Stripe subscription if exists
        try:
            from app.services.billing import billing_service

            await billing_service.cleanup_user(user_id)
        except Exception:
            logger.warning("Stripe cleanup failed for user %s (continuing deletion)", user_id)

        # Delete Supabase Auth user (subscription row cascades via ON DELETE CASCADE)
        try:
            await asyncio.to_thread(self.client.auth.admin.delete_user, user_id)
        except Exception:
            logger.exception("Failed to delete user %s", user_id)
            raise

    async def resend_verification(self, email: str) -> str:
        """Resend verification email. Anti-enumeration: same message always."""
        try:
            await asyncio.to_thread(self.client.auth.resend, {"type": "signup", "email": email})
        except Exception:
            logger.info("Resend verification for unknown email (suppressed)")
        return "If an account exists with this email, a verification link has been sent."

    async def verify_email(self, email: str, token: str) -> dict:
        """Verify email with 6-digit OTP code. Returns tokens + user on success."""
        try:
            response = await asyncio.to_thread(
                self.client.auth.verify_otp,
                {"email": email, "token": token, "type": "email"},
            )
        except Exception:
            raise AuthenticationError("Invalid or expired verification code")

        if not response.session or not response.user:
            raise AuthenticationError("Invalid or expired verification code")

        user = response.user
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in or 900,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None,
                "created_at": str(user.created_at) if user.created_at else None,
            },
        }

    async def forgot_password(self, email: str) -> str:
        """Send password reset email. Anti-enumeration: same message always."""
        try:
            await asyncio.to_thread(self.client.auth.reset_password_for_email, email)
        except Exception:
            logger.info("Password reset for unknown email (suppressed)")
        return "If an account exists with this email, a password reset link has been sent."

    async def reset_password(self, email: str, token: str, new_password: str) -> dict:
        """Reset password using OTP token. Checks HIBP, then updates password."""
        if await self.check_password_breached(new_password):
            raise BreachedPasswordError(
                "This password has been found in a data breach. "
                "Please choose a different password."
            )

        try:
            response = await asyncio.to_thread(
                self.client.auth.verify_otp,
                {"email": email, "token": token, "type": "recovery"},
            )
        except Exception:
            raise AuthenticationError("Invalid or expired reset code")

        if not response.session or not response.user:
            raise AuthenticationError("Invalid or expired reset code")

        # Update password via the SDK's internal _request with the user's
        # JWT from OTP verification. We cannot use update_user() because that
        # operates on the client's current session, and our shared service-role
        # client must not have per-user session state. The jwt= parameter
        # sends the request as the authenticated user without mutating the client.
        try:
            session_token = response.session.access_token
            await asyncio.to_thread(
                self.client.auth._request,
                "PUT",
                "user",
                body={"password": new_password},
                jwt=session_token,
            )
        except Exception:
            logger.exception("Password update failed for user %s", response.user.id)
            raise AuthenticationError("Password reset failed. Please try again.")

        user = response.user
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in or 900,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None,
                "created_at": str(user.created_at) if user.created_at else None,
            },
        }

    async def check_password_breached(self, password: str) -> bool:
        """Check password against HIBP Pwned Passwords API (k-anonymity).

        Returns True if the password has been found in a data breach.
        Returns False if safe, if HIBP is disabled, or if the API is unreachable
        (lenient mode -- never block signups due to third-party outage).
        """
        if not settings.hibp_enabled:
            return False

        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()  # noqa: S324
        prefix, suffix = sha1[:5], sha1[5:]

        try:
            async with httpx.AsyncClient(timeout=settings.hibp_timeout_seconds) as http:
                response = await http.get(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    headers={"User-Agent": "Praxis-PasswordCheck"},
                )
                response.raise_for_status()

            for line in response.text.splitlines():
                parts = line.split(":")
                if len(parts) == 2 and parts[0].strip() == suffix:
                    return True

            return False

        except Exception:
            logger.warning(
                "HIBP API unreachable -- breached password check skipped",
                exc_info=True,
            )
            return False


auth_service = AuthService()
