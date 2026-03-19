"""Structured security event logging.

Logs security-relevant events in a consistent format for monitoring.
Uses Python's standard logging — no external dependencies.

Events logged:
- AUTH_SIGNUP: new account creation attempt
- AUTH_LOGIN_SUCCESS: successful authentication
- AUTH_LOGIN_FAILURE: failed authentication (wrong credentials, unverified, etc.)
- AUTH_LOGOUT: session invalidation
- AUTH_TOKEN_REFRESH: token refresh
- AUTH_ACCOUNT_DELETED: account deletion
- AUTH_VERIFY_EMAIL: email verification
- RATE_LIMIT_EXCEEDED: rate limit hit (logged by slowapi, not us — documented here)
"""

import logging

logger = logging.getLogger("security")


def log_auth_event(
    event: str,
    *,
    email: str = "",
    user_id: str = "",
    ip: str = "",
    success: bool = True,
    detail: str = "",
) -> None:
    """Log a security-relevant authentication event.

    Args:
        event: Event type (e.g., "AUTH_LOGIN_SUCCESS")
        email: User email (masked for privacy — first 3 chars + domain)
        user_id: User ID (if available)
        ip: Client IP address
        success: Whether the operation succeeded
        detail: Additional context (never include passwords or tokens)
    """
    masked_email = _mask_email(email) if email else ""

    log_data: dict[str, object] = {
        "event": event,
        "success": success,
    }
    if masked_email:
        log_data["email"] = masked_email
    if user_id:
        log_data["user_id"] = user_id
    if ip:
        log_data["ip"] = ip
    if detail:
        log_data["detail"] = detail

    if success:
        logger.info("security_event %s", log_data)
    else:
        logger.warning("security_event %s", log_data)


def _mask_email(email: str) -> str:
    """Mask email for log privacy: show first 3 chars of local part + domain."""
    if "@" not in email:
        return "***"
    local, domain = email.rsplit("@", 1)
    if len(local) <= 3:
        return f"{local}***@{domain}"
    return f"{local[:3]}***@{domain}"
