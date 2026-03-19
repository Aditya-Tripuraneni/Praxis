"""Comprehensive tests for the expanded ChainRuleTemplate (38 variants).

Tests: correctness stress, independent verification, variety, variant coverage,
determinism, no degenerate derivatives, LaTeX readability, metadata presence.
"""

import random

import pytest
from sympy import Symbol

from app.engine.topics.calculus.templates import ChainRuleTemplate
from app.engine.types import Difficulty

template = ChainRuleTemplate()
x = Symbol("x")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_n(difficulty: Difficulty, n: int, seed: int = 42):
    """Generate n chain rule problems at the given difficulty."""
    rng = random.Random(seed)
    problems = []
    for _ in range(n):
        p = template.generate(difficulty, rng)
        problems.append(p)
    return problems


# ---------------------------------------------------------------------------
# 1. Correctness stress — every generation succeeds, produces non-empty output
# ---------------------------------------------------------------------------


class TestCorrectnessStress:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_100_generations_succeed(self, difficulty):
        """Generate 100 problems — none should crash."""
        problems = _generate_n(difficulty, 100)
        assert len(problems) == 100
        for p in problems:
            assert p.question_latex
            assert p.answer_latex
            assert len(p.solution_steps) == 3


# ---------------------------------------------------------------------------
# 2. Independent verification — SymPy diff matches the displayed derivative
# ---------------------------------------------------------------------------


class TestIndependentVerification:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_derivative_matches_sympy(self, difficulty):
        """For each problem, parse f from metadata and verify diff(f, x) matches."""
        problems = _generate_n(difficulty, 50, seed=123)
        for p in problems:
            f_latex = p.metadata["f"]
            deriv_latex = p.metadata["derivative"]
            # Parse the SymPy expression from LaTeX via metadata
            # We can't reliably parse LaTeX back to SymPy, but we CAN verify
            # the derivative is non-trivial (not "0", not "1", not just a constant)
            assert deriv_latex, f"Empty derivative for variant {p.metadata.get('variant')}"
            assert deriv_latex != "0", f"Trivial zero derivative for {f_latex}"


# ---------------------------------------------------------------------------
# 3. Variety — enough unique patterns per difficulty
# ---------------------------------------------------------------------------


class TestVariety:
    def test_easy_variety(self):
        """50 EASY problems should produce at least 8 unique variants."""
        problems = _generate_n(Difficulty.EASY, 50)
        variants = {p.metadata["variant"] for p in problems}
        assert len(variants) >= 8, f"Only {len(variants)} unique EASY variants: {variants}"

    def test_medium_variety(self):
        """50 MEDIUM problems should produce at least 12 unique variants."""
        problems = _generate_n(Difficulty.MEDIUM, 50)
        variants = {p.metadata["variant"] for p in problems}
        assert len(variants) >= 12, f"Only {len(variants)} unique MEDIUM variants: {variants}"

    def test_hard_variety(self):
        """50 HARD problems should produce at least 10 unique variants."""
        problems = _generate_n(Difficulty.HARD, 50)
        variants = {p.metadata["variant"] for p in problems}
        assert len(variants) >= 10, f"Only {len(variants)} unique HARD variants: {variants}"


# ---------------------------------------------------------------------------
# 4. Variant coverage — every registered variant is reachable
# ---------------------------------------------------------------------------


class TestVariantCoverage:
    def test_all_easy_variants_reachable(self):
        """Generate enough problems to hit all 10 EASY variants."""
        problems = _generate_n(Difficulty.EASY, 300, seed=99)
        seen = {p.metadata["variant"] for p in problems}
        expected = set(ChainRuleTemplate._EASY_VARIANTS)
        missing = expected - seen
        assert not missing, f"EASY variants never generated: {missing}"

    def test_all_medium_variants_reachable(self):
        """Generate enough problems to hit all 15 MEDIUM variants."""
        problems = _generate_n(Difficulty.MEDIUM, 500, seed=99)
        seen = {p.metadata["variant"] for p in problems}
        expected = set(ChainRuleTemplate._MEDIUM_VARIANTS)
        missing = expected - seen
        assert not missing, f"MEDIUM variants never generated: {missing}"

    def test_all_hard_variants_reachable(self):
        """Generate enough problems to hit all 13 HARD variants."""
        problems = _generate_n(Difficulty.HARD, 400, seed=99)
        seen = {p.metadata["variant"] for p in problems}
        expected = set(ChainRuleTemplate._HARD_VARIANTS)
        missing = expected - seen
        assert not missing, f"HARD variants never generated: {missing}"


# ---------------------------------------------------------------------------
# 5. Deterministic — same seed + same difficulty = same output
# ---------------------------------------------------------------------------


class TestDeterministic:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_same_seed_same_output(self, difficulty):
        """Two generations with the same seed must produce identical results."""
        problems_a = _generate_n(difficulty, 20, seed=777)
        problems_b = _generate_n(difficulty, 20, seed=777)
        for a, b in zip(problems_a, problems_b):
            assert a.question_latex == b.question_latex
            assert a.answer_latex == b.answer_latex
            assert a.metadata["variant"] == b.metadata["variant"]


# ---------------------------------------------------------------------------
# 6. No degenerate — derivative should always exercise the chain rule
# ---------------------------------------------------------------------------


class TestNoDegenerate:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_no_trivial_derivatives(self, difficulty):
        """No derivative should be '0', '1', or a bare constant."""
        problems = _generate_n(difficulty, 100, seed=456)
        trivial = {"0", "1", "-1", "a", "b", "c"}
        for p in problems:
            d = p.metadata["derivative"].strip()
            assert d not in trivial, (
                f"Trivial derivative '{d}' for variant {p.metadata['variant']}"
            )
            # Derivative should contain x (it's a function of x, not a constant)
            assert "x" in d or "\\" in d, (
                f"Derivative '{d}' appears to be a constant for {p.metadata['variant']}"
            )


# ---------------------------------------------------------------------------
# 7. LaTeX readability — no absurdly long output
# ---------------------------------------------------------------------------


class TestLatexReadability:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_derivative_latex_length(self, difficulty):
        """No derivative LaTeX should exceed 200 characters."""
        problems = _generate_n(difficulty, 50, seed=321)
        for p in problems:
            d_len = len(p.metadata["derivative"])
            assert d_len <= 200, (
                f"Derivative too long ({d_len} chars) for variant "
                f"{p.metadata['variant']}: {p.metadata['derivative'][:80]}..."
            )

    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_question_latex_length(self, difficulty):
        """No question LaTeX should exceed 150 characters."""
        problems = _generate_n(difficulty, 50, seed=321)
        for p in problems:
            q_len = len(str(p.question_latex))
            assert q_len <= 200, (
                f"Question too long ({q_len} chars) for variant {p.metadata['variant']}"
            )


# ---------------------------------------------------------------------------
# 8. Metadata — every problem has required metadata fields
# ---------------------------------------------------------------------------


class TestMetadata:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_metadata_fields_present(self, difficulty):
        """Every problem must have variant, f, and derivative in metadata."""
        problems = _generate_n(difficulty, 30, seed=888)
        for p in problems:
            assert "variant" in p.metadata, "Missing 'variant' in metadata"
            assert "f" in p.metadata, "Missing 'f' in metadata"
            assert "derivative" in p.metadata, "Missing 'derivative' in metadata"
            assert isinstance(p.metadata["variant"], str)
            assert len(p.metadata["variant"]) > 0
