"""Shared helpers for geometry templates.

Pure functions returning LaTeX strings or generating useful coordinate values.
"""

from __future__ import annotations

import random

from sympy import Rational, latex, sqrt

from app.engine.types import GenerationError

# Common Pythagorean triples for generating integer distances
_PYTHAGOREAN_TRIPLES = [
    (3, 4, 5),
    (5, 12, 13),
    (8, 15, 17),
    (7, 24, 25),
    (6, 8, 10),
    (9, 12, 15),
]


def fmt_point(x, y) -> str:
    """Format a coordinate point as LaTeX: (3, -2)."""
    return f"({latex(x)}, {latex(y)})"


def fmt_slope(num, den=1) -> str:
    """Format a slope value as LaTeX. Returns integer or fraction."""
    if den == 1:
        return latex(num)
    return latex(Rational(num, den))


def fmt_line_eq(m, b) -> str:
    """Format y = mx + b in LaTeX."""
    if m == 0:
        return f"y = {latex(b)}"
    m_str = latex(m)
    if m == 1:
        m_str = ""
    elif m == -1:
        m_str = "-"
    if b == 0:
        return f"y = {m_str}x"
    b_val = Rational(b)
    sign = "+" if b_val > 0 else "-"
    return f"y = {m_str}x {sign} {latex(abs(b_val))}"


def pythagorean_triple(rng: random.Random) -> tuple[int, int, int]:
    """Return a random (a, b, c) where a² + b² = c²."""
    return rng.choice(_PYTHAGOREAN_TRIPLES)


def random_nonzero_int(rng: random.Random, low: int, high: int) -> int:
    """Random integer in [low, high] excluding 0."""
    for _ in range(50):
        val = rng.randint(low, high)
        if val != 0:
            return val
    raise GenerationError("Parameter sampling exhausted")


def distance_between(x1, y1, x2, y2):
    """Compute exact distance between two points using SymPy."""
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def midpoint_of(x1, y1, x2, y2) -> tuple:
    """Compute midpoint as (Rational, Rational)."""
    return (Rational(x1 + x2, 2), Rational(y1 + y2, 2))


def shoelace_area(x1, y1, x2, y2, x3, y3):
    """Compute triangle area via Shoelace formula. Returns positive Rational."""
    area = Rational(abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)), 2)
    return area
