"""Coordinate geometry templates — line-related problems.

Covers slopes, slope-intercept form, parallel/perpendicular slopes,
and line equations (point-slope, standard form, perpendicular).
"""

from __future__ import annotations

import random

from sympy import Rational, latex, simplify

from app.engine.registry import register_template
from app.engine.topics.geometry._helpers import (
    fmt_line_eq,
    fmt_point,
    fmt_slope,
    random_nonzero_int,
)
from app.engine.types import (
    ALL_DIFFICULTIES,
    Difficulty,
    GeneratedProblem,
    GenerationError,
    Topic,
    TrustedLatex,
)

# ---------------------------------------------------------------------------
# SlopeFromPointsTemplate — subtopic "slope_from_points"
# ---------------------------------------------------------------------------


@register_template
class SlopeFromPointsTemplate:
    topic = Topic.GEOMETRY
    subtopic = "slope_from_points"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Integer slope: pick m in [-3,3] nonzero, P1 coords in [1,5]
        m = random_nonzero_int(rng, -3, 3)
        x1 = rng.randint(1, 5)
        y1 = rng.randint(1, 5)
        x2 = x1 + 1
        y2 = y1 + m

        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)
        slope_latex = fmt_slope(m)

        dy = y2 - y1
        dx = x2 - x1
        steps = [
            TrustedLatex(f"$(x_1, y_1) = {p1}, \\quad (x_2, y_2) = {p2}$"),
            TrustedLatex(f"$m = \\frac{{{latex(dy)}}}{{{latex(dx)}}}$"),
            TrustedLatex(f"$m = {slope_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the slope of the line passing through ${p1} \\text{{ and }} {p2}$"
            ),
            answer_latex=TrustedLatex(f"$m = {slope_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # Fractional slope: m = a/b with a in [-5,5] nonzero, b in [2,4]
        a = random_nonzero_int(rng, -5, 5)
        b = rng.randint(2, 4)
        m = Rational(a, b)

        x1 = rng.randint(-5, 5)
        y1 = rng.randint(-5, 5)
        x2 = x1 + b
        y2 = y1 + a

        # Ensure points are distinct (guaranteed since b >= 2, so x2 != x1)
        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)
        slope_latex = latex(m)

        dy = y2 - y1
        dx = x2 - x1
        steps = [
            TrustedLatex(f"$(x_1, y_1) = {p1}, \\quad (x_2, y_2) = {p2}$"),
            TrustedLatex(f"$m = \\frac{{{latex(dy)}}}{{{latex(dx)}}}$"),
            TrustedLatex(f"$m = {slope_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the slope of the line passing through ${p1} \\text{{ and }} {p2}$"
            ),
            answer_latex=TrustedLatex(f"$m = {slope_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Larger coords [-10,10], slope = a/b with a in [-7,7] nonzero, b in [2,6]
        a = random_nonzero_int(rng, -7, 7)
        b = rng.randint(2, 6)
        m = Rational(a, b)

        x1 = rng.randint(-10, 10)
        y1 = rng.randint(-10, 10)
        x2 = x1 + b
        y2 = y1 + a

        # Points are always distinct since b >= 2
        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)
        slope_latex = latex(m)

        dy = y2 - y1
        dx = x2 - x1
        steps = [
            TrustedLatex(f"$(x_1, y_1) = {p1}, \\quad (x_2, y_2) = {p2}$"),
            TrustedLatex(f"$m = \\frac{{{latex(dy)}}}{{{latex(dx)}}}$"),
            TrustedLatex(f"$m = {slope_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the slope of the line passing through ${p1} \\text{{ and }} {p2}$"
            ),
            answer_latex=TrustedLatex(f"$m = {slope_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# SlopeInterceptTemplate — subtopic "slope_intercept"
# ---------------------------------------------------------------------------


@register_template
class SlopeInterceptTemplate:
    topic = Topic.GEOMETRY
    subtopic = "slope_intercept"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Given m and b directly, write the equation
        m = random_nonzero_int(rng, -5, 5)
        b = rng.randint(-10, 10)

        eq_latex = fmt_line_eq(m, b)

        steps = [
            TrustedLatex(f"$m = {latex(m)}, \\quad b = {latex(b)}$"),
            TrustedLatex(f"${eq_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Write the equation of the line with slope $m = {latex(m)}$"
                f" and $y$-intercept $b = {latex(b)}$."
            ),
            answer_latex=TrustedLatex(f"${eq_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # Given a point and slope, find equation in slope-intercept form
        # Backward: pick m and b, compute a point on the line
        m = random_nonzero_int(rng, -5, 5)
        b = rng.randint(-8, 8)

        # Pick an x-coordinate for the given point
        x1 = random_nonzero_int(rng, -5, 5)
        y1 = m * x1 + b

        p1 = fmt_point(x1, y1)
        eq_latex = fmt_line_eq(m, b)

        steps = [
            TrustedLatex(f"${p1}, \\quad m = {latex(m)}$"),
            TrustedLatex(f"$b = {latex(b)}$"),
            TrustedLatex(f"${eq_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the line in slope-intercept form"
                f" that passes through ${p1}$ with slope $m = {latex(m)}$."
            ),
            answer_latex=TrustedLatex(f"${eq_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Given two points, find equation in slope-intercept form
        # Backward: pick fractional m and integer b, compute two points
        a = random_nonzero_int(rng, -5, 5)
        den = rng.randint(2, 4)
        m = Rational(a, den)
        b = rng.randint(-8, 8)

        # Pick two x-coordinates that are multiples of den apart for clean points
        x1 = rng.randint(-5, 5)
        x2 = x1 + den
        y1 = m * x1 + b
        y2 = m * x2 + b

        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)
        eq_latex = fmt_line_eq(m, b)

        dy = y2 - y1
        dx = x2 - x1
        steps = [
            TrustedLatex(f"${p1}, \\quad {p2}$"),
            TrustedLatex(f"$m = \\frac{{{latex(dy)}}}{{{latex(dx)}}} = {latex(m)}$"),
            TrustedLatex(f"${eq_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the line in slope-intercept"
                f" form that passes through "
                f"${p1} \\text{{ and }} {p2}$"
            ),
            answer_latex=TrustedLatex(f"${eq_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# ParallelPerpSlopeTemplate — subtopic "parallel_perp_slopes"
# ---------------------------------------------------------------------------


@register_template
class ParallelPerpSlopeTemplate:
    topic = Topic.GEOMETRY
    subtopic = "parallel_perp_slopes"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Given y = mx + b, find slope of a parallel line.
        m = random_nonzero_int(rng, -8, 8)
        b = rng.randint(-10, 10)
        line_eq = fmt_line_eq(m, b)
        answer = fmt_slope(m)

        steps = [
            TrustedLatex(f"${line_eq}$"),
            TrustedLatex(f"$m_{{\\parallel}} = {answer}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"A line is given by ${line_eq}$. What is the slope of any line parallel to it?"
            ),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # Given y = mx + b, find slope of a perpendicular line.
        # Never use m=0 (perpendicular slope would be undefined).
        variant = rng.choice(["integer_slope", "fractional_slope"])

        if variant == "integer_slope":
            m = random_nonzero_int(rng, -8, 8)
            b = rng.randint(-10, 10)
            line_eq = fmt_line_eq(m, b)
            perp_slope = Rational(-1, m)
        else:
            num = random_nonzero_int(rng, -7, 7)
            den = random_nonzero_int(rng, 2, 7)
            # Ensure the fraction is not an integer
            for _ in range(50):
                if num % den != 0:
                    break
                den = random_nonzero_int(rng, 2, 7)
            else:
                raise GenerationError("Parameter sampling exhausted")
            m = Rational(num, den)
            b = rng.randint(-10, 10)
            line_eq = fmt_line_eq(m, b)
            perp_slope = Rational(-den, num)

        answer = latex(perp_slope)

        steps = [
            TrustedLatex(f"${line_eq}, \\quad m = {latex(m)}$"),
            TrustedLatex(f"$m_{{\\perp}} = {answer}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"A line is given by ${line_eq}$. What is the slope of a line perpendicular to it?"
            ),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Given a line through two points, find the equation of the
        # perpendicular line through a third point.
        # Backward: pick perpendicular slope, pick third point, compute eq.
        perp_m_num = random_nonzero_int(rng, -5, 5)
        perp_m_den = random_nonzero_int(rng, 1, 5)
        perp_slope = Rational(perp_m_num, perp_m_den)

        # Original slope is the negative reciprocal of the perpendicular slope
        orig_slope = Rational(-perp_m_den, perp_m_num)

        # Build two distinct points on the original line
        x1 = rng.randint(-6, 6)
        y1 = rng.randint(-6, 6)
        # Step along so that the second point has integer-friendly coords
        t = random_nonzero_int(rng, 1, 4) * abs(perp_m_num)
        x2 = x1 + t
        y2_exact = Rational(y1) + orig_slope * t
        # Only keep if y2 is an integer for a cleaner problem
        if y2_exact != int(y2_exact):
            # Adjust: use denominator-friendly step
            t = abs(perp_m_num) * abs(perp_m_den)
            x2 = x1 + t
            y2_exact = Rational(y1) + orig_slope * t
        y2 = int(y2_exact)

        # Third point (the perpendicular line passes through here)
        x3 = rng.randint(-6, 6)
        y3 = rng.randint(-6, 6)

        # Perpendicular line: y - y3 = perp_slope (x - x3)
        # => y = perp_slope * x + (y3 - perp_slope * x3)
        perp_b = Rational(y3) - perp_slope * x3
        answer_eq = fmt_line_eq(perp_slope, perp_b)

        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)
        p3 = fmt_point(x3, y3)

        steps = [
            TrustedLatex(f"${p1}, \\quad {p2}, \\quad {p3}$"),
            TrustedLatex(f"$m = {latex(orig_slope)}$"),
            TrustedLatex(f"$m_{{\\perp}} = {latex(perp_slope)}$"),
            TrustedLatex(f"${answer_eq}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the line perpendicular"
                f" to the line through "
                f"${p1} \\text{{ and }} {p2}$ "
                f"that passes through ${p3}$"
            ),
            answer_latex=TrustedLatex(f"${answer_eq}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# LineEquationTemplate — subtopic "line_equation"
# ---------------------------------------------------------------------------


@register_template
class LineEquationTemplate:
    topic = Topic.GEOMETRY
    subtopic = "line_equation"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Given slope and a point, write equation in point-slope and slope-intercept form
        m = random_nonzero_int(rng, -3, 3)
        b = rng.randint(-8, 8)

        # Pick a point on the line
        x1 = random_nonzero_int(rng, -5, 5)
        y1 = m * x1 + b

        p1 = fmt_point(x1, y1)

        # Point-slope form: y - y1 = m(x - x1)
        if y1 == 0:
            ps_lhs = "y"
        elif y1 > 0:
            ps_lhs = f"y - {latex(y1)}"
        else:
            ps_lhs = f"y + {latex(abs(y1))}"

        if x1 == 0:
            ps_rhs = f"{latex(m)} x"
        elif x1 > 0:
            ps_rhs = f"{latex(m)}(x - {latex(x1)})"
        else:
            ps_rhs = f"{latex(m)}(x + {latex(abs(x1))})"

        point_slope_latex = f"{ps_lhs} = {ps_rhs}"
        si_latex = fmt_line_eq(m, b)

        steps = [
            TrustedLatex(f"${p1}, \\quad m = {latex(m)}$"),
            TrustedLatex(f"${point_slope_latex}$"),
            TrustedLatex(f"${si_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the line with slope $m = {latex(m)}$"
                f" passing through ${p1}$. Give both point-slope and"
                f" slope-intercept forms."
            ),
            answer_latex=TrustedLatex(f"${point_slope_latex}$, or equivalently ${si_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # Given two points, find equation in standard form Ax + By = C
        # Backward: pick two points with integer coords, ensure x1 != x2
        x1 = rng.randint(-5, 5)
        for _ in range(50):
            x2 = rng.randint(-5, 5)
            if x2 != x1:
                break
        else:
            raise GenerationError("Parameter sampling exhausted")
        y1 = rng.randint(-5, 5)
        y2 = rng.randint(-5, 5)

        # Standard form: dy*x - dx*y = dy*x1 - dx*y1
        dy = y2 - y1
        dx = x2 - x1
        A = dy
        B = -dx
        C = dy * x1 - dx * y1

        # Simplify by GCD and ensure A > 0
        from math import gcd

        g = gcd(gcd(abs(A), abs(B)), abs(C)) if C != 0 else gcd(abs(A), abs(B))
        if g > 0:
            A //= g
            B //= g
            C //= g
        if A < 0:
            A, B, C = -A, -B, -C

        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)

        # Build standard form string: Ax + By = C
        if A == 0:
            ax_str = ""
        elif A == 1:
            ax_str = "x"
        elif A == -1:
            ax_str = "-x"
        else:
            ax_str = f"{A}x"

        if B == 0:
            by_str = ""
        elif B == 1:
            by_str = "+ y" if A != 0 else "y"
        elif B == -1:
            by_str = "- y"
        elif B > 0 and A != 0:
            by_str = f"+ {B}y"
        else:
            by_str = f"{B}y"

        std_form = f"{ax_str} {by_str} = {C}".strip()

        m_frac = f"\\frac{{{latex(dy)}}}{{{latex(dx)}}}"
        steps = [
            TrustedLatex(f"${p1}, \\quad {p2}$"),
            TrustedLatex(f"$m = {m_frac}$"),
            TrustedLatex(f"${std_form}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the line passing through "
                f"${p1} \\text{{ and }} {p2}$ "
                f"in standard form $Ax + By = C$"
            ),
            answer_latex=TrustedLatex(f"${std_form}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Line through a point perpendicular to a given line
        # Backward: pick given line y = mx + b, pick point not on it
        m_given = random_nonzero_int(rng, -3, 3)
        b_given = rng.randint(-6, 6)

        # Point not on the given line
        px = rng.randint(-5, 5)
        py_on_line = m_given * px + b_given
        py = py_on_line + random_nonzero_int(rng, -3, 3)

        # Perpendicular slope
        m_perp = Rational(-1, m_given)
        b_perp = simplify(py - m_perp * px)

        given_eq = fmt_line_eq(m_given, b_given)
        pt = fmt_point(px, py)
        answer_eq = fmt_line_eq(m_perp, b_perp)

        steps = [
            TrustedLatex(f"${given_eq}, \\quad P = {pt}$"),
            TrustedLatex(f"$m_{{\\perp}} = {latex(m_perp)}$"),
            TrustedLatex(f"${answer_eq}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the line passing through ${pt}$"
                f" that is perpendicular to ${given_eq}$."
                f" Give the answer in slope-intercept form."
            ),
            answer_latex=TrustedLatex(f"${answer_eq}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )
