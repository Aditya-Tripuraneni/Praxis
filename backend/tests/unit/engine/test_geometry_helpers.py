"""Tests for geometry helper functions."""

import random

from sympy import Rational, sqrt

from app.engine.topics.geometry._helpers import (
    distance_between,
    fmt_line_eq,
    fmt_point,
    fmt_slope,
    midpoint_of,
    pythagorean_triple,
    random_nonzero_int,
    shoelace_area,
)


class TestFmtPoint:
    def test_positive_ints(self):
        assert fmt_point(3, 4) == "(3, 4)"

    def test_negative(self):
        result = fmt_point(-2, 5)
        assert "-2" in result and "5" in result

    def test_rational(self):
        result = fmt_point(Rational(1, 2), Rational(-3, 4))
        assert "frac" in result


class TestFmtSlope:
    def test_integer(self):
        assert fmt_slope(3) == "3"

    def test_fraction(self):
        result = fmt_slope(2, 3)
        assert "frac" in result

    def test_negative(self):
        result = fmt_slope(-1, 2)
        assert "-" in result


class TestFmtLineEq:
    def test_standard(self):
        result = fmt_line_eq(2, 3)
        assert "y =" in result
        assert "2" in result
        assert "3" in result

    def test_zero_intercept(self):
        result = fmt_line_eq(3, 0)
        assert "y = 3x" == result or "y = 3 x" in result

    def test_zero_slope(self):
        result = fmt_line_eq(0, 5)
        assert "y = 5" == result

    def test_negative_intercept(self):
        result = fmt_line_eq(2, -3)
        assert "-" in result


class TestPythagoreanTriple:
    def test_is_valid_triple(self):
        rng = random.Random(42)
        for _ in range(10):
            a, b, c = pythagorean_triple(rng)
            assert a**2 + b**2 == c**2, f"{a}² + {b}² ≠ {c}²"


class TestRandomNonzeroInt:
    def test_never_zero(self):
        rng = random.Random(42)
        for _ in range(100):
            val = random_nonzero_int(rng, -5, 5)
            assert val != 0


class TestDistanceBetween:
    def test_pythagorean(self):
        assert distance_between(0, 0, 3, 4) == 5

    def test_horizontal(self):
        assert distance_between(1, 3, 6, 3) == 5

    def test_vertical(self):
        assert distance_between(2, 1, 2, 8) == 7

    def test_irrational(self):
        result = distance_between(0, 0, 1, 1)
        assert result == sqrt(2)


class TestMidpointOf:
    def test_integer_result(self):
        mx, my = midpoint_of(2, 4, 6, 8)
        assert mx == 4
        assert my == 6

    def test_fractional_result(self):
        mx, my = midpoint_of(1, 3, 4, 6)
        assert mx == Rational(5, 2)
        assert my == Rational(9, 2)


class TestShoelaceArea:
    def test_right_triangle_at_origin(self):
        area = shoelace_area(0, 0, 4, 0, 0, 3)
        assert area == 6

    def test_general_triangle(self):
        area = shoelace_area(1, 1, 4, 1, 1, 5)
        assert area == 6

    def test_order_independent(self):
        a1 = shoelace_area(0, 0, 3, 0, 0, 4)
        a2 = shoelace_area(0, 0, 0, 4, 3, 0)
        assert a1 == a2

    def test_collinear_is_zero(self):
        area = shoelace_area(0, 0, 1, 1, 2, 2)
        assert area == 0
