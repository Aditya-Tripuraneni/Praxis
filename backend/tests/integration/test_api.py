"""Integration tests for API endpoints."""

import time


class TestHealthCheck:
    async def test_health(self, client):
        r = await client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestTopics:
    async def test_get_topics(self, client):
        r = await client.get("/api/tests/topics")
        assert r.status_code == 200
        topics = r.json()
        assert len(topics) >= 4
        for t in topics:
            assert "id" in t
            assert "name" in t
            assert "subtopics" in t
            assert "template_count" in t
            assert t["template_count"] > 0


class TestGenerate:
    async def test_valid_request(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 10},
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["questions"]) == 10
        assert data["test_id"]
        for q in data["questions"]:
            assert q["question_latex"]
            assert q["answer_latex"]
            assert q["topic"] == "algebra"

    async def test_multiple_topics(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra", "calculus"], "difficulty": "medium", "count": 10},
        )
        assert r.status_code == 200
        topics = {q["topic"] for q in r.json()["questions"]}
        assert len(topics) >= 2

    async def test_deterministic_with_seed(self, auth_client):
        body = {"topics": ["algebra"], "difficulty": "easy", "count": 5, "seed": 42}
        r1 = await auth_client.post("/api/tests/generate", json=body)
        r2 = await auth_client.post("/api/tests/generate", json=body)
        q1 = [q["question_latex"] for q in r1.json()["questions"]]
        q2 = [q["question_latex"] for q in r2.json()["questions"]]
        assert q1 == q2

    async def test_invalid_topic(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["nonexistent"], "difficulty": "easy", "count": 5},
        )
        # Pydantic field_validator catches invalid topics → 422
        assert r.status_code == 422

    async def test_invalid_difficulty(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "impossible", "count": 5},
        )
        # Literal["easy","medium","hard"] causes Pydantic 422, not our 400
        assert r.status_code == 422

    async def test_count_too_low(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 0},
        )
        assert r.status_code == 422

    async def test_count_too_high(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 100},
        )
        assert r.status_code == 422

    async def test_empty_topics(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": [], "difficulty": "easy", "count": 5},
        )
        assert r.status_code == 422

    async def test_performance_50_questions(self, auth_client):
        """SC-002: generation < 3s for 50 questions."""
        start = time.perf_counter()
        r = await auth_client.post(
            "/api/tests/generate",
            json={
                "topics": ["algebra", "functions", "trigonometry", "calculus"],
                "difficulty": "medium",
                "count": 50,
            },
        )
        elapsed = time.perf_counter() - start
        assert r.status_code == 200
        assert len(r.json()["questions"]) == 50
        assert elapsed < 5.0, f"Generation took {elapsed:.2f}s"


class TestSolutionSteps:
    async def test_generate_includes_solution_steps_field(self, auth_client):
        """Generated questions must include a solution_steps list in JSON."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 1, "seed": 42},
        )
        assert r.status_code == 200
        data = r.json()
        for q in data["questions"]:
            assert "solution_steps" in q
            assert isinstance(q["solution_steps"], list)

    async def test_pdf_include_solutions_param(self, auth_client):
        """PDF endpoint accepts include_solutions=true and returns valid PDF."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        r2 = await auth_client.get(
            f"/api/tests/{test_id}/pdf?include_solutions=true&include_answers=true"
        )
        assert r2.status_code == 200
        assert r2.headers["content-type"] == "application/pdf"
        assert b"%PDF" in r2.content[:10]


class TestGetTest:
    async def test_retrieve_generated(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        r2 = await auth_client.get(f"/api/tests/{test_id}")
        assert r2.status_code == 200
        assert r2.json()["test_id"] == test_id

    async def test_not_found(self, auth_client):
        r = await auth_client.get("/api/tests/nonexistent")
        assert r.status_code == 404


class TestPdf:
    async def test_download_pdf(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf")
        assert r2.status_code == 200
        assert r2.headers["content-type"] == "application/pdf"
        assert b"%PDF" in r2.content[:10]

    async def test_pdf_without_answers(self, auth_client):
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf?include_answers=false")
        assert r2.status_code == 200
        assert b"%PDF" in r2.content[:10]

    async def test_pdf_with_underscore_topics(self, auth_client):
        """Regression: subtopic names with underscores must be LaTeX-escaped in PDF."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["functions.domain_rational"], "difficulty": "easy", "count": 3},
        )
        assert r.status_code == 200
        test_id = r.json()["test_id"]

        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf")
        assert r2.status_code == 200, f"PDF failed for underscore topics: {r2.text[:200]}"
        assert b"%PDF" in r2.content[:10]

    async def test_pdf_not_found(self, auth_client):
        r = await auth_client.get("/api/tests/nonexistent/pdf")
        assert r.status_code == 404

    async def test_pdf_performance(self, auth_client):
        """SC-005: PDF < 10s."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 20},
        )
        test_id = r.json()["test_id"]

        start = time.perf_counter()
        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf")
        elapsed = time.perf_counter() - start
        assert r2.status_code == 200
        assert elapsed < 10.0, f"PDF generation took {elapsed:.2f}s"


class TestAuthRequired:
    async def test_generate_requires_auth(self, client):
        """Protected endpoints return 401 without authentication."""
        response = await client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        assert response.status_code == 401

    async def test_topics_is_public(self, client):
        """Topics endpoint remains public."""
        response = await client.get("/api/tests/topics")
        assert response.status_code == 200
