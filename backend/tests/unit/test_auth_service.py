"""Tests for auth service (HIBP check) and auth Pydantic models."""

import hashlib
from unittest.mock import AsyncMock, patch

import pytest

from app.services.auth import AuthService


@pytest.fixture
def auth_service():
    """AuthService with no real Supabase connection (for unit tests)."""
    return AuthService()


class TestCheckPasswordBreached:
    """Tests for HIBP k-anonymity password check."""

    @pytest.mark.asyncio
    async def test_breached_password_detected(self, auth_service):
        password = "password123"
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        _prefix, suffix = sha1[:5], sha1[5:]

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = f"{suffix}:42\r\nABCDE12345:10\r\n"
        mock_response.raise_for_status = lambda: None

        with patch("app.services.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await auth_service.check_password_breached(password)
            assert result is True

    @pytest.mark.asyncio
    async def test_safe_password_not_flagged(self, auth_service):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "AAAAAAA1111:5\r\nBBBBBBB2222:3\r\n"
        mock_response.raise_for_status = lambda: None

        with patch("app.services.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await auth_service.check_password_breached("my-unique-passphrase-2026")
            assert result is False

    @pytest.mark.asyncio
    async def test_api_down_returns_false_lenient(self, auth_service):
        with patch("app.services.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client_cls.return_value = mock_client

            result = await auth_service.check_password_breached("anypassword")
            assert result is False

    @pytest.mark.asyncio
    async def test_hibp_disabled_returns_false(self):
        service = AuthService()
        with patch("app.services.auth.settings") as mock_settings:
            mock_settings.hibp_enabled = False
            result = await service.check_password_breached("password123")
            assert result is False


class TestResetPasswordModels:
    """Tests for ForgotPasswordRequest and ResetPasswordRequest Pydantic models."""

    def test_forgot_password_valid(self):
        from app.models.auth import ForgotPasswordRequest

        req = ForgotPasswordRequest(email="test@example.com")
        assert req.email == "test@example.com"

    def test_forgot_password_invalid_email(self):
        from app.models.auth import ForgotPasswordRequest

        with pytest.raises(Exception):
            ForgotPasswordRequest(email="not-an-email")

    def test_reset_password_valid(self):
        from app.models.auth import ResetPasswordRequest

        req = ResetPasswordRequest(
            email="test@example.com", token="123456", new_password="newsecure123"
        )
        assert req.email == "test@example.com"
        assert req.token == "123456"
        assert req.new_password == "newsecure123"

    def test_reset_password_short_token(self):
        from app.models.auth import ResetPasswordRequest

        with pytest.raises(Exception):
            ResetPasswordRequest(
                email="test@example.com", token="123", new_password="newsecure123"
            )

    def test_reset_password_long_token(self):
        from app.models.auth import ResetPasswordRequest

        with pytest.raises(Exception):
            ResetPasswordRequest(
                email="test@example.com", token="1234567", new_password="newsecure123"
            )

    def test_reset_password_short_password(self):
        from app.models.auth import ResetPasswordRequest

        with pytest.raises(Exception):
            ResetPasswordRequest(email="test@example.com", token="123456", new_password="short")

    def test_reset_password_long_password(self):
        from app.models.auth import ResetPasswordRequest

        with pytest.raises(Exception):
            ResetPasswordRequest(email="test@example.com", token="123456", new_password="a" * 129)


class TestPasswordValidation:
    def test_password_too_short(self):
        from app.models.auth import SignupRequest

        with pytest.raises(Exception):
            SignupRequest(email="test@example.com", password="short")

    def test_password_too_long(self):
        from app.models.auth import SignupRequest

        with pytest.raises(Exception):
            SignupRequest(email="test@example.com", password="a" * 129)

    def test_password_valid_length(self):
        from app.models.auth import SignupRequest

        req = SignupRequest(email="test@example.com", password="validpass")
        assert req.password == "validpass"

    def test_password_max_length(self):
        from app.models.auth import SignupRequest

        req = SignupRequest(email="test@example.com", password="a" * 128)
        assert len(req.password) == 128

    def test_invalid_email_rejected(self):
        from app.models.auth import SignupRequest

        with pytest.raises(Exception):
            SignupRequest(email="not-an-email", password="validpass")
