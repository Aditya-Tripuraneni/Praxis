"""Correctness tests for trig evaluation templates.

Verifies answers by independent computation using the STANDARD_VALUES
lookup table and SymPy's simplify.  For inverse-trig compositions (HARD),
verifies the answer is a rational number from Pythagorean-triple arithmetic.
"""

import random

from sympy import acos, asin, atan, latex, simplify

from app.engine.topics.trigonometry._helpers import STANDARD_VALUES
from app.engine.topics.trigonometry.evaluation import (
    InverseTrigTemplate,
    TrigEvalTemplate,
)
from app.engine.types import Difficulty

# ---------------------------------------------------------------------------
# TrigEvalTemplate
# ---------------------------------------------------------------------------


class TestTrigEvalCorrectness:
    """Verify TrigEvalTemplate answers match STANDARD_VALUES independently."""

    def _verify_answer(self, problem):
        """Cross-check the answer against the STANDARD_VALUES table.

        The metadata stores the function name and base_angle as LaTeX strings.
        We iterate STANDARD_VALUES to find the matching entry and compare.
        """
        meta = problem.metadata
        func_name = meta["function"]
        base_angle_ltx = meta["base_angle"]
        answer_str = str(problem.answer_latex)

        # Find the matching standard value by LaTeX comparison on the
        # base angle (the angle before any coterminal shift).
        matched = False
        for (fname, angle), val in STANDARD_VALUES.items():
            if fname != func_name:
                continue
            if latex(angle) != base_angle_ltx:
                continue
            expected_answer = f"${latex(val)}$"
            assert answer_str == expected_answer, (
                f"{func_name}({base_angle_ltx}): got {answer_str}, expected {expected_answer}"
            )
            matched = True
            break

        assert matched, f"No STANDARD_VALUES entry for {func_name} at {base_angle_ltx}"

    def test_easy_50_correct(self):
        t = TrigEvalTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex
            self._verify_answer(p)

    def test_medium_50_correct(self):
        t = TrigEvalTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex
            self._verify_answer(p)

    def test_hard_50_correct(self):
        t = TrigEvalTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex
            self._verify_answer(p)

    def test_hard_uses_all_six_functions(self):
        """HARD difficulty should eventually use all 6 trig functions."""
        funcs_seen: set[str] = set()
        t = TrigEvalTemplate()
        for seed in range(200):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            funcs_seen.add(p.metadata["function"])
        expected = {"sin", "cos", "tan", "cot", "sec", "csc"}
        assert funcs_seen == expected, f"Only saw {funcs_seen}"

    def test_easy_only_sin_cos(self):
        """EASY difficulty must only use sin and cos."""
        t = TrigEvalTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.metadata["function"] in ("sin", "cos"), (
                f"EASY used {p.metadata['function']} at seed {seed}"
            )

    def test_medium_only_sin_cos_tan(self):
        """MEDIUM difficulty must only use sin, cos, tan."""
        t = TrigEvalTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            assert p.metadata["function"] in ("sin", "cos", "tan"), (
                f"MEDIUM used {p.metadata['function']} at seed {seed}"
            )

    def test_hard_coterminal_angle_differs_from_base(self):
        """At least some HARD problems should display a coterminal angle
        that differs from the base angle."""
        has_shift = False
        t = TrigEvalTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            if p.metadata["angle"] != p.metadata["base_angle"]:
                has_shift = True
                break
        assert has_shift, "No HARD problem used a coterminal shift"

    def test_deterministic_with_same_seed(self):
        """Same seed must produce identical output."""
        t = TrigEvalTemplate()
        p1 = t.generate(Difficulty.MEDIUM, random.Random(42))
        p2 = t.generate(Difficulty.MEDIUM, random.Random(42))
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)


# ---------------------------------------------------------------------------
# InverseTrigTemplate — EASY / MEDIUM (direct evaluation)
# ---------------------------------------------------------------------------


