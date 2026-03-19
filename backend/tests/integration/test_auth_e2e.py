"""End-to-end auth flow tests with mocked Supabase.

Tests the complete signup -> login -> access -> refresh -> logout -> 401 flow.
"""

from unittest.mock import AsyncMock, patch

from app.services.auth import InvalidTokenError


class TestFullAuthFlow:
    async def test_signup_login_access_logout(self, client):
        """Full flow: signup -> login -> access protected -> logout -> 401."""
        # 1. Signup
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            return_value="Account created. Please check your email to verify your account.",
        ):
            signup_resp = await client.post(
                "/api/auth/signup",
                json={"email": "e2e@example.com", "password": "e2epassword"},
            )
        assert signup_resp.status_code == 201
        assert "check your email" in signup_resp.json()["message"].lower()

        # 2. Login
        login_result = {
            "access_token": "e2e-access-token",
            "refresh_token": "e2e-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
            "user": {
                "id": "e2e-user-id",
                "email": "e2e@example.com",
                "email_verified": True,
                "created_at": "2026-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            return_value=login_result,
        ):
            login_resp = await client.post(
                "/api/auth/login",
                json={"email": "e2e@example.com", "password": "e2epassword"},
            )
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        access_token = tokens["access_token"]
        assert access_token == "e2e-access-token"
        assert tokens["user"]["email"] == "e2e@example.com"

        # 3. Access protected endpoint with token
        user_data = {
            "id": "e2e-user-id",
            "email": "e2e@example.com",
            "email_verified": True,
            "created_at": "2026-01-01T00:00:00Z",
        }

        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            return_value=user_data,
        ):
            me_resp = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "e2e@example.com"
        assert me_resp.json()["id"] == "e2e-user-id"

        # 4. Logout
        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            return_value=user_data,
        ):
            with patch(
                "app.services.auth.auth_service.logout",
                new_callable=AsyncMock,
            ):
                logout_resp = await client.post(
                    "/api/auth/logout",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
        assert logout_resp.status_code == 200
        assert "logged out" in logout_resp.json()["message"].lower()

        # 5. Verify token no longer works (mock returns error)
        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            side_effect=InvalidTokenError("Invalid or expired token"),
        ):
            unauth_resp = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert unauth_resp.status_code == 401

    async def test_signup_login_refresh_flow(self, client):
        """Flow: signup -> login -> refresh -> access with new token."""
        # 1. Signup
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            return_value="Account created. Please check your email to verify your account.",
        ):
            signup_resp = await client.post(
                "/api/auth/signup",
                json={"email": "refresh@example.com", "password": "refreshpass1"},
            )
        assert signup_resp.status_code == 201

        # 2. Login
        login_result = {
            "access_token": "original-access-token",
            "refresh_token": "original-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
            "user": {
                "id": "refresh-user-id",
                "email": "refresh@example.com",
                "email_verified": True,
                "created_at": "2026-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            return_value=login_result,
        ):
            login_resp = await client.post(
                "/api/auth/login",
                json={"email": "refresh@example.com", "password": "refreshpass1"},
            )
        assert login_resp.status_code == 200
        refresh_token = login_resp.json()["refresh_token"]

        # 3. Refresh to get new tokens
        refresh_result = {
            "access_token": "refreshed-access-token",
            "refresh_token": "refreshed-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
        }

        with patch(
            "app.services.auth.auth_service.refresh",
            new_callable=AsyncMock,
            return_value=refresh_result,
        ):
            refresh_resp = await client.post(
                "/api/auth/refresh",
                json={"refresh_token": refresh_token},
            )
        assert refresh_resp.status_code == 200
        new_access_token = refresh_resp.json()["access_token"]
        assert new_access_token == "refreshed-access-token"

        # 4. Access protected endpoint with new token
        user_data = {
            "id": "refresh-user-id",
            "email": "refresh@example.com",
            "email_verified": True,
            "created_at": "2026-01-01T00:00:00Z",
        }

        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            return_value=user_data,
        ):
            me_resp = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {new_access_token}"},
            )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "refresh@example.com"

    async def test_signup_login_delete_account_flow(self, client):
        """Flow: signup -> login -> delete account -> 401."""
        # 1. Signup
        with patch(
            "app.services.auth.auth_service.signup",
            new_callable=AsyncMock,
            return_value="Account created. Please check your email to verify your account.",
        ):
            signup_resp = await client.post(
                "/api/auth/signup",
                json={"email": "delete@example.com", "password": "deletepass1"},
            )
        assert signup_resp.status_code == 201

        # 2. Login
        login_result = {
            "access_token": "delete-access-token",
            "refresh_token": "delete-refresh-token",
            "expires_in": 900,
            "token_type": "bearer",
            "user": {
                "id": "delete-user-id",
                "email": "delete@example.com",
                "email_verified": True,
                "created_at": "2026-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.services.auth.auth_service.login",
            new_callable=AsyncMock,
            return_value=login_result,
        ):
            login_resp = await client.post(
                "/api/auth/login",
                json={"email": "delete@example.com", "password": "deletepass1"},
            )
        assert login_resp.status_code == 200
        access_token = login_resp.json()["access_token"]

        # 3. Delete account
        user_data = {
            "id": "delete-user-id",
            "email": "delete@example.com",
            "email_verified": True,
            "created_at": "2026-01-01T00:00:00Z",
        }

        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            return_value=user_data,
        ):
            with patch(
                "app.services.auth.auth_service.delete_user",
                new_callable=AsyncMock,
            ):
                delete_resp = await client.delete(
                    "/api/auth/account",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
        assert delete_resp.status_code == 200
        assert "deleted" in delete_resp.json()["message"].lower()

        # 4. Verify token no longer works
        with patch(
            "app.services.auth.auth_service.get_user",
            new_callable=AsyncMock,
            side_effect=InvalidTokenError("Invalid or expired token"),
        ):
            unauth_resp = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert unauth_resp.status_code == 401
