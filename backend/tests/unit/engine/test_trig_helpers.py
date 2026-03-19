"""Tests for trigonometry helper utilities."""

import random

from sympy import Integer, Rational, pi, sqrt

from app.engine.topics.trigonometry._helpers import (
    STANDARD_VALUES,
    TRIG_FUNCTIONS,
    format_solution_set,
    get_standard_func_values,
    is_defined_at,
    pick_angle,
    pick_trig_func,
    solve_trig_basic,
)
from app.engine.types import Difficulty


class TestStandardValues:
    def test_has_six_functions(self):
        assert len(TRIG_FUNCTIONS) == 6

    def test_values_count_reasonable(self):
        """Should have 70-100 entries (6 funcs x 16 angles minus undefined)."""
        assert 70 <= len(STANDARD_VALUES) <= 100

    def test_sin_pi_over_6(self):
        assert STANDARD_VALUES[("sin", pi / 6)] == Rational(1, 2)

    def test_cos_pi_over_4(self):
        assert STANDARD_VALUES[("cos", pi / 4)] == sqrt(2) / 2

    def test_tan_pi_over_2_not_in_table(self):
        assert ("tan", pi / 2) not in STANDARD_VALUES

    def test_csc_zero_not_in_table(self):
        assert ("csc", Integer(0)) not in STANDARD_VALUES

    def test_sec_pi_over_3(self):
        assert STANDARD_VALUES[("sec", pi / 3)] == 2

    def test_cot_pi_over_4(self):
        assert STANDARD_VALUES[("cot", pi / 4)] == 1


class TestSolveTrigBasic:
    def test_sin_equals_zero(self):
        sols = solve_trig_basic("sin", Integer(0))
        assert len(sols) == 2

    def test_cos_equals_one(self):
        sols = solve_trig_basic("cos", Integer(1))
        assert len(sols) == 1

    def test_sin_equals_half(self):
        sols = solve_trig_basic("sin", Rational(1, 2))
        assert len(sols) == 2

    def test_tan_equals_one(self):
        sols = solve_trig_basic("tan", Integer(1))
        assert len(sols) == 2

    def test_sin_equals_two_no_solutions(self):
        sols = solve_trig_basic("sin", Integer(2))
        assert len(sols) == 0

    def test_with_multiplier_2(self):
        sols = solve_trig_basic("sin", Integer(0), multiplier=2)
        assert len(sols) == 4

    def test_csc_equals_2(self):
        sols = solve_trig_basic("csc", Integer(2))
        assert len(sols) == 2

    def test_cot_equals_zero(self):
        sols = solve_trig_basic("cot", Integer(0))
        assert len(sols) == 2

    def test_with_phase_shift(self):
        sols = solve_trig_basic("sin", Rational(1, 2), phase=pi / 6)
        assert len(sols) >= 1

    def test_all_solutions_in_range(self):
        """Every solution must be in [0, 2pi)."""
        for func_name in ["sin", "cos", "tan"]:
            for (fname, angle), val in STANDARD_VALUES.items():
                if fname != func_name:
                    continue
                sols = solve_trig_basic(func_name, val)
                for s in sols:
                    s_float = float(s.evalf())
                    assert -0.001 <= s_float < 6.284, (
                        f"{func_name}(x)={val}: solution {s}={s_float} out of range"
                    )


class TestFormatSolutionSet:
    def test_empty(self):
        result = format_solution_set([])
        assert "No solution" in result

    def test_single_solution(self):
        result = format_solution_set([pi / 6])
        assert r"\frac{\pi}{6}" in result

    def test_multiple_solutions(self):
        result = format_solution_set([pi / 6, 5 * pi / 6])
        assert r"\left\{" in result


class TestPickAngle:
    def test_easy_returns_axis_angles(self):
        rng = random.Random(42)
        for _ in range(20):
            angle = pick_angle(Difficulty.EASY, rng)
            angle_float = float(angle.evalf())
            assert any(abs(angle_float - t) < 0.01 for t in [0, 1.5708, 3.14159, 4.71239])

    def test_hard_returns_variety(self):
        rng = random.Random(42)
        angles = set()
        for _ in range(50):
            angles.add(float(pick_angle(Difficulty.HARD, rng).evalf()))
        assert len(angles) >= 8


class TestPickTrigFunc:
    def test_easy_only_sin_cos(self):
        rng = random.Random(42)
        funcs = set()
        for _ in range(50):
            name, _, _ = pick_trig_func(Difficulty.EASY, rng)
            funcs.add(name)
        assert funcs <= {"sin", "cos"}

    def test_hard_includes_reciprocal(self):
        rng = random.Random(42)
        funcs = set()
        for _ in range(100):
            name, _, _ = pick_trig_func(Difficulty.HARD, rng)
            funcs.add(name)
        assert len(funcs) >= 4


class TestIsDefined:
    def test_sin_always_defined(self):
        assert is_defined_at("sin", pi / 2) is True
        assert is_defined_at("sin", Integer(0)) is True

    def test_tan_undefined_at_pi_over_2(self):
        assert is_defined_at("tan", pi / 2) is False

    def test_csc_undefined_at_zero(self):
        assert is_defined_at("csc", Integer(0)) is False


class TestGetStandardFuncValues:
    def test_sin_values(self):
        vals = get_standard_func_values("sin")
        assert len(vals) >= 5

    def test_tan_values(self):
        vals = get_standard_func_values("tan")
        assert len(vals) >= 5
