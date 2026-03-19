"""Auth endpoint integration tests.

All tests mock the Supabase client to avoid live connections.
Tests verify HTTP request/response behavior of auth endpoints.
"""

from unittest.mock import AsyncMock, patch

from app.services.auth import AuthenticationError


class TestSignupEndpoint:
    async def test_signup_valid(self, client):
        """Valid signup returns 201 with success message."""
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            return_value="Account created. Please check your email to verify your account.",
        ):
            response = await client.post(
                "/api/auth/signup",
                json={"email": "new@example.com", "password": "securepass123"},
            )
        assert response.status_code == 201
        assert "check your email" in response.json()["message"].lower()

    async def test_signup_short_password(self, client):
        """Password under 8 chars returns 422."""
        response = await client.post(
            "/api/auth/signup",
            json={"email": "new@example.com", "password": "short"},
        )
        assert response.status_code == 422

    async def test_signup_long_password(self, client):
        """Password over 128 chars returns 422."""
        response = await client.post(
            "/api/auth/signup",
            json={"email": "new@example.com", "password": "a" * 129},
        )
        assert response.status_code == 422

    async def test_signup_invalid_email(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/auth/signup",
            json={"email": "not-an-email", "password": "securepass123"},
        )
        assert response.status_code == 422

    async def test_signup_breached_password(self, client):
        """Breached password returns 400."""
        from app.services.auth import BreachedPasswordError

        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            side_effect=BreachedPasswordError(
                "This password has been found in a data breach. "
                "Please choose a different password."
            ),
        ):
            response = await client.post(
                "/api/auth/signup",
                json={"email": "new@example.com", "password": "breachedpass"},
            )
        assert response.status_code == 400
        assert "data breach" in response.json()["detail"].lower()

    async def test_signup_missing_email(self, client):
        """Missing email field returns 422."""
        response = await client.post(
            "/api/auth/signup",
            json={"password": "securepass123"},
        )
        assert response.status_code == 422

    async def test_signup_missing_password(self, client):
        """Missing password field returns 422."""
        response = await client.post(
            "/api/auth/signup",
            json={"email": "new@example.com"},
        )
        assert response.status_code == 422

    async def test_signup_server_error(self, client):
        """Unexpected error during signup returns 500."""
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Unexpected"),
        ):
            response = await client.post(
                "/api/auth/signup",
                json={"email": "new@example.com", "password": "securepass123"},
            )
        assert response.status_code == 500


class TestLoginEndpoint:
    async def test_login_returns_401_on_failure(self, client):
        """Failed login returns 401 with generic message."""
        from app.services.auth import AuthenticationError

        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            side_effect=AuthenticationError("Invalid email or password"),
        ):
            response = await client.post(
                "/api/auth/login",
                json={"email": "wrong@example.com", "password": "wrongpass"},
            )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    async def test_login_success(self, client):
        """Valid login returns 200 with tokens and user."""
        login_result = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
            "user": {
                "id": "user-123",
                "email": "test@example.com",
                "email_verified": True,
                "created_at": "2026-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            return_value=login_result,
        ):
            response = await client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "validpass123"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test-access-token"
        assert data["refresh_token"] == "test-refresh-token"
        assert data["expires_in"] == 900
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["email_verified"] is True

    async def test_login_invalid_email_format(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/auth/login",
            json={"email": "not-an-email", "password": "somepassword"},
        )
        assert response.status_code == 422

    async def test_login_unexpected_error_returns_500(self, client):
        """Unexpected error during login returns 500 (not masked as 401)."""
        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Something broke"),
        ):
            response = await client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "validpass123"},
            )
        assert response.status_code == 500
        assert response.json()["detail"] == "Login failed"


