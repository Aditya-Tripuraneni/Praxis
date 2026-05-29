"""Tests proving PDF cache correctness — hit/miss, key isolation, no cross-contamination."""

import app.api.pdf as pdf_module


class TestPdfCacheCorrectness:
    async def test_cache_hit_skips_tectonic(self, auth_client, mocker):
        """Second request never calls _generate_pdf_sync — proves cache was read."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        spy = mocker.spy(pdf_module, "_generate_pdf_sync")

        await auth_client.get(f"/api/tests/{test_id}/pdf")  # miss — Tectonic runs
        await auth_client.get(f"/api/tests/{test_id}/pdf")  # hit  — cache returned

        assert spy.call_count == 1

    async def test_cache_hit_returns_identical_bytes(self, auth_client):
        """Same test_id + same params → byte-for-byte identical response."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        r1 = await auth_client.get(f"/api/tests/{test_id}/pdf")
        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.content == r2.content

    async def test_cache_key_differentiates_include_answers(self, auth_client, mocker):
        """include_answers=true vs false → separate cache entries, Tectonic called twice."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        spy = mocker.spy(pdf_module, "_generate_pdf_sync")

        r1 = await auth_client.get(f"/api/tests/{test_id}/pdf?include_answers=true")
        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf?include_answers=false")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert spy.call_count == 2  # different keys — both were cache misses
        assert r1.content != r2.content

    async def test_cache_key_differentiates_include_solutions(self, auth_client, mocker):
        """include_solutions=true vs false → separate cache entries, Tectonic called twice."""
        r = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5},
        )
        test_id = r.json()["test_id"]

        spy = mocker.spy(pdf_module, "_generate_pdf_sync")

        r1 = await auth_client.get(f"/api/tests/{test_id}/pdf?include_solutions=true")
        r2 = await auth_client.get(f"/api/tests/{test_id}/pdf?include_solutions=false")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert spy.call_count == 2
        assert r1.content != r2.content

    async def test_cache_miss_on_different_test_id(self, auth_client, mocker):
        """Two different test_ids generate independently — no cross-contamination."""
        r1 = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5, "seed": 1},
        )
        r2 = await auth_client.post(
            "/api/tests/generate",
            json={"topics": ["algebra"], "difficulty": "easy", "count": 5, "seed": 2},
        )

        spy = mocker.spy(pdf_module, "_generate_pdf_sync")

        pdf1 = await auth_client.get(f"/api/tests/{r1.json()['test_id']}/pdf")
        pdf2 = await auth_client.get(f"/api/tests/{r2.json()['test_id']}/pdf")

        assert pdf1.status_code == 200
        assert pdf2.status_code == 200
        assert spy.call_count == 2  # different test_ids — both were cache misses
        assert pdf1.content != pdf2.content
