import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.rate_limiter import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset rate limiter state between tests to prevent 429s in test suite."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
async def client():
    """Unauthenticated test client."""
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """A mock user profile for testing protected endpoints."""
    return {
        "id": "test-user-id-123",
        "email": "test@example.com",
        "email_verified": True,
        "created_at": "2026-03-12T00:00:00Z",
    }


@pytest.fixture
async def auth_client(mock_user):
    """Test client with mocked authentication and subscription.

    Bypasses both get_current_user and require_active_subscription
    so tests don't need a live Supabase connection.
    """
    from app.api.dependencies import (
        AuthenticatedUser,
        get_current_user,
        require_active_subscription,
    )
    from app.models.auth import UserProfile

    authenticated_user = AuthenticatedUser(
        profile=UserProfile(**mock_user),
        access_token="mock-access-token",
    )

    async def mock_get_current_user():
        return authenticated_user

    async def mock_require_active_subscription():
        return authenticated_user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_active_subscription] = mock_require_active_subscription

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_no_sub_client(mock_user):
    """Test client with auth but NO active subscription (for testing 403).

    Only overrides get_current_user — require_active_subscription runs
    normally, allowing tests to verify the subscription gate.
    """
    from app.api.dependencies import AuthenticatedUser, get_current_user
    from app.models.auth import UserProfile

    async def mock_get_current_user():
        return AuthenticatedUser(
            profile=UserProfile(**mock_user),
            access_token="mock-access-token",
        )

    app.dependency_overrides[get_current_user] = mock_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
