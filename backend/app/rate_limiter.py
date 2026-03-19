from slowapi import Limiter
from starlette.requests import Request

from app.config import settings


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP from a proxied request.

    Uses ``request.client.host`` as the base (set correctly by Uvicorn when
    ``--proxy-headers`` is enabled). Falls back to parsing X-Forwarded-For
    with ``trusted_proxy_count`` to select the correct entry from the right
    side of the chain, which prevents spoofing via prepended headers.

    Requires Uvicorn to run with ``--proxy-headers --forwarded-allow-ips``
    so that ``request.client.host`` reflects the outermost trusted proxy.
    """
    # Prefer request.client.host — Uvicorn populates this from the last
    # trusted proxy's REMOTE_ADDR when --proxy-headers is configured.
    client_host = request.client.host if request.client else ""

    # If X-Forwarded-For exists, use trusted_proxy_count to pick the
    # correct entry. The rightmost N entries are proxies we trust; the
    # entry just before them is the real client.
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
        # Index of the real client: total entries minus trusted proxies
        client_index = len(ips) - settings.trusted_proxy_count
        if 0 <= client_index < len(ips):
            return ips[client_index]

    return client_host or "127.0.0.1"


limiter = Limiter(key_func=_get_client_ip)