class TestProtectedEndpoints:
    async def test_me_with_auth(self, auth_client):
        """GET /api/auth/me returns user profile when authenticated."""
        response = await auth_client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["id"] == "test-user-id-123"
        assert data["email_verified"] is True

    async def test_me_without_auth(self, client):
        """GET /api/auth/me without auth returns 401."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_me_with_invalid_bearer(self, client):
        """GET /api/auth/me with invalid token returns 401."""
        from app.services.auth import InvalidTokenError

        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            side_effect=InvalidTokenError("Invalid or expired token"),
        ):
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer bad-token"},
            )
        assert response.status_code == 401

    async def test_me_without_bearer_prefix(self, client):
        """GET /api/auth/me with malformed auth header returns 401."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Token some-token"},
        )
        assert response.status_code == 401

    async def test_logout_with_auth(self, auth_client):
        """POST /api/auth/logout with auth returns 200."""
        with patch("app.services.auth.auth_service.logout", new_callable=AsyncMock):
            response = await auth_client.post("/api/auth/logout")
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    async def test_logout_without_auth(self, client):
        """POST /api/auth/logout without auth returns 401."""
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401

    async def test_delete_account_with_auth(self, auth_client):
        """DELETE /api/auth/account with auth returns 200."""
        with patch("app.services.auth.auth_service.delete_user", new_callable=AsyncMock):
            response = await auth_client.delete("/api/auth/account")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    async def test_delete_account_without_auth(self, client):
        """DELETE /api/auth/account without auth returns 401."""
        response = await client.delete("/api/auth/account")
        assert response.status_code == 401

    async def test_delete_account_server_error(self, auth_client):
        """DELETE /api/auth/account server error returns 500."""
        with patch(
            "app.services.auth.auth_service.delete_user",
            new_callable=AsyncMock,
            side_effect=RuntimeError("DB error"),
        ):
            response = await auth_client.delete("/api/auth/account")
        assert response.status_code == 500
        assert "deletion failed" in response.json()["detail"].lower()


class TestRefreshEndpoint:
    async def test_refresh_invalid_token(self, client):
        """Invalid refresh token returns 401."""
        from app.services.auth import InvalidTokenError

        with patch(
            "app.services.auth.auth_service.refresh",
            new_callable=AsyncMock,
            side_effect=InvalidTokenError("Invalid or expired refresh token"),
        ):
            response = await client.post(
                "/api/auth/refresh",
                json={"refresh_token": "invalid-token"},
            )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_refresh_success(self, client):
        """Valid refresh returns new tokens."""
        refresh_result = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
        }

        with patch(
            "app.services.auth.auth_service.refresh",
            new_callable=AsyncMock,
            return_value=refresh_result,
        ):
            response = await client.post(
                "/api/auth/refresh",
                json={"refresh_token": "valid-refresh-token"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new-access-token"
        assert data["refresh_token"] == "new-refresh-token"
        assert data["expires_in"] == 900
        assert data["token_type"] == "bearer"

    async def test_refresh_missing_token(self, client):
        """Missing refresh_token field returns 422."""
        response = await client.post(
            "/api/auth/refresh",
            json={},
        )
        assert response.status_code == 422


class TestResendVerification:
    async def test_resend_returns_200(self, client):
        """Resend verification always returns 200 (anti-enumeration)."""
        with patch(
            "app.services.auth.auth_service.resend_verification",
            new_callable=AsyncMock,
            return_value="If an account exists with this email, a verification link has been sent.",  # noqa: E501
        ):
            response = await client.post(
                "/api/auth/resend-verification",
                json={"email": "anyone@example.com"},
            )
        assert response.status_code == 200
        assert "verification link" in response.json()["message"].lower()

    async def test_resend_invalid_email_format(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/auth/resend-verification",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    async def test_resend_nonexistent_email_still_200(self, client):
        """Nonexistent email still returns 200 (anti-enumeration)."""
        with patch(
            "app.services.auth.auth_service.resend_verification",
            new_callable=AsyncMock,
            return_value="If an account exists with this email, a verification link has been sent.",  # noqa: E501
        ):
            response = await client.post(
                "/api/auth/resend-verification",
                json={"email": "nonexistent@example.com"},
            )
        assert response.status_code == 200


class TestForgotPasswordEndpoint:
    async def test_forgot_password_returns_200(self, client):
        """Forgot password always returns 200 (anti-enumeration)."""
        with patch(
            "app.services.auth.auth_service.forgot_password",
            new_callable=AsyncMock,
            return_value="If an account exists with this email, a password reset link has been sent.",  # noqa: E501
        ):
            response = await client.post(
                "/api/auth/forgot-password",
                json={"email": "anyone@example.com"},
            )
        assert response.status_code == 200
        assert "reset" in response.json()["message"].lower()

    async def test_forgot_password_nonexistent_email_still_200(self, client):
        """Nonexistent email still returns 200 (anti-enumeration)."""
        with patch(
            "app.services.auth.auth_service.forgot_password",
            new_callable=AsyncMock,
            return_value="If an account exists with this email, a password reset link has been sent.",  # noqa: E501
        ):
            response = await client.post(
                "/api/auth/forgot-password",
                json={"email": "nonexistent@example.com"},
            )
        assert response.status_code == 200

    async def test_forgot_password_invalid_email_format(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    async def test_forgot_password_missing_email(self, client):
        """Missing email field returns 422."""
        response = await client.post(
            "/api/auth/forgot-password",
            json={},
        )
        assert response.status_code == 422


class TestResetPasswordEndpoint:
    async def test_reset_password_success(self, client):
        """Valid reset code + new password returns 200 with tokens."""
        reset_result = {
            "access_token": "reset-access-token",
            "refresh_token": "reset-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
            "user": {
                "id": "user-123",
                "email": "user@example.com",
                "email_verified": True,
                "created_at": "2026-01-01T00:00:00Z",
            },
        }
        with patch(
            "app.services.auth.auth_service.reset_password",
            new_callable=AsyncMock,
            return_value=reset_result,
        ):
            response = await client.post(
                "/api/auth/reset-password",
                json={
                    "email": "user@example.com",
                    "token": "123456",
                    "new_password": "newsecurepass123",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "reset-access-token"
        assert data["refresh_token"] == "reset-refresh-token"
        assert data["user"]["email"] == "user@example.com"
        assert data["user"]["email_verified"] is True

    async def test_reset_password_invalid_code(self, client):
        """Invalid reset code returns 400."""
        with patch(
            "app.services.auth.auth_service.reset_password",
            new_callable=AsyncMock,
            side_effect=AuthenticationError("Invalid or expired reset code"),
        ):
            response = await client.post(
                "/api/auth/reset-password",
                json={
                    "email": "user@example.com",
                    "token": "000000",
                    "new_password": "newsecurepass123",
                },
            )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    async def test_reset_password_breached_password(self, client):
        """Breached new password returns 400."""
        from app.services.auth import BreachedPasswordError

        with patch(
            "app.services.auth.auth_service.reset_password",
            new_callable=AsyncMock,
            side_effect=BreachedPasswordError(
                "This password has been found in a data breach. "
                "Please choose a different password."
            ),
        ):
            response = await client.post(
                "/api/auth/reset-password",
                json={
                    "email": "user@example.com",
                    "token": "123456",
                    "new_password": "breachedpass",
                },
            )
        assert response.status_code == 400
        assert "data breach" in response.json()["detail"].lower()

    async def test_reset_password_short_password(self, client):
        """Password under 8 chars returns 422."""
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "email": "user@example.com",
                "token": "123456",
                "new_password": "short",
            },
        )
        assert response.status_code == 422

    async def test_reset_password_long_password(self, client):
        """Password over 128 chars returns 422."""
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "email": "user@example.com",
                "token": "123456",
                "new_password": "a" * 129,
            },
        )
        assert response.status_code == 422

    async def test_reset_password_short_token(self, client):
        """Token shorter than 6 chars returns 422."""
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "email": "user@example.com",
                "token": "123",
                "new_password": "newsecurepass123",
            },
        )
        assert response.status_code == 422

    async def test_reset_password_invalid_email(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "email": "not-an-email",
                "token": "123456",
                "new_password": "newsecurepass123",
            },
        )
        assert response.status_code == 422

    async def test_reset_password_missing_fields(self, client):
        """Missing required fields returns 422."""
        response = await client.post(
            "/api/auth/reset-password",
            json={"email": "user@example.com"},
        )
        assert response.status_code == 422


