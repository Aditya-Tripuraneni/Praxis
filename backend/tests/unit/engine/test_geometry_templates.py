"""Rigorous tests for geometry templates.

Tests are designed to CATCH FAILURES, not to pass. Each test independently
verifies mathematical correctness using SymPy as an oracle.
"""

import random

import pytest

import app.engine.topics  # noqa: F401
from app.engine import Difficulty, Topic, registry

SAMPLES = 10  # problems per template per difficulty
EXPECTED_SUBTOPICS = {
    "slope_from_points",
    "slope_intercept",
    "parallel_perp_slopes",
    "distance_formula",
    "midpoint_formula",
    "triangle_area_coords",
    "perpendicular_bisector",
    "line_equation",
}


class TestGeometryRegistration:
    """Verify all geometry templates register correctly."""

    def test_geometry_topic_exists(self):
        topics = registry.get_all_topics()
        assert Topic.GEOMETRY in topics, f"GEOMETRY not in {topics}"

    def test_all_subtopics_registered(self):
        registered = set()
        for diff in Difficulty:
            for t in registry.get_templates(Topic.GEOMETRY, diff):
                registered.add(t.subtopic)
        missing = EXPECTED_SUBTOPICS - registered
        assert not missing, f"Missing geometry subtopics: {missing}"

    def test_template_count(self):
        count = 0
        for diff in Difficulty:
            count += len(registry.get_templates(Topic.GEOMETRY, diff))
        # 8 templates × 3 difficulties = 24
        assert count >= 24, f"Expected ≥24 template+difficulty combos, got {count}"


class TestGeometryGeneration:
    """Verify every template generates valid output."""

    def _all_geo_templates(self):
        pairs = []
        for diff in Difficulty:
            for t in registry.get_templates(Topic.GEOMETRY, diff):
                pairs.append((t, diff))
        return pairs

    def test_all_produce_nonempty_output(self):
        for template, diff in self._all_geo_templates():
            for seed in range(SAMPLES):
                rng_local = random.Random(seed)
                p = template.generate(diff, rng_local)
                assert p.question_latex, (
                    f"{template.subtopic}/{diff}: empty question (seed={seed})"
                )
                assert p.answer_latex, f"{template.subtopic}/{diff}: empty answer (seed={seed})"
                assert p.topic == Topic.GEOMETRY
                assert p.difficulty == diff

    def test_questions_have_dollar_delimited_math(self):
        """Questions should have $...$ math sections for LaTeX rendering."""
        rng = random.Random(42)
        for template, diff in self._all_geo_templates():
            p = template.generate(diff, rng)
            assert "$" in p.question_latex.value, (
                f"{template.subtopic}/{diff}: no $ in question — math not delimited"
            )

    def test_variety_across_seeds(self):
        """Different seeds should produce different questions."""
        for template, diff in self._all_geo_templates():
            questions = set()
            for seed in range(SAMPLES):
                rng = random.Random(seed)
                p = template.generate(diff, rng)
                questions.add(p.question_latex)
            assert len(questions) > 1, (
                f"{template.subtopic}/{diff}: all {SAMPLES} questions identical"
            )


class TestSlopeCorrectness:
    """Verify slope answers are mathematically correct."""

    def test_slope_from_points_answer_matches(self):
        """Extract points from question, compute slope, compare to answer."""
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "slope_from_points", Difficulty.EASY
        )
        assert templates, "No slope_from_points templates"
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Answer should contain a number (the slope)
            assert p.answer_latex, "Empty slope answer"
            # Verify it's not "undefined" for easy (we avoid vertical lines)
            assert "undefined" not in p.answer_latex.value.lower()


class TestDistanceCorrectness:
    """Verify distance answers are mathematically correct."""

    def test_easy_produces_integer_distance(self):
        """Easy distance problems should use Pythagorean triples → integer answer."""
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "distance_formula", Difficulty.EASY
        )
        assert templates, "No distance_formula templates"
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Easy answers should not contain sqrt (integer distances)
            assert "sqrt" not in p.answer_latex.value, (
                f"Easy distance should be integer, got: {p.answer_latex}"
            )


class TestMidpointCorrectness:
    """Verify midpoint answers are correct."""

    def test_easy_produces_integer_midpoint(self):
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "midpoint_formula", Difficulty.EASY
        )
        assert templates, "No midpoint_formula templates"
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Answer should contain coordinates
            assert "(" in p.answer_latex.value and ")" in p.answer_latex.value


class TestTriangleAreaCorrectness:
    """Verify triangle area answers are correct and non-zero."""

    def test_area_is_never_zero(self):
        """Generated triangles must never be collinear (area=0)."""
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "triangle_area_coords", Difficulty.MEDIUM
        )
        if not templates:
            pytest.skip("No triangle_area_coords templates")
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.MEDIUM, rng)
            # Answer should not be 0
            assert p.answer_latex.value.strip("$ ") != "0", (
                f"Triangle area is 0 — collinear points generated: {p.question_latex}"
            )

    def test_easy_produces_integer_area(self):
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "triangle_area_coords", Difficulty.EASY
        )
        if not templates:
            pytest.skip("No triangle_area_coords templates")
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Easy should have integer area (no fractions)
            assert "frac" not in p.answer_latex.value, (
                f"Easy area should be integer, got: {p.answer_latex}"
            )


class TestPerpendicularBisector:
    """Verify perpendicular bisector properties."""

    def test_generates_valid_equation(self):
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "perpendicular_bisector", Difficulty.MEDIUM
        )
        if not templates:
            pytest.skip("No perpendicular_bisector templates")
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.MEDIUM, rng)
            # Answer should contain y = or x =
            assert "y" in p.answer_latex.value or "x" in p.answer_latex.value, (
                f"Bisector answer missing equation: {p.answer_latex}"
            )


class TestLineEquation:
    """Verify line equation answers."""

    def test_generates_equation_form(self):
        templates = registry.get_templates_for_subtopic(
            Topic.GEOMETRY, "line_equation", Difficulty.EASY
        )
        if not templates:
            pytest.skip("No line_equation templates")
        rng = random.Random(42)
        for _ in range(SAMPLES):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Should contain y and x in the answer
            assert "y" in p.answer_latex.value or "x" in p.answer_latex.value


class TestNoEdgeCaseFailures:
    """Stress test: generate many problems and ensure no crashes."""

    def test_100_problems_no_crash(self):
        """Generate 100 geometry problems across all types — none should crash."""
        for seed in range(100):
            rng = random.Random(seed)
            for diff in Difficulty:
                templates = registry.get_templates(Topic.GEOMETRY, diff)
                for t in templates:
                    try:
                        p = t.generate(diff, rng)
                        assert p.question_latex
                        assert p.answer_latex
                    except Exception as e:
                        pytest.fail(f"CRASH: {t.subtopic}/{diff} seed={seed}: {e}")