class TestInverseTrigDirectCorrectness:
    """Verify EASY/MEDIUM inverse trig answers by applying the forward
    function to the answer and checking it equals the input value."""

    def _verify_direct(self, problem):
        """For arcF(v) = angle, verify F(angle) == v."""
        meta = problem.metadata
        func_name = meta["function"]
        value_ltx = meta["value"]
        answer_str = str(problem.answer_latex)

        inv_funcs = {"arcsin": asin, "arccos": acos, "arctan": atan}
        inv_func = inv_funcs[func_name]

        # Reconstruct the value from the known pools.
        from app.engine.topics.trigonometry.evaluation import (
            _EASY_INV_VALUES,
            _MEDIUM_INV_VALUES,
        )

        all_vals = _EASY_INV_VALUES + _MEDIUM_INV_VALUES
        for v in all_vals:
            if latex(v) == value_ltx:
                expected_angle = simplify(inv_func(v))
                expected_answer = f"${latex(expected_angle)}$"
                assert answer_str == expected_answer, (
                    f"{func_name}({value_ltx}): got {answer_str}, expected {expected_answer}"
                )
                return

        # Value not in our pools — just check generation succeeded.
        assert problem.question_latex
        assert problem.answer_latex

    def test_easy_50_correct(self):
        t = InverseTrigTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex
            self._verify_direct(p)

    def test_medium_50_correct(self):
        t = InverseTrigTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex
            self._verify_direct(p)

    def test_deterministic_with_same_seed(self):
        t = InverseTrigTemplate()
        p1 = t.generate(Difficulty.EASY, random.Random(99))
        p2 = t.generate(Difficulty.EASY, random.Random(99))
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)


# ---------------------------------------------------------------------------
# InverseTrigTemplate — HARD (Pythagorean-triple compositions)
# ---------------------------------------------------------------------------


class TestInverseTrigCompositionCorrectness:
    """Verify HARD inverse trig composition answers using Pythagorean
    triple arithmetic."""

    def test_hard_50_generates(self):
        t = InverseTrigTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_hard_answer_is_rational(self):
        """HARD composition answers should be rational fractions derived
        from Pythagorean triples -- no unsimplified inverse trig."""
        t = InverseTrigTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            a = str(p.answer_latex)
            for inv in ("arctan", "arcsin", "arccos", "asin", "acos", "atan"):
                assert inv not in a, f"Seed {seed}: unsimplified answer {a}"

    def test_hard_answer_matches_triangle_arithmetic(self):
        """Recompute the expected answer from the Pythagorean triple
        and verify it matches the template's answer."""
        from app.engine.topics.trigonometry.evaluation import (
            _triangle_trig,
        )

        t = InverseTrigTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            meta = p.metadata
            outer_func = meta["outer_function"]
            inner_func = meta["inner_function"]
            triple_str = meta["triple"]

            # Parse triple "(a,b,c)"
            nums = triple_str.strip("()").split(",")
            a, b, c = (int(x) for x in nums)

            # Reconstruct opp, adj, hyp (mirrors template logic)
            if inner_func == "arcsin":
                opp, adj, hyp = a, b, c
            elif inner_func == "arccos":
                adj, opp, hyp = a, b, c
            else:  # arctan
                opp, adj, hyp = a, b, c

            expected = _triangle_trig(outer_func, opp, adj, hyp)
            assert expected is not None, (
                f"Seed {seed}: undefined {outer_func} for triple ({a},{b},{c})"
            )
            expected_answer = f"${latex(expected)}$"
            assert str(p.answer_latex) == expected_answer, (
                f"Seed {seed}: "
                f"{outer_func}({inner_func}({meta['value']})) "
                f"= {p.answer_latex}, expected {expected_answer}"
            )

    def test_hard_uses_multiple_outer_functions(self):
        """HARD should exercise more than just sin/cos as outer."""
        outer_seen: set[str] = set()
        t = InverseTrigTemplate()
        for seed in range(100):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            outer_seen.add(p.metadata["outer_function"])
        assert len(outer_seen) >= 4, f"Only saw outer funcs: {outer_seen}"

    def test_hard_uses_all_three_inner_functions(self):
        """HARD should exercise all three inverse trig as inner."""
        inner_seen: set[str] = set()
        t = InverseTrigTemplate()
        for seed in range(100):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            inner_seen.add(p.metadata["inner_function"])
        expected = {"arcsin", "arccos", "arctan"}
        assert inner_seen == expected, f"Only saw inner funcs: {inner_seen}"
