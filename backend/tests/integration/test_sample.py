"""Integration tests for the public sample test endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestSampleTestEndpoint:
    async def test_returns_sample_test_no_auth(self, client):
        """GET /api/sample-test works without authentication."""
        resp = await client.get("/api/sample-test")
        assert resp.status_code == 200
        data = resp.json()
        assert "test_id" in data
        assert "questions" in data
        assert len(data["questions"]) <= 5

    async def test_default_params(self, client):
        """Default params: algebra, easy, 5 questions."""
        resp = await client.get("/api/sample-test")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 5
        for q in data["questions"]:
            assert q["topic"] == "algebra"
            assert q["difficulty"] == "easy"

    async def test_custom_topic_and_difficulty(self, client):
        """Supports topic and difficulty query params."""
        resp = await client.get("/api/sample-test?topics=functions&difficulty=medium&count=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 3
        for q in data["questions"]:
            assert q["topic"] == "functions"
            assert q["difficulty"] == "medium"

    async def test_count_capped_at_5(self, client):
        """Requesting more than 5 questions is silently capped to 5."""
        resp = await client.get("/api/sample-test?count=50")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 5

    async def test_multiple_topics(self, client):
        """Comma-separated topics work."""
        resp = await client.get("/api/sample-test?topics=algebra,functions&count=4")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 4

    async def test_invalid_topic_returns_400(self, client):
        """Unknown topic returns 400."""
        resp = await client.get("/api/sample-test?topics=astrology")
        assert resp.status_code == 400

    async def test_invalid_difficulty_returns_422(self, client):
        """Invalid difficulty fails Pydantic validation."""
        resp = await client.get("/api/sample-test?difficulty=impossible")
        assert resp.status_code == 400 or resp.status_code == 422

    async def test_questions_have_latex(self, client):
        """Each question has non-empty LaTeX fields."""
        resp = await client.get("/api/sample-test")
        data = resp.json()
        for q in data["questions"]:
            assert q["question_latex"], "question_latex should not be empty"
            assert q["answer_latex"], "answer_latex should not be empty"

    async def test_response_matches_test_response_schema(self, client):
        """Response has all TestResponse fields."""
        resp = await client.get("/api/sample-test")
        data = resp.json()
        assert "test_id" in data
        assert "questions" in data
        assert "created_at" in data
        assert "config" in data
        assert data["config"]["difficulty"] == "easy"
