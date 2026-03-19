"""Correctness tests for trig identity/simplification templates.

The template's _build method already runs trigsimp(expr - answer) == 0
at generation time.  If the check fails, GenerationError is raised.
Therefore, any successful generation IS a mathematical correctness proof.

These tests stress-test across many seeds and verify variety.
"""

import random

from app.engine.topics.trigonometry.identities import TrigSimplifyTemplate
from app.engine.types import Difficulty

# ---------------------------------------------------------------------------
# Correctness via stress-test (crash-free = mathematically verified)
# ---------------------------------------------------------------------------


class TestIdentityCorrectness:
    """Generate many problems per difficulty; each success is a SymPy-verified
    identity proof (trigsimp(expr - answer) == 0 is checked inside _build)."""

    def test_100_easy_no_error(self):
        t = TrigSimplifyTemplate()
        for seed in range(100):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_100_medium_no_error(self):
        t = TrigSimplifyTemplate()
        for seed in range(100):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_200_hard_no_error(self):
        t = TrigSimplifyTemplate()
        for seed in range(200):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_metadata_contains_variant(self):
        """Every generated problem should include the variant name in
        its metadata."""
        t = TrigSimplifyTemplate()
        for d in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            for seed in range(10):
                p = t.generate(d, random.Random(seed))
                assert "variant" in p.metadata, (
                    f"Missing 'variant' in metadata at {d}, seed {seed}"
                )
                assert p.metadata["variant"], f"Empty variant at {d}, seed {seed}"

    def test_metadata_contains_expression(self):
        """Every problem should store the raw expression LaTeX in metadata."""
        t = TrigSimplifyTemplate()
        for d in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            for seed in range(10):
                p = t.generate(d, random.Random(seed))
                assert "expression" in p.metadata
                assert p.metadata["expression"]

    def test_deterministic_with_same_seed(self):
        t = TrigSimplifyTemplate()
        p1 = t.generate(Difficulty.HARD, random.Random(42))
        p2 = t.generate(Difficulty.HARD, random.Random(42))
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)


# ---------------------------------------------------------------------------
# Variety
# ---------------------------------------------------------------------------


class TestIdentityVariety:
    """Verify adequate problem diversity across seeds."""

    def test_easy_variety(self):
        t = TrigSimplifyTemplate()
        questions = set()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 3, f"Only {len(questions)} unique easy questions"

    def test_medium_variety(self):
        t = TrigSimplifyTemplate()
        questions = set()
        for seed in range(30):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 4, f"Only {len(questions)} unique medium questions"

    def test_hard_variety(self):
        t = TrigSimplifyTemplate()
        questions = set()
        for seed in range(200):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 50, f"Only {len(questions)} unique hard questions from 200 seeds"

    def test_easy_covers_all_variants(self):
        """EASY has 4 variants; 50 seeds should hit all of them."""
        expected = {"pyth_basic", "pyth_rearranged", "reciprocal", "quotient"}
        t = TrigSimplifyTemplate()
        seen: set[str] = set()
        for seed in range(50):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            seen.add(p.metadata["variant"])
        assert seen == expected, f"Only saw easy variants: {seen}"

    def test_medium_covers_all_variants(self):
        """MEDIUM has 6 variants; 100 seeds should hit all of them."""
        expected = {
            "frac_simplify",
            "double_angle_frac",
            "half_angle_cos2",
            "trig_product",
            "sec_tan_pyth",
            "csc_cot_pyth",
        }
        t = TrigSimplifyTemplate()
        seen: set[str] = set()
        for seed in range(100):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            seen.add(p.metadata["variant"])
        assert seen == expected, f"Only saw medium variants: {seen}"

    def test_hard_covers_all_variants(self):
        """HARD has 13 variants; 500 seeds should hit all of them."""
        expected = {
            # Original families
            "sum_diff_expansion",
            "cos_diff_expansion",
            "sec_cos_over_tan",
            "double_angle_tan",
            "sin_sec_product",
            # New families
            "compound_fraction",
            "conjugate_product",
            "multi_step_algebraic",
            "factoring",
            "fraction_sum",
            "cofunction",
            "even_odd_compound",
            "double_angle_extended",
        }
        t = TrigSimplifyTemplate()
        seen: set[str] = set()
        for seed in range(500):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            seen.add(p.metadata["variant"])
        assert seen == expected, f"Only saw hard variants: {seen}"

    def test_hard_no_trivial_zero_or_one_questions(self):
        """HARD questions must never be 'Simplify $0$.',
        'Simplify $1$.' or 'Simplify $-1$.' — those are trivially easy."""
        t = TrigSimplifyTemplate()
        trivial_questions: list[tuple[int, str]] = []
        total = 200
        for seed in range(total):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            q = str(p.question_latex)
            if q.strip() in ("Simplify $0$.", "Simplify $1$.", "Simplify $-1$."):
                trivial_questions.append((seed, q.strip()))
        assert len(trivial_questions) == 0, (
            f"{len(trivial_questions)}/{total} trivial HARD questions: {trivial_questions}"
        )

    def test_hard_sum_diff_uses_angle_metadata(self):
        """sum_diff_expansion and cos_diff_expansion variants should
        include angle_a, angle_b, and operation in metadata."""
        t = TrigSimplifyTemplate()
        found = False
        for seed in range(100):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            variant = p.metadata["variant"]
            if variant in ("sum_diff_expansion", "cos_diff_expansion"):
                assert "angle_a" in p.metadata
                assert "angle_b" in p.metadata
                assert "operation" in p.metadata
                assert p.metadata["operation"] in ("plus", "minus")
                found = True
        assert found, "No sum/diff expansion variant found in 100 seeds"