class TestVerifyEmailEndpoint:
    async def test_verify_email_success(self, client):
        """Valid OTP code returns 200 with tokens."""
        verify_result = {
            "access_token": "verified-access-token",
            "refresh_token": "verified-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
            "user": {
                "id": "verified-user-id",
                "email": "verified@example.com",
                "email_verified": True,
                "created_at": "2026-01-01T00:00:00Z",
            },
        }
        with patch(
            "app.services.auth.auth_service.verify_email",
            new_callable=AsyncMock,
            return_value=verify_result,
        ):
            response = await client.post(
                "/api/auth/verify-email",
                json={"email": "verified@example.com", "token": "123456"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "verified@example.com"
        assert data["user"]["email_verified"] is True

    async def test_verify_email_invalid_code(self, client):
        """Invalid OTP code returns 400."""
        with patch(
            "app.services.auth.auth_service.verify_email",
            new_callable=AsyncMock,
            side_effect=AuthenticationError("Invalid or expired verification code"),
        ):
            response = await client.post(
                "/api/auth/verify-email",
                json={"email": "user@example.com", "token": "000000"},
            )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    async def test_verify_email_short_token(self, client):
        """Token shorter than 6 chars returns 422."""
        response = await client.post(
            "/api/auth/verify-email",
            json={"email": "user@example.com", "token": "123"},
        )
        assert response.status_code == 422

    async def test_verify_email_invalid_email(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/auth/verify-email",
            json={"email": "not-an-email", "token": "123456"},
        )
        assert response.status_code == 422
