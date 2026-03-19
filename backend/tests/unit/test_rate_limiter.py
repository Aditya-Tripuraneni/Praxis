"""Unit tests for rate limiter client IP extraction.

X-Forwarded-For convention: each proxy appends the IP of the entity
connecting TO it (the previous hop), NOT its own IP. So:

  Client (203.0.113.50) → Render proxy → Server
  XFF = "203.0.113.50"  (Render added the client's IP)

  Client → Cloudflare (172.16.0.1) → Render → Server
  XFF = "203.0.113.50, 172.16.0.1"  (CF added client, Render added CF)

  Attacker spoofs XFF: "1.1.1.1" → Render → Server
  XFF = "1.1.1.1, 203.0.113.50"  (Render appended real client IP)

With trusted_proxy_count = N, the real client IP is at index len(ips) - N.
"""

from unittest.mock import patch

from app.rate_limiter import _get_client_ip


class FakeClient:
    def __init__(self, host: str):
        self.host = host


class FakeRequest:
    """Minimal request stub for testing IP extraction."""

    def __init__(self, client_host: str = "10.0.0.1", forwarded_for: str = ""):
        self.client = FakeClient(client_host) if client_host else None
        self._headers = {}
        if forwarded_for:
            self._headers["x-forwarded-for"] = forwarded_for

    @property
    def headers(self):
        return self._headers


class TestGetClientIp:
    """Tests for _get_client_ip with various proxy configurations."""

    def test_direct_connection_no_proxy(self):
        """No X-Forwarded-For → use request.client.host."""
        req = FakeRequest(client_host="203.0.113.50")
        assert _get_client_ip(req) == "203.0.113.50"

    @patch("app.rate_limiter.settings")
    def test_single_proxy_no_spoofing(self, mock_settings):
        """Single proxy (Render): XFF = [client_ip] → return client."""
        mock_settings.trusted_proxy_count = 1
        req = FakeRequest(client_host="10.0.0.1", forwarded_for="203.0.113.50")
        assert _get_client_ip(req) == "203.0.113.50"

    @patch("app.rate_limiter.settings")
    def test_single_proxy_with_spoofing(self, mock_settings):
        """Single proxy + attacker spoofed XFF: [fake, real_client] → return real client."""
        mock_settings.trusted_proxy_count = 1
        req = FakeRequest(
            client_host="10.0.0.1",
            forwarded_for="1.1.1.1, 203.0.113.50",
        )
        assert _get_client_ip(req) == "203.0.113.50"

    @patch("app.rate_limiter.settings")
    def test_two_proxies_cloudflare_plus_render(self, mock_settings):
        """Two proxies: XFF = [client, cloudflare_ip] → return client."""
        mock_settings.trusted_proxy_count = 2
        req = FakeRequest(
            client_host="10.0.0.1",
            forwarded_for="203.0.113.50, 172.16.0.1",
        )
        assert _get_client_ip(req) == "203.0.113.50"

    @patch("app.rate_limiter.settings")
    def test_two_proxies_with_spoofing(self, mock_settings):
        """Two proxies + spoofed XFF: [fake, real_client, cf_ip] → return real client."""
        mock_settings.trusted_proxy_count = 2
        req = FakeRequest(
            client_host="10.0.0.1",
            forwarded_for="1.1.1.1, 203.0.113.50, 172.16.0.1",
        )
        assert _get_client_ip(req) == "203.0.113.50"

    @patch("app.rate_limiter.settings")
    def test_spoofed_multiple_fake_ips_ignored(self, mock_settings):
        """Attacker prepends multiple fake IPs — only trusted entries matter."""
        mock_settings.trusted_proxy_count = 1
        req = FakeRequest(
            client_host="10.0.0.1",
            forwarded_for="1.1.1.1, 2.2.2.2, 3.3.3.3, 203.0.113.50",
        )
        assert _get_client_ip(req) == "203.0.113.50"

    def test_no_client_no_xff_returns_fallback(self):
        """No client and no XFF → fallback to 127.0.0.1."""
        req = FakeRequest(client_host="", forwarded_for="")
        assert _get_client_ip(req) == "127.0.0.1"

    def test_null_client_no_xff(self):
        """request.client is None → fallback to 127.0.0.1."""
        req = FakeRequest(client_host="", forwarded_for="")
        req.client = None
        assert _get_client_ip(req) == "127.0.0.1"

    @patch("app.rate_limiter.settings")
    def test_xff_whitespace_handling(self, mock_settings):
        """XFF entries with extra whitespace are trimmed."""
        mock_settings.trusted_proxy_count = 1
        req = FakeRequest(
            client_host="10.0.0.1",
            forwarded_for="  203.0.113.50  ",
        )
        assert _get_client_ip(req) == "203.0.113.50"
