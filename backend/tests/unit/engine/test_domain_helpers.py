"""Tests for domain formatting helpers."""

from sympy import Rational, oo

from app.engine.topics.domain._helpers import (
    fmt_all_reals,
    fmt_interval,
    fmt_periodic_exclusion,
    fmt_set_minus,
    fmt_union,
)


class TestFmtInterval:
    def test_closed_finite(self):
        assert fmt_interval(1, 5) == "[1, 5]"

    def test_open_finite(self):
        assert fmt_interval(1, 5, False, False) == "(1, 5)"

    def test_half_open(self):
        assert fmt_interval(1, 5, True, False) == "[1, 5)"
        assert fmt_interval(1, 5, False, True) == "(1, 5]"

    def test_negative_infinity(self):
        result = fmt_interval(-oo, 3, False, True)
        assert "-\\infty" in result
        assert result.startswith("(")

    def test_positive_infinity(self):
        result = fmt_interval(2, oo, True, False)
        assert "\\infty" in result
        assert result.endswith(")")

    def test_rational_bounds(self):
        result = fmt_interval(Rational(-1, 2), Rational(3, 4))
        assert "\\frac" in result or "-1/2" in result


class TestFmtUnion:
    def test_two_intervals(self):
        result = fmt_union(["(-\\infty, -3)", "(3, \\infty)"])
        assert "\\cup" in result
        assert "(-\\infty, -3)" in result

    def test_single_interval(self):
        result = fmt_union(["[0, \\infty)"])
        assert result == "[0, \\infty)"


class TestFmtSetMinus:
    def test_single_excluded(self):
        result = fmt_set_minus([3])
        assert "\\mathbb{R}" in result
        assert "\\setminus" in result
        assert "3" in result

    def test_multiple_excluded_sorted(self):
        result = fmt_set_minus([5, -2, 3])
        assert "-2" in result
        # Should be sorted: -2, 3, 5
        idx_neg2 = result.index("-2")
        idx_3 = result.index("3")
        assert idx_neg2 < idx_3


class TestFmtAllReals:
    def test_returns_reals(self):
        assert "\\mathbb{R}" in fmt_all_reals()


class TestFmtPeriodicExclusion:
    def test_basic(self):
        result = fmt_periodic_exclusion("\\frac{\\pi}{2}", "\\pi")
        assert "\\mathbb{R}" in result
        assert "\\setminus" in result
        assert "n" in result
        assert "\\mathbb{Z}" in result
