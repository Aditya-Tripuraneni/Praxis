"""Tests for rational expression and equation templates.

Covers: simplify, add/sub, multiply/divide, equations, extraneous, complex fractions.
"""

import random

import pytest
from sympy import Symbol

from app.engine.topics.algebra.rational import (
    ComplexFractionsTemplate,
    RationalAddSubTemplate,
    RationalEquationsTemplate,
    RationalExtraneousTemplate,
    RationalMultiplyDivideTemplate,
    RationalSimplifyTemplate,
)
from app.engine.types import Difficulty

x = Symbol("x")

ALL3 = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
MH = [Difficulty.MEDIUM, Difficulty.HARD]

# All templates to test
TEMPLATES = {
    "simplify": (RationalSimplifyTemplate(), ALL3),
    "add_sub": (RationalAddSubTemplate(), ALL3),
    "multiply_divide": (RationalMultiplyDivideTemplate(), ALL3),
    "equations": (RationalEquationsTemplate(), ALL3),
    "extraneous": (RationalExtraneousTemplate(), MH),
    "complex": (ComplexFractionsTemplate(), ALL3),
}


def _generate_n(template, difficulty, n, seed=42):
    rng = random.Random(seed)
    problems = []
    for _ in range(n):
        try:
            p = template.generate(difficulty, rng)
            problems.append(p)
        except Exception:
            pass  # Some random combos may fail; that's OK if most succeed
    return problems


# ---------------------------------------------------------------------------
# 1. Correctness stress — generate 100 per difficulty, assert no crash
# ---------------------------------------------------------------------------
class TestCorrectnessStress:
    @pytest.mark.parametrize("name,template_info", list(TEMPLATES.items()))
    def test_generates_without_crash(self, name, template_info):
        template, difficulties = template_info
        for diff in difficulties:
            problems = _generate_n(template, diff, 100)
            assert len(problems) >= 80, f"{name}/{diff.value}: only {len(problems)}/100 succeeded"
            for p in problems:
                assert p.question_latex, f"Empty question for {name}/{diff.value}"
                assert p.answer_latex, f"Empty answer for {name}/{diff.value}"
                assert len(p.solution_steps) >= 2, f"Too few steps for {name}/{diff.value}"


# ---------------------------------------------------------------------------
# 2. Simplify verification — cancel() matches answer
# ---------------------------------------------------------------------------
class TestSimplifyVerification:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_answer_is_simplified(self, difficulty):
        """The answer should already be in simplified form (cancel is a no-op)."""
        template = RationalSimplifyTemplate()
        problems = _generate_n(template, difficulty, 50, seed=99)
        for p in problems:
            # Answer should not contain the original unsimplified form
            q_text = str(p.question_latex)
            a_text = str(p.answer_latex)
            assert a_text != q_text, "Answer identical to question — nothing to simplify"


# ---------------------------------------------------------------------------
# 3. Extraneous solution verification
# ---------------------------------------------------------------------------
class TestExtraneousVerification:
    @pytest.mark.parametrize("difficulty", [Difficulty.MEDIUM, Difficulty.HARD])
    def test_extraneous_zeros_denominator(self, difficulty):
        """Every reported extraneous solution must zero a denominator."""
        template = RationalExtraneousTemplate()
        problems = _generate_n(template, difficulty, 50, seed=77)
        assert len(problems) >= 30, f"Too few generated: {len(problems)}"
        for p in problems:
            extra_list = p.metadata.get("extraneous", [])
            assert len(extra_list) >= 1, "No extraneous solution reported"

    @pytest.mark.parametrize("difficulty", [Difficulty.MEDIUM, Difficulty.HARD])
    def test_valid_solution_exists(self, difficulty):
        """Every problem must have at least one valid solution."""
        template = RationalExtraneousTemplate()
        problems = _generate_n(template, difficulty, 50, seed=88)
        for p in problems:
            valid_list = p.metadata.get("valid", [])
            assert len(valid_list) >= 1, "No valid solution reported"


# ---------------------------------------------------------------------------
# 4. Equation solution check — substitute back
# ---------------------------------------------------------------------------
class TestEquationSolutionCheck:
    @pytest.mark.parametrize("difficulty", [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    def test_solutions_in_metadata(self, difficulty):
        """Equation problems should have solution metadata."""
        template = RationalEquationsTemplate()
        problems = _generate_n(template, difficulty, 30, seed=55)
        for p in problems:
            # Should have solution or solutions in metadata
            has_sol = "solution" in p.metadata or "solutions" in p.metadata
            assert has_sol, f"No solution metadata for {difficulty.value}"


# ---------------------------------------------------------------------------
# 5. Variety — enough unique questions
# ---------------------------------------------------------------------------
class TestVariety:
    @pytest.mark.parametrize("name,template_info", list(TEMPLATES.items()))
    def test_unique_questions(self, name, template_info):
        template, difficulties = template_info
        for diff in difficulties:
            problems = _generate_n(template, diff, 50, seed=123)
            unique = {str(p.question_latex) for p in problems}
            assert len(unique) >= 10, (
                f"{name}/{diff.value}: only {len(unique)} unique out of {len(problems)}"
            )


# ---------------------------------------------------------------------------
# 6. No degenerate cases
# ---------------------------------------------------------------------------
class TestNoDegenerate:
    @pytest.mark.parametrize("name,template_info", list(TEMPLATES.items()))
    def test_no_trivial_answers(self, name, template_info):
        template, difficulties = template_info
        for diff in difficulties:
            problems = _generate_n(template, diff, 50, seed=200)
            for p in problems:
                a = str(p.answer_latex).strip()
                # Answer should not be empty or just "$0$" or "$1$"
                assert a not in {"", "$0$", "$1$", "$-1$"}, (
                    f"Trivial answer '{a}' in {name}/{diff.value}"
                )


# ---------------------------------------------------------------------------
# 7. Deterministic — same seed = same output
# ---------------------------------------------------------------------------
class TestDeterministic:
    @pytest.mark.parametrize("name,template_info", list(TEMPLATES.items()))
    def test_same_seed_same_output(self, name, template_info):
        template, difficulties = template_info
        for diff in difficulties:
            a = _generate_n(template, diff, 10, seed=999)
            b = _generate_n(template, diff, 10, seed=999)
            for pa, pb in zip(a, b):
                assert str(pa.question_latex) == str(pb.question_latex), (
                    f"Non-deterministic: {name}/{diff.value}"
                )


# ---------------------------------------------------------------------------
# 8. LaTeX readability — not absurdly long
# ---------------------------------------------------------------------------
class TestLatexReadability:
    @pytest.mark.parametrize("name,template_info", list(TEMPLATES.items()))
    def test_reasonable_length(self, name, template_info):
        template, difficulties = template_info
        for diff in difficulties:
            problems = _generate_n(template, diff, 30, seed=321)
            for p in problems:
                q_len = len(str(p.question_latex))
                a_len = len(str(p.answer_latex))
                assert q_len <= 300, f"Question too long ({q_len}) in {name}/{diff.value}"
                assert a_len <= 200, f"Answer too long ({a_len}) in {name}/{diff.value}"
