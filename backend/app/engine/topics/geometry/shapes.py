"""Coordinate geometry templates — measurement-related problems.

Covers distance formula, midpoint formula, triangle area via coordinates,
and perpendicular bisectors.
"""

from __future__ import annotations

import random

from sympy import Rational, latex, simplify

from app.engine.registry import register_template
from app.engine.topics.geometry._helpers import (
    distance_between,
    fmt_line_eq,
    fmt_point,
    midpoint_of,
    pythagorean_triple,
    random_nonzero_int,
    shoelace_area,
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
# DistanceFormulaTemplate — subtopic "distance_formula"
# ---------------------------------------------------------------------------


@register_template
class DistanceFormulaTemplate:
    topic = Topic.GEOMETRY
    subtopic = "distance_formula"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Pythagorean triple for a clean integer distance.
        a, b, c = pythagorean_triple(rng)

        # Randomly flip signs for variety
        if rng.random() < 0.5:
            a = -a
        if rng.random() < 0.5:
            b = -b

        p1 = fmt_point(0, 0)
        p2 = fmt_point(a, b)

        radicand = a**2 + b**2
        steps = [
            TrustedLatex(f"$(x_1, y_1) = {p1}, \\quad (x_2, y_2) = {p2}$"),
            TrustedLatex(
                f"$d = \\sqrt{{{latex(a**2)} + {latex(b**2)}}} = \\sqrt{{{latex(radicand)}}}$"
            ),
            TrustedLatex(f"$d = {latex(c)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the distance between ${p1} \\text{{ and }} {p2}$"),
            answer_latex=TrustedLatex(f"$d = {latex(c)}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # General integer coords in [-8, 8]; distance is a simplified radical.
        x1 = rng.randint(-8, 8)
        y1 = rng.randint(-8, 8)
        x2 = rng.randint(-8, 8)
        y2 = rng.randint(-8, 8)

        # Ensure the two points are not identical
        for _ in range(50):
            if not (x1 == x2 and y1 == y2):
                break
            x2 = rng.randint(-8, 8)
            y2 = rng.randint(-8, 8)
        else:
            raise GenerationError("Parameter sampling exhausted")

        dist = distance_between(x1, y1, x2, y2)
        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)

        dx_val = x2 - x1
        dy_val = y2 - y1
        radicand = dx_val**2 + dy_val**2
        steps = [
            TrustedLatex(f"$(x_1, y_1) = {p1}, \\quad (x_2, y_2) = {p2}$"),
            TrustedLatex(
                f"$d = \\sqrt{{{latex(dx_val)}^2"
                f" + {latex(dy_val)}^2}}"
                f" = \\sqrt{{{latex(radicand)}}}$"
            ),
            TrustedLatex(f"$d = {latex(dist)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the distance between ${p1} \\text{{ and }} {p2}$"),
            answer_latex=TrustedLatex(f"$d = {latex(dist)}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Larger coordinate range [-15, 15] for more complex radicals.
        x1 = rng.randint(-15, 15)
        y1 = rng.randint(-15, 15)
        x2 = rng.randint(-15, 15)
        y2 = rng.randint(-15, 15)

        # Ensure at least one coordinate differs
        for _ in range(50):
            if not (x1 == x2 and y1 == y2):
                break
            x2 = rng.randint(-15, 15)
            y2 = rng.randint(-15, 15)
        else:
            raise GenerationError("Parameter sampling exhausted")

        dist = distance_between(x1, y1, x2, y2)
        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)

        dx_val = x2 - x1
        dy_val = y2 - y1
        radicand = dx_val**2 + dy_val**2
        steps = [
            TrustedLatex(f"$(x_1, y_1) = {p1}, \\quad (x_2, y_2) = {p2}$"),
            TrustedLatex(
                f"$d = \\sqrt{{{latex(dx_val)}^2"
                f" + {latex(dy_val)}^2}}"
                f" = \\sqrt{{{latex(radicand)}}}$"
            ),
            TrustedLatex(f"$d = {latex(dist)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the distance between ${p1} \\text{{ and }} {p2}$"),
            answer_latex=TrustedLatex(f"$d = {latex(dist)}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# MidpointFormulaTemplate — subtopic "midpoint_formula"
# ---------------------------------------------------------------------------


@register_template
class MidpointFormulaTemplate:
    topic = Topic.GEOMETRY
    subtopic = "midpoint_formula"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Backward: pick midpoint M with integer coords, pick P1, compute P2
        mx = rng.randint(-5, 5)
        my = rng.randint(-5, 5)

        x1 = rng.randint(-5, 5)
        y1 = rng.randint(-5, 5)

        x2 = 2 * mx - x1
        y2 = 2 * my - y1

        # Edge case: endpoints must not be identical
        for _ in range(50):
            if not (x1 == x2 and y1 == y2):
                break
            x1 = rng.randint(-5, 5)
            y1 = rng.randint(-5, 5)
            x2 = 2 * mx - x1
            y2 = 2 * my - y1
        else:
            raise GenerationError("Parameter sampling exhausted")

        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)

        steps = [
            TrustedLatex(f"${p1}, \\quad {p2}$"),
            TrustedLatex(
                f"$M = \\left("
                f"\\frac{{{latex(x1)}+{latex(x2)}}}{{{2}}},"
                f" \\frac{{{latex(y1)}+{latex(y2)}}}"
                f"{{{2}}}\\right)$"
            ),
            TrustedLatex(f"$M = {fmt_point(mx, my)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the midpoint of the segment with endpoints ${p1} \\text{{ and }} {p2}$"
            ),
            answer_latex=TrustedLatex(f"$M = {fmt_point(mx, my)}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # Given midpoint M and one endpoint P1, find the other endpoint P2
        mx = rng.randint(-6, 6)
        my = rng.randint(-6, 6)

        x1 = rng.randint(-6, 6)
        y1 = rng.randint(-6, 6)

        x2 = 2 * mx - x1
        y2 = 2 * my - y1

        # Edge case: endpoints must not be identical
        for _ in range(50):
            if not (x1 == x2 and y1 == y2):
                break
            x1 = rng.randint(-6, 6)
            y1 = rng.randint(-6, 6)
            x2 = 2 * mx - x1
            y2 = 2 * my - y1
        else:
            raise GenerationError("Parameter sampling exhausted")

        p1 = fmt_point(x1, y1)
        m_pt = fmt_point(mx, my)

        steps = [
            TrustedLatex(f"$M = {m_pt}, \\quad P_1 = {p1}$"),
            TrustedLatex(
                f"$P_2 = (2 \\cdot {latex(mx)}"
                f" - {latex(x1)},"
                f" \\; 2 \\cdot {latex(my)}"
                f" - {latex(y1)})$"
            ),
            TrustedLatex(f"$P_2 = {fmt_point(x2, y2)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"The midpoint of a segment is "
                f"$M = {m_pt} \\text{{ and one endpoint"
                f" is }} {p1}$. Find the other endpoint"
            ),
            answer_latex=TrustedLatex(f"$P_2 = {fmt_point(x2, y2)}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Fractional midpoint: pick P1 and P2 with odd integers so midpoint has .5
        def _odd(r: random.Random, lo: int, hi: int) -> int:
            v = r.randint(lo, hi)
            return v if v % 2 != 0 else v + 1

        x1 = _odd(rng, -9, 9)
        y1 = _odd(rng, -9, 9)
        x2 = _odd(rng, -9, 9)
        y2 = _odd(rng, -9, 9)

        # Ensure endpoints are not identical
        for _ in range(50):
            if not (x1 == x2 and y1 == y2):
                break
            x2 = _odd(rng, -9, 9)
            y2 = _odd(rng, -9, 9)
        else:
            raise GenerationError("Parameter sampling exhausted")

        mid_x, mid_y = midpoint_of(x1, y1, x2, y2)

        p1 = fmt_point(x1, y1)
        p2 = fmt_point(x2, y2)

        steps = [
            TrustedLatex(f"${p1}, \\quad {p2}$"),
            TrustedLatex(
                f"$M = \\left("
                f"\\frac{{{latex(x1)}+{latex(x2)}}}{{{2}}},"
                f" \\frac{{{latex(y1)}+{latex(y2)}}}"
                f"{{{2}}}\\right)$"
            ),
            TrustedLatex(f"$M = ({latex(mid_x)}, {latex(mid_y)})$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the midpoint of the segment with endpoints ${p1} \\text{{ and }} {p2}$"
            ),
            answer_latex=TrustedLatex(f"$M = ({latex(mid_x)}, {latex(mid_y)})$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# TriangleAreaCoordsTemplate — subtopic "triangle_area_coords"
# ---------------------------------------------------------------------------


@register_template
class TriangleAreaCoordsTemplate:
    topic = Topic.GEOMETRY
    subtopic = "triangle_area_coords"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # One vertex at origin, others at small positive coords
        # Backward: pick area A (integer), place vertex at (0,0),
        # second at (b,0) on x-axis, third at (cx, 2A/b)
        area = rng.randint(1, 12)
        b = rng.randint(1, 6)
        # 2A/b must be integer => pick area as multiple of b, or adjust
        # Ensure 2*area is divisible by b
        for _ in range(50):
            if (2 * area) % b == 0:
                break
            b = rng.randint(1, 6)
        else:
            raise GenerationError("Parameter sampling exhausted")

        cx = rng.randint(0, 6)
        cy = (2 * area) // b

        x1, y1 = 0, 0
        x2, y2 = b, 0
        x3, y3 = cx, cy

        # Verify non-collinear (guaranteed since cy > 0 and b > 0)
        computed_area = shoelace_area(x1, y1, x2, y2, x3, y3)

        a_pt = fmt_point(x1, y1)
        b_pt = fmt_point(x2, y2)
        c_pt = fmt_point(x3, y3)

        det_val = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        steps = [
            TrustedLatex(f"$A = {a_pt}, \\quad B = {b_pt}, \\quad C = {c_pt}$"),
            TrustedLatex(f"$\\text{{Area}} = \\frac{{1}}{{2}}|{latex(det_val)}|$"),
            TrustedLatex(f"$\\text{{Area}} = {latex(computed_area)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the area of the triangle with vertices "
                f"$A = {a_pt},\\; B = {b_pt},\\; C = {c_pt}$"
            ),
            answer_latex=TrustedLatex(f"$\\text{{Area}} = {latex(computed_area)}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # General position, all integer coords [-6,6]
        for _ in range(10):
            x1 = rng.randint(-6, 6)
            y1 = rng.randint(-6, 6)
            x2 = rng.randint(-6, 6)
            y2 = rng.randint(-6, 6)
            x3 = rng.randint(-6, 6)
            y3 = rng.randint(-6, 6)

            area = shoelace_area(x1, y1, x2, y2, x3, y3)
            if area != 0:
                a_pt = fmt_point(x1, y1)
                b_pt = fmt_point(x2, y2)
                c_pt = fmt_point(x3, y3)

                det_val = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
                steps = [
                    TrustedLatex(f"$A = {a_pt}, \\quad B = {b_pt}, \\quad C = {c_pt}$"),
                    TrustedLatex(f"$\\text{{Area}} = \\frac{{1}}{{2}}|{latex(det_val)}|$"),
                    TrustedLatex(f"$\\text{{Area}} = {latex(area)}$"),
                ]

                return GeneratedProblem(
                    question_latex=TrustedLatex(
                        f"Find the area of the triangle with "
                        f"vertices $A = {a_pt},\\; "
                        f"B = {b_pt},\\; C = {c_pt}$"
                    ),
                    answer_latex=TrustedLatex(f"$\\text{{Area}} = {latex(area)}$"),
                    topic=Topic.GEOMETRY,
                    difficulty=Difficulty.MEDIUM,
                    subtopic=self.subtopic,
                    solution_steps=tuple(steps),
                )

        # Fallback: guaranteed non-collinear triangle
        return self._fallback(Difficulty.MEDIUM, rng)

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Larger coords [-10,10], verify non-collinear
        for _ in range(10):
            x1 = rng.randint(-10, 10)
            y1 = rng.randint(-10, 10)
            x2 = rng.randint(-10, 10)
            y2 = rng.randint(-10, 10)
            x3 = rng.randint(-10, 10)
            y3 = rng.randint(-10, 10)

            area = shoelace_area(x1, y1, x2, y2, x3, y3)
            if area != 0:
                a_pt = fmt_point(x1, y1)
                b_pt = fmt_point(x2, y2)
                c_pt = fmt_point(x3, y3)

                det_val = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
                steps = [
                    TrustedLatex(f"$A = {a_pt}, \\quad B = {b_pt}, \\quad C = {c_pt}$"),
                    TrustedLatex(f"$\\text{{Area}} = \\frac{{1}}{{2}}|{latex(det_val)}|$"),
                    TrustedLatex(f"$\\text{{Area}} = {latex(area)}$"),
                ]

                return GeneratedProblem(
                    question_latex=TrustedLatex(
                        f"Find the area of the triangle with "
                        f"vertices $A = {a_pt},\\; "
                        f"B = {b_pt},\\; C = {c_pt}$"
                    ),
                    answer_latex=TrustedLatex(f"$\\text{{Area}} = {latex(area)}$"),
                    topic=Topic.GEOMETRY,
                    difficulty=Difficulty.HARD,
                    subtopic=self.subtopic,
                    solution_steps=tuple(steps),
                )

        # Fallback: guaranteed non-collinear triangle
        return self._fallback(Difficulty.HARD, rng)

    # -- Fallback -----------------------------------------------------------

    def _fallback(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Guaranteed non-collinear triangle as a fallback."""
        x1, y1 = 0, 0
        x2, y2 = rng.randint(1, 6), 0
        x3, y3 = rng.randint(0, 6), rng.randint(1, 6)

        area = shoelace_area(x1, y1, x2, y2, x3, y3)

        a_pt = fmt_point(x1, y1)
        b_pt = fmt_point(x2, y2)
        c_pt = fmt_point(x3, y3)

        det_val = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        steps = [
            TrustedLatex(f"$A = {a_pt}, \\quad B = {b_pt}, \\quad C = {c_pt}$"),
            TrustedLatex(f"$\\text{{Area}} = \\frac{{1}}{{2}}|{latex(det_val)}|$"),
            TrustedLatex(f"$\\text{{Area}} = {latex(area)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the area of the triangle with vertices "
                f"$A = {a_pt},\\; B = {b_pt},\\; C = {c_pt}$"
            ),
            answer_latex=TrustedLatex(f"$\\text{{Area}} = {latex(area)}$"),
            topic=Topic.GEOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# PerpendicularBisectorTemplate — subtopic "perpendicular_bisector"
# ---------------------------------------------------------------------------


@register_template
class PerpendicularBisectorTemplate:
    topic = Topic.GEOMETRY
    subtopic = "perpendicular_bisector"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # Horizontal or vertical segment — perp bisector is vertical or horizontal
        horizontal = rng.choice([True, False])

        if horizontal:
            # Endpoints (x1, k), (x2, k) with x1 != x2
            k = rng.randint(-5, 5)
            x1 = rng.randint(-5, 4)
            x2 = x1 + rng.randint(1, 5)  # ensure x2 > x1
            mid_x = Rational(x1 + x2, 2)

            p_a = fmt_point(x1, k)
            p_b = fmt_point(x2, k)
            answer = f"$x = {latex(mid_x)}$"
            steps = [
                TrustedLatex(f"$A = {p_a}, \\quad B = {p_b}$"),
                TrustedLatex(
                    f"$M = \\left(\\frac{{{latex(x1)}+{latex(x2)}}}{{{2}}}, {latex(k)}\\right)$"
                ),
                TrustedLatex(f"$x = {latex(mid_x)}$"),
            ]
        else:
            # Endpoints (k, y1), (k, y2) with y1 != y2
            k = rng.randint(-5, 5)
            y1 = rng.randint(-5, 4)
            y2 = y1 + rng.randint(1, 5)  # ensure y2 > y1
            mid_y = Rational(y1 + y2, 2)

            p_a = fmt_point(k, y1)
            p_b = fmt_point(k, y2)
            answer = f"$y = {latex(mid_y)}$"
            steps = [
                TrustedLatex(f"$A = {p_a}, \\quad B = {p_b}$"),
                TrustedLatex(
                    f"$M = \\left({latex(k)}, \\frac{{{latex(y1)}+{latex(y2)}}}{{{2}}}\\right)$"
                ),
                TrustedLatex(f"$y = {latex(mid_y)}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the perpendicular"
                f" bisector of the segment with endpoints "
                f"$A = {p_a} \\text{{ and }} B = {p_b}$"
            ),
            answer_latex=TrustedLatex(answer),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        # Sloped segment with integer slope
        # Backward: pick integer slope m_seg, midpoint M, derive endpoints
        m_seg = random_nonzero_int(rng, -3, 3)

        # Midpoint with integer coordinates
        mx = rng.randint(-5, 5)
        my = rng.randint(-5, 5)

        # Endpoints equidistant from M along slope direction
        x1 = mx - 1
        y1 = my - m_seg
        x2 = mx + 1
        y2 = my + m_seg

        # Perpendicular bisector: slope = -1/m_seg, passes through M
        m_perp = Rational(-1, m_seg)
        b_perp = simplify(my - m_perp * mx)

        p_a = fmt_point(x1, y1)
        p_b = fmt_point(x2, y2)
        eq_latex = fmt_line_eq(m_perp, b_perp)

        steps = [
            TrustedLatex(f"$A = {p_a}, \\quad B = {p_b}$"),
            TrustedLatex(f"$M = {fmt_point(mx, my)}$"),
            TrustedLatex(f"$m_{{\\perp}} = {latex(m_perp)}$"),
            TrustedLatex(f"${eq_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the perpendicular"
                f" bisector of the segment with endpoints "
                f"$A = {p_a} \\text{{ and }} B = {p_b}$"
            ),
            answer_latex=TrustedLatex(f"${eq_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        # Segment with fractional slope, larger coordinates
        a_num = random_nonzero_int(rng, -5, 5)
        a_den = rng.randint(2, 4)

        # Midpoint with integer coordinates
        mx = rng.randint(-8, 8)
        my = rng.randint(-8, 8)

        # Endpoints: offset by (a_den, a_num) from midpoint
        x1 = mx - a_den
        y1 = my - a_num
        x2 = mx + a_den
        y2 = my + a_num

        # Perpendicular bisector: slope = -1/m_seg = -a_den/a_num
        m_perp = Rational(-a_den, a_num)
        b_perp = simplify(my - m_perp * mx)

        p_a = fmt_point(x1, y1)
        p_b = fmt_point(x2, y2)
        eq_latex = fmt_line_eq(m_perp, b_perp)

        steps = [
            TrustedLatex(f"$A = {p_a}, \\quad B = {p_b}$"),
            TrustedLatex(f"$M = {fmt_point(mx, my)}$"),
            TrustedLatex(f"$m_{{\\perp}} = {latex(m_perp)}$"),
            TrustedLatex(f"${eq_latex}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(
                f"Find the equation of the perpendicular"
                f" bisector of the segment with endpoints "
                f"$A = {p_a} \\text{{ and }} B = {p_b}$"
            ),
            answer_latex=TrustedLatex(f"${eq_latex}$"),
            topic=Topic.GEOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )
