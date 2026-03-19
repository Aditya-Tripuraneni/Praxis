"""Shared LaTeX formatting helpers for domain problem templates.

All functions return raw LaTeX strings (without $ delimiters).
"""

from __future__ import annotations

import random

from sympy import latex, oo

from app.engine.types import GenerationError


def fmt_interval(lower, upper, lower_inclusive: bool = True, upper_inclusive: bool = True) -> str:
    """Format a single interval in LaTeX notation.

    Examples:
        fmt_interval(-3, oo, True, False)  -> "[-3, \\infty)"
        fmt_interval(-oo, 5, False, True)  -> "(-\\infty, 5]"
        fmt_interval(Rational(1,2), 3)     -> "[\\frac{1}{2}, 3]"
    """
    left = "[" if lower_inclusive else "("
    right = "]" if upper_inclusive else ")"

    if lower == -oo:
        left = "("
        lower_str = "-\\infty"
    else:
        lower_str = latex(lower)

    if upper == oo:
        right = ")"
        upper_str = "\\infty"
    else:
        upper_str = latex(upper)

    return f"{left}{lower_str}, {upper_str}{right}"


def fmt_union(intervals: list[str]) -> str:
    """Join multiple interval strings with \\cup.

    Example:
        fmt_union(["(-\\infty, -3)", "(3, \\infty)"])
        -> "(-\\infty, -3) \\cup (3, \\infty)"
    """
    return " \\cup ".join(intervals)


def fmt_set_minus(excluded: list) -> str:
    """Format domain as R minus a finite set.

    Example:
        fmt_set_minus([2, -3])  -> "\\mathbb{R} \\setminus \\{-3, 2\\}"
    """
    sorted_vals = sorted(excluded, key=lambda v: float(v))
    vals_str = ", ".join(latex(v) for v in sorted_vals)
    return f"\\mathbb{{R}} \\setminus \\{{{vals_str}\\}}"


def fmt_all_reals() -> str:
    return "\\mathbb{R}"


def fmt_periodic_exclusion(base_str: str, period_str: str) -> str:
    """Format periodic domain exclusion for trig functions.

    Example:
        fmt_periodic_exclusion("\\frac{\\pi}{2}", "\\pi")
        -> "\\mathbb{R} \\setminus \\{\\frac{\\pi}{2} + n\\pi \\mid n \\in \\mathbb{Z}\\}"
    """
    return (
        f"\\mathbb{{R}} \\setminus \\{{{base_str} + n{period_str} \\mid n \\in \\mathbb{{Z}}\\}}"
    )


def _distinct_pair(rng: random.Random, lo: int, hi: int) -> tuple[int, int]:
    """Return two distinct integers in [lo, hi], with a < b."""
    a = rng.randint(lo, hi)
    for _ in range(50):
        b = rng.randint(lo, hi)
        if b != a:
            break
    else:
        raise GenerationError("Parameter sampling exhausted")
    return (min(a, b), max(a, b))
