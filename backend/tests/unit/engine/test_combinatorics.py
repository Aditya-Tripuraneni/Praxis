"""Tests for the combinatorics & probability templates.

Covers: stress (crash-free), independent verification via metadata,
variety, determinism, anti-degenerate guards, and solution steps.
"""

from __future__ import annotations

import math
import random

import pytest
from sympy import Rational

# Importing topics triggers @register_template decorators
import app.engine.topics  # noqa: F401
from app.engine.topics.combinatorics.templates import (
    BasicProbabilityTemplate,
    CombinationsTemplate,
    CompoundProbabilityTemplate,
    CountingPrincipleTemplate,
    FactorialBasicsTemplate,
    PermutationsTemplate,
)
from app.engine.types import Difficulty, GeneratedProblem, Topic, TrustedLatex

SEEDS = 100
VARIETY_SEEDS = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _gen(template, difficulty: Difficulty, seed: int) -> GeneratedProblem:
    return template.generate(difficulty, random.Random(seed))


# ---------------------------------------------------------------------------
# CountingPrincipleTemplate
# ---------------------------------------------------------------------------


class TestCountingPrinciple:
    @pytest.fixture
    def template(self):
        return CountingPrincipleTemplate()

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_stress_no_crash(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.question_latex
            assert p.answer_latex
            assert p.topic == Topic.COMBINATORICS
            assert p.difficulty == diff
            assert p.subtopic == "counting_principle"

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_metadata_cross_validation(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            choices = p.metadata["choices"]
            expected = math.prod(choices)
            assert p.metadata["answer"] == expected
            assert expected > 1

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_variety(self, template, diff):
        questions = {str(_gen(template, diff, s).question_latex) for s in range(VARIETY_SEEDS)}
        assert len(questions) >= 5

    def test_determinism(self, template):
        p1 = _gen(template, Difficulty.EASY, 42)
        p2 = _gen(template, Difficulty.EASY, 42)
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_solution_steps(self, template, diff):
        for seed in range(10):
            p = _gen(template, diff, seed)
            assert len(p.solution_steps) >= 2
            for step in p.solution_steps:
                assert isinstance(step, TrustedLatex)
                assert step.value


# ---------------------------------------------------------------------------
# FactorialBasicsTemplate
# ---------------------------------------------------------------------------


class TestFactorialBasics:
    @pytest.fixture
    def template(self):
        return FactorialBasicsTemplate()

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_stress_no_crash(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.question_latex
            assert p.answer_latex
            assert p.topic == Topic.COMBINATORICS
            assert p.difficulty == diff

    def test_easy_metadata_verification(self, template):
        for seed in range(SEEDS):
            p = _gen(template, Difficulty.EASY, seed)
            n = p.metadata["n"]
            assert p.metadata["answer"] == math.factorial(n)
            assert p.metadata["type"] == "factorial"
            assert 3 <= n <= 7

    def test_medium_metadata_verification(self, template):
        for seed in range(SEEDS):
            p = _gen(template, Difficulty.MEDIUM, seed)
            n = p.metadata["n"]
            k = p.metadata["k"]
            assert p.metadata["answer"] == math.factorial(n) // math.factorial(k)
            assert p.metadata["type"] == "factorial_ratio"
            assert n > k

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_variety(self, template, diff):
        questions = {str(_gen(template, diff, s).question_latex) for s in range(VARIETY_SEEDS)}
        assert len(questions) >= 5

    def test_determinism(self, template):
        p1 = _gen(template, Difficulty.MEDIUM, 99)
        p2 = _gen(template, Difficulty.MEDIUM, 99)
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_solution_steps(self, template, diff):
        for seed in range(10):
            p = _gen(template, diff, seed)
            assert len(p.solution_steps) >= 2
            for step in p.solution_steps:
                assert isinstance(step, TrustedLatex)


# ---------------------------------------------------------------------------
# PermutationsTemplate
# ---------------------------------------------------------------------------


class TestPermutations:
    @pytest.fixture
    def template(self):
        return PermutationsTemplate()

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_stress_no_crash(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.question_latex
            assert p.answer_latex
            assert p.topic == Topic.COMBINATORICS
            assert p.difficulty == diff
            assert p.subtopic == "permutations"

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_metadata_cross_validation(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            n = p.metadata["n"]
            r = p.metadata["r"]
            assert p.metadata["answer"] == math.perm(n, r)
            assert n > r, f"n={n} must be > r={r}"
            assert r >= 2

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_anti_degenerate(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.metadata["answer"] > 1

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_variety(self, template, diff):
        questions = {str(_gen(template, diff, s).question_latex) for s in range(VARIETY_SEEDS)}
        assert len(questions) >= 5

    def test_determinism(self, template):
        for diff in Difficulty:
            p1 = _gen(template, diff, 77)
            p2 = _gen(template, diff, 77)
            assert str(p1.question_latex) == str(p2.question_latex)
            assert str(p1.answer_latex) == str(p2.answer_latex)

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_solution_steps(self, template, diff):
        for seed in range(10):
            p = _gen(template, diff, seed)
            assert len(p.solution_steps) >= 3
            for step in p.solution_steps:
                assert isinstance(step, TrustedLatex)


# ---------------------------------------------------------------------------
# CombinationsTemplate
# ---------------------------------------------------------------------------


class TestCombinations:
    @pytest.fixture
    def template(self):
        return CombinationsTemplate()

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_stress_no_crash(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.question_latex
            assert p.answer_latex
            assert p.topic == Topic.COMBINATORICS
            assert p.difficulty == diff
            assert p.subtopic == "combinations"

    @pytest.mark.parametrize("diff", [Difficulty.EASY, Difficulty.MEDIUM])
    def test_simple_metadata_cross_validation(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            n = p.metadata["n"]
            r = p.metadata["r"]
            assert p.metadata["answer"] == math.comb(n, r)
            assert n > r
            assert r >= 2

    def test_hard_answer_positive(self, template):
        for seed in range(SEEDS):
            p = _gen(template, Difficulty.HARD, seed)
            assert p.metadata["answer"] > 1

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_variety(self, template, diff):
        questions = {str(_gen(template, diff, s).question_latex) for s in range(VARIETY_SEEDS)}
        assert len(questions) >= 5

    def test_determinism(self, template):
        for diff in Difficulty:
            p1 = _gen(template, diff, 123)
            p2 = _gen(template, diff, 123)
            assert str(p1.question_latex) == str(p2.question_latex)
            assert str(p1.answer_latex) == str(p2.answer_latex)

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_solution_steps(self, template, diff):
        for seed in range(10):
            p = _gen(template, diff, seed)
            assert len(p.solution_steps) >= 2
            for step in p.solution_steps:
                assert isinstance(step, TrustedLatex)

    def test_hard_at_least_variant_exists(self, template):
        """Verify that the 'at_least' variant is produced across seeds."""
        seen_types = set()
        for seed in range(200):
            p = _gen(template, Difficulty.HARD, seed)
            seen_types.add(p.metadata.get("type", "simple"))
        assert "at_least" in seen_types, f"Only saw types: {seen_types}"


# ---------------------------------------------------------------------------
# BasicProbabilityTemplate
# ---------------------------------------------------------------------------


class TestBasicProbability:
    @pytest.fixture
    def template(self):
        return BasicProbabilityTemplate()

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_stress_no_crash(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.question_latex
            assert p.answer_latex
            assert p.topic == Topic.COMBINATORICS
            assert p.difficulty == diff
            assert p.subtopic == "basic_probability"

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_probability_is_valid_fraction(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            num = p.metadata["answer_num"]
            den = p.metadata["answer_den"]
            prob = Rational(num, den)
            assert 0 < prob < 1, f"Probability {prob} is not strictly between 0 and 1"

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_metadata_favorable_total(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            fav = p.metadata["favorable"]
            total = p.metadata["total"]
            assert 0 < fav < total
            # Check simplified fraction matches
            expected = Rational(fav, total)
            assert expected.p == p.metadata["answer_num"]
            assert expected.q == p.metadata["answer_den"]

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_variety(self, template, diff):
        questions = {str(_gen(template, diff, s).question_latex) for s in range(VARIETY_SEEDS)}
        assert len(questions) >= 5

    def test_determinism(self, template):
        for diff in Difficulty:
            p1 = _gen(template, diff, 55)
            p2 = _gen(template, diff, 55)
            assert str(p1.question_latex) == str(p2.question_latex)
            assert str(p1.answer_latex) == str(p2.answer_latex)

    @pytest.mark.parametrize("diff", list(Difficulty))
    def test_solution_steps(self, template, diff):
        for seed in range(10):
            p = _gen(template, diff, seed)
            assert len(p.solution_steps) >= 2
            for step in p.solution_steps:
                assert isinstance(step, TrustedLatex)

    def test_hard_variant_coverage(self, template):
        """Both 'two_dice' and 'number_range' should appear across seeds."""
        variants = set()
        for seed in range(100):
            p = _gen(template, Difficulty.HARD, seed)
            v = p.metadata.get("variant", "")
            if v:
                variants.add(v)
        assert "two_dice" in variants, f"Only saw: {variants}"
        assert "number_range" in variants, f"Only saw: {variants}"


# ---------------------------------------------------------------------------
# CompoundProbabilityTemplate
# ---------------------------------------------------------------------------


class TestCompoundProbability:
    @pytest.fixture
    def template(self):
        return CompoundProbabilityTemplate()

    @pytest.mark.parametrize("diff", [Difficulty.MEDIUM, Difficulty.HARD])
    def test_stress_no_crash(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            assert p.question_latex
            assert p.answer_latex
            assert p.topic == Topic.COMBINATORICS
            assert p.difficulty == diff
            assert p.subtopic == "compound_probability"

    @pytest.mark.parametrize("diff", [Difficulty.MEDIUM, Difficulty.HARD])
    def test_probability_is_valid_fraction(self, template, diff):
        for seed in range(SEEDS):
            p = _gen(template, diff, seed)
            num = p.metadata["answer_num"]
            den = p.metadata["answer_den"]
            prob = Rational(num, den)
            assert 0 < prob < 1, f"Probability {prob} out of range"

    def test_medium_is_independent(self, template):
        for seed in range(SEEDS):
            p = _gen(template, Difficulty.MEDIUM, seed)
            assert p.metadata["type"] == "independent"

    def test_hard_is_dependent(self, template):
        for seed in range(SEEDS):
            p = _gen(template, Difficulty.HARD, seed)
            assert p.metadata["type"] == "dependent"

    def test_medium_variant_coverage(self, template):
        variants = set()
        for seed in range(200):
            p = _gen(template, Difficulty.MEDIUM, seed)
            variants.add(p.metadata["variant"])
        expected = {"coins", "coin_die", "spinner", "repeated"}
        assert variants == expected, f"Only saw: {variants}"

    def test_hard_variant_coverage(self, template):
        variants = set()
        for seed in range(200):
            p = _gen(template, Difficulty.HARD, seed)
            variants.add(p.metadata["variant"])
        expected = {"bag_2color", "bag_3color", "cards_suit", "cards_face"}
        assert variants == expected, f"Only saw: {variants}"

    @pytest.mark.parametrize("diff", [Difficulty.MEDIUM, Difficulty.HARD])
    def test_variety(self, template, diff):
        questions = {str(_gen(template, diff, s).question_latex) for s in range(VARIETY_SEEDS)}
        assert len(questions) >= 5

    def test_determinism(self, template):
        for diff in [Difficulty.MEDIUM, Difficulty.HARD]:
            p1 = _gen(template, diff, 33)
            p2 = _gen(template, diff, 33)
            assert str(p1.question_latex) == str(p2.question_latex)
            assert str(p1.answer_latex) == str(p2.answer_latex)

    @pytest.mark.parametrize("diff", [Difficulty.MEDIUM, Difficulty.HARD])
    def test_solution_steps(self, template, diff):
        for seed in range(10):
            p = _gen(template, diff, seed)
            assert len(p.solution_steps) >= 2
            for step in p.solution_steps:
                assert isinstance(step, TrustedLatex)


# ---------------------------------------------------------------------------
# Cross-cutting: all templates registered correctly
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_combinatorics_templates_in_registry(self):
        from app.engine.registry import registry

        templates = registry.get_templates(Topic.COMBINATORICS, Difficulty.EASY)
        subtopics = {t.subtopic for t in templates}
        assert "counting_principle" in subtopics
        assert "factorial_basics" in subtopics
        assert "permutations" in subtopics
        assert "combinations" in subtopics
        assert "basic_probability" in subtopics

    def test_combinatorics_medium_includes_compound(self):
        from app.engine.registry import registry

        templates = registry.get_templates(Topic.COMBINATORICS, Difficulty.MEDIUM)
        subtopics = {t.subtopic for t in templates}
        assert "compound_probability" in subtopics

    def test_combinatorics_hard_templates(self):
        from app.engine.registry import registry

        templates = registry.get_templates(Topic.COMBINATORICS, Difficulty.HARD)
        subtopics = {t.subtopic for t in templates}
        assert "permutations" in subtopics
        assert "combinations" in subtopics
        assert "basic_probability" in subtopics
        assert "compound_probability" in subtopics
        # factorial_basics and counting_principle are NOT hard
        assert "factorial_basics" not in subtopics
        assert "counting_principle" not in subtopics
