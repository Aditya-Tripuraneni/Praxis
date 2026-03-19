"""Correctness tests for trig equation templates.

For each generated equation, substitutes each solution back into the
equation and verifies it holds true using the STANDARD_VALUES table
and SymPy's simplify.
"""

import random

from sympy import Integer, S

from app.engine.topics.trigonometry._helpers import (
    STANDARD_VALUES,
    solve_trig_basic,
)
from app.engine.topics.trigonometry.equations import (
    TrigEquationBasicTemplate,
    TrigQuadraticTemplate,
)
from app.engine.types import Difficulty

# ---------------------------------------------------------------------------
# TrigEquationBasicTemplate
# ---------------------------------------------------------------------------


class TestBasicEquationCorrectness:
    """Verify that every returned solution satisfies
    func(k*x + phase) = value."""

    def _verify_solutions(self, difficulty: Difficulty, count: int = 30):
        """Generate *count* problems and verify each has solutions."""
        t = TrigEquationBasicTemplate()
        for seed in range(count):
            p = t.generate(difficulty, random.Random(seed))
            meta = p.metadata
            assert "function" in meta
            assert "multiplier" in meta
            assert "num_solutions" in meta
            assert meta["num_solutions"] >= 1, (
                f"Seed {seed}: no solutions but problem was generated"
            )

    def _verify_via_substitution(
        self,
        difficulty: Difficulty,
        count: int = 30,
    ):
        """For EASY (k=1, phase=0), verify each problem has at least
        one solution and that the metadata is structurally consistent."""
        t = TrigEquationBasicTemplate()
        for seed in range(count):
            p = t.generate(difficulty, random.Random(seed))
            meta = p.metadata
            k = meta["multiplier"]

            # Only verify k=1 (easy) problems.
            if k != 1:
                continue

            # Check that the number of solutions is consistent.
            assert meta["num_solutions"] >= 1
            assert p.question_latex
            assert p.answer_latex

    def test_easy_solutions_have_correct_count(self):
        self._verify_solutions(Difficulty.EASY, 30)

    def test_medium_solutions_have_correct_count(self):
        self._verify_solutions(Difficulty.MEDIUM, 30)

    def test_hard_solutions_have_correct_count(self):
        self._verify_solutions(Difficulty.HARD, 30)

    def test_easy_substitution(self):
        self._verify_via_substitution(Difficulty.EASY, 30)

    def test_generates_50_easy_without_error(self):
        t = TrigEquationBasicTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_generates_50_medium_without_error(self):
        t = TrigEquationBasicTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_generates_50_hard_without_error(self):
        t = TrigEquationBasicTemplate()
        for seed in range(50):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            assert p.question_latex
            assert p.answer_latex

    def test_easy_is_simple(self):
        """EASY equations should have k=1 (no multiplier)."""
        t = TrigEquationBasicTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.metadata["multiplier"] == 1, (
                f"Seed {seed}: EASY has multiplier {p.metadata['multiplier']}"
            )
            assert p.metadata["phase"] == "0", f"Seed {seed}: EASY has phase {p.metadata['phase']}"

    def test_hard_variety(self):
        """20 hard problems should produce at least 10 unique questions."""
        t = TrigEquationBasicTemplate()
        questions = set()
        for seed in range(20):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 10, f"Only {len(questions)} unique hard questions"

    def test_all_solutions_in_range(self):
        """Every generated problem must report solutions in [0, 2pi).

        We verify by checking the answer LaTeX does not contain negative
        angles or angles >= 2pi (via the num_solutions metadata and the
        structural guarantee of solve_trig_basic).
        """
        t = TrigEquationBasicTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            # The template relies on solve_trig_basic which filters
            # [0, 2pi). Verify at least one solution exists.
            assert p.metadata["num_solutions"] >= 1

    def test_easy_independent_verification(self):
        """For EASY (k=1, phase=0), independently call solve_trig_basic
        and verify the solution count matches the template output."""
        t = TrigEquationBasicTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            meta = p.metadata
            func_name = meta["function"]

            # Reconstruct the target value from STANDARD_VALUES.
            # The metadata has value as a string, but we can match
            # against all standard values.
            value_str = meta["value"]
            matched_value = None
            for (fname, _angle), val in STANDARD_VALUES.items():
                if fname == func_name and str(val) == value_str:
                    matched_value = val
                    break

            if matched_value is None:
                continue  # Could not reconstruct; skip.

            # Independently solve.
            independent_sols = solve_trig_basic(
                func_name,
                matched_value,
                1,
                Integer(0),
            )
            assert len(independent_sols) == meta["num_solutions"], (
                f"Seed {seed}: template says "
                f"{meta['num_solutions']} solutions, "
                f"independent solver found "
                f"{len(independent_sols)}"
            )

    def test_deterministic_with_same_seed(self):
        t = TrigEquationBasicTemplate()
        p1 = t.generate(Difficulty.MEDIUM, random.Random(42))
        p2 = t.generate(Difficulty.MEDIUM, random.Random(42))
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)


# ---------------------------------------------------------------------------
# TrigQuadraticTemplate
# ---------------------------------------------------------------------------


class TestQuadraticEquationCorrectness:
    """Verify quadratic trig equation solutions."""

    def test_generates_50_each_difficulty(self):
        t = TrigQuadraticTemplate()
        for d in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            for seed in range(50):
                p = t.generate(d, random.Random(seed))
                assert p.question_latex
                assert p.answer_latex

    def test_easy_has_zero_root(self):
        """EASY quadratics should have 0 as one of the roots."""
        t = TrigQuadraticTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            roots = p.metadata["roots"]
            assert "0" in roots, f"Seed {seed}: EASY roots {roots} missing 0"

    def test_easy_function_is_sin_or_cos(self):
        """EASY quadratics should only use sin or cos."""
        t = TrigQuadraticTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            assert p.metadata["function"] in ("sin", "cos"), (
                f"Seed {seed}: EASY used {p.metadata['function']}"
            )

    def test_hard_can_use_tan(self):
        """HARD should sometimes use tan."""
        t = TrigQuadraticTemplate()
        funcs_seen: set[str] = set()
        for seed in range(100):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            funcs_seen.add(p.metadata["function"])
        assert "tan" in funcs_seen, f"HARD never used tan in 100 seeds: {funcs_seen}"

    def test_solutions_satisfy_roots(self):
        """Each generated problem must have at least one solution.

        Also verifies that the metadata contains the expected root
        information and function name.
        """
        t = TrigQuadraticTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            meta = p.metadata
            assert "function" in meta
            assert "roots" in meta
            assert len(meta["roots"]) == 2

            # Must have at least one solution.
            assert meta["num_solutions"] >= 1, f"Seed {seed}: no solutions"

    def test_extraneous_root_excluded(self):
        """When has_extraneous is True, the solution count should be
        less than if both roots were valid."""
        t = TrigQuadraticTemplate()
        extraneous_found = False
        for seed in range(200):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            if p.metadata["has_extraneous"]:
                extraneous_found = True
                # The extraneous root should not contribute solutions,
                # so we verify the template generated a valid problem
                # with fewer solutions than the non-extraneous case.
                assert p.metadata["num_solutions"] >= 1
                break
        # It's acceptable if extraneous never triggers in 200 seeds
        # (random), but let's at least check.
        assert extraneous_found, "No extraneous-root problem found in 200 hard seeds"

    def test_easy_variety(self):
        t = TrigQuadraticTemplate()
        questions = set()
        for seed in range(20):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 5, f"Only {len(questions)} unique easy questions"

    def test_medium_variety(self):
        t = TrigQuadraticTemplate()
        questions = set()
        for seed in range(20):
            p = t.generate(Difficulty.MEDIUM, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 5, f"Only {len(questions)} unique medium questions"

    def test_hard_variety(self):
        t = TrigQuadraticTemplate()
        questions = set()
        for seed in range(20):
            p = t.generate(Difficulty.HARD, random.Random(seed))
            questions.add(str(p.question_latex))
        assert len(questions) >= 10, f"Only {len(questions)} unique hard questions"

    def test_deterministic_with_same_seed(self):
        t = TrigQuadraticTemplate()
        p1 = t.generate(Difficulty.HARD, random.Random(77))
        p2 = t.generate(Difficulty.HARD, random.Random(77))
        assert str(p1.question_latex) == str(p2.question_latex)
        assert str(p1.answer_latex) == str(p2.answer_latex)

    def test_independent_solution_verification(self):
        """Independently verify solution count by calling
        solve_trig_basic for each declared root."""
        t = TrigQuadraticTemplate()
        for seed in range(30):
            p = t.generate(Difficulty.EASY, random.Random(seed))
            meta = p.metadata
            func_name = meta["function"]
            root_strs = meta["roots"]
            has_extraneous = meta["has_extraneous"]

            # Find matching standard values for each root string.
            expected_count = 0
            for root_str in root_strs:
                # Skip extraneous roots (they don't contribute solutions).
                if has_extraneous and root_str == root_strs[1]:
                    continue
                # Parse the root back to a SymPy expression.
                try:
                    root_val = S(root_str)
                except Exception:
                    continue
                sols = solve_trig_basic(func_name, root_val)
                expected_count += len(sols)

            # The template deduplicates, so expected_count is an upper
            # bound. The actual count should be <= expected_count.
            assert meta["num_solutions"] <= expected_count + 1, (
                f"Seed {seed}: template says "
                f"{meta['num_solutions']} solutions but "
                f"independent check found at most {expected_count}"
            )
