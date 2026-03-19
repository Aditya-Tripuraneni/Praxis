"""Shared helpers for trigonometry templates.

Pure functions and pre-computed lookup tables for all 6 trig functions
across the 16 standard unit-circle angles. The STANDARD_VALUES table is
computed once at import time so that generation code can do O(1) lookups
instead of calling simplify() per problem.
"""

from __future__ import annotations

import random

import sympy
from sympy import (
    Integer,
    cos,
    cot,
    csc,
    latex,
    pi,
    sec,
    simplify,
    sin,
    tan,
)

from app.engine.types import Difficulty

# ---------------------------------------------------------------------------
# 1. Standard unit-circle angles in [0, 2pi)
# ---------------------------------------------------------------------------
STANDARD_ANGLES: list[sympy.Expr] = [
    Integer(0),
    pi / 6,
    pi / 4,
    pi / 3,
    pi / 2,
    2 * pi / 3,
    3 * pi / 4,
    5 * pi / 6,
    pi,
    7 * pi / 6,
    5 * pi / 4,
    4 * pi / 3,
    3 * pi / 2,
    5 * pi / 3,
    7 * pi / 4,
    11 * pi / 6,
]

# ---------------------------------------------------------------------------
# 2. All 6 trig functions registry
# ---------------------------------------------------------------------------
# Mapping: name -> (sympy callable, LaTeX command string)
TRIG_FUNCTIONS: dict[str, tuple[sympy.core.function.Function, str]] = {
    "sin": (sin, r"\sin"),
    "cos": (cos, r"\cos"),
    "tan": (tan, r"\tan"),
    "cot": (cot, r"\cot"),
    "sec": (sec, r"\sec"),
    "csc": (csc, r"\csc"),
}

# ---------------------------------------------------------------------------
# 3. Pre-computed standard values table
# ---------------------------------------------------------------------------


def _build_standard_values() -> dict[tuple[str, sympy.Expr], sympy.Expr]:
    """Pre-compute exact trig values for all standard angle/function combos.

    Skips combinations that are undefined (e.g. tan(pi/2), csc(0)).
    Runs once at module import.
    """
    table: dict[tuple[str, sympy.Expr], sympy.Expr] = {}
    for func_name, (func, _) in TRIG_FUNCTIONS.items():
        for angle in STANDARD_ANGLES:
            try:
                val = simplify(func(angle))
                if val.is_finite:
                    table[(func_name, angle)] = val
            except Exception:  # noqa: BLE001
                pass  # undefined value — skip
    return table


STANDARD_VALUES: dict[tuple[str, sympy.Expr], sympy.Expr] = _build_standard_values()

# ---------------------------------------------------------------------------
# 4. Angle selection helpers (difficulty-scaled)
# ---------------------------------------------------------------------------

# Pre-built pools so we don't recreate lists on every call
_EASY_ANGLES: list[sympy.Expr] = [Integer(0), pi / 2, pi, 3 * pi / 2]
_MEDIUM_ANGLES: list[sympy.Expr] = [pi / 6, pi / 4, pi / 3]


def pick_angle(difficulty: Difficulty, rng: random.Random) -> sympy.Expr:
    """Pick a random standard angle appropriate for the difficulty level.

    EASY   -- axis angles only: 0, pi/2, pi, 3pi/2
    MEDIUM -- Q1 special angles: pi/6, pi/4, pi/3
    HARD   -- any of the 16 standard angles
    """
    if difficulty == Difficulty.EASY:
        return rng.choice(_EASY_ANGLES)
    if difficulty == Difficulty.MEDIUM:
        return rng.choice(_MEDIUM_ANGLES)
    return rng.choice(STANDARD_ANGLES)


# ---------------------------------------------------------------------------
# 5. Function selection helpers (difficulty-scaled)
# ---------------------------------------------------------------------------

_EASY_FUNCS = ["sin", "cos"]
_MEDIUM_FUNCS = ["sin", "cos", "tan"]
_HARD_FUNCS = ["sin", "cos", "tan", "cot", "sec", "csc"]


def pick_trig_func(
    difficulty: Difficulty,
    rng: random.Random,
    exclude_undefined_at: sympy.Expr | None = None,
) -> tuple[str, sympy.core.function.Function, str]:
    """Pick a random trig function appropriate for difficulty.

    Returns (name, sympy_func, latex_cmd).  If *exclude_undefined_at* is
    given, functions that are undefined at that angle are filtered out.
    """
    if difficulty == Difficulty.EASY:
        candidates = list(_EASY_FUNCS)
    elif difficulty == Difficulty.MEDIUM:
        candidates = list(_MEDIUM_FUNCS)
    else:
        candidates = list(_HARD_FUNCS)

    if exclude_undefined_at is not None:
        candidates = [
            name for name in candidates if (name, exclude_undefined_at) in STANDARD_VALUES
        ]

    # Fallback: sin/cos are always defined at every standard angle
    if not candidates:
        candidates = list(_EASY_FUNCS)

    name = rng.choice(candidates)
    func, latex_cmd = TRIG_FUNCTIONS[name]
    return name, func, latex_cmd


# ---------------------------------------------------------------------------
# 6. Coefficient and multiplier generators
# ---------------------------------------------------------------------------


def pick_coefficient(difficulty: Difficulty, rng: random.Random) -> int:
    """Pick a coefficient for trig expressions, scaled by difficulty.

    EASY=1, MEDIUM in {1,2}, HARD in [1..4].
    """
    if difficulty == Difficulty.EASY:
        return 1
    if difficulty == Difficulty.MEDIUM:
        return rng.choice([1, 2])
    return rng.randint(1, 4)


def pick_angle_multiplier(difficulty: Difficulty, rng: random.Random) -> int:
    """Pick an angle multiplier (e.g. 2 for sin(2x)), scaled by difficulty.

    EASY=1, MEDIUM in {1,2}, HARD in {1,2,3}.
    """
    if difficulty == Difficulty.EASY:
        return 1
    if difficulty == Difficulty.MEDIUM:
        return rng.choice([1, 2])
    return rng.choice([1, 2, 3])


def pick_phase_shift(difficulty: Difficulty, rng: random.Random) -> sympy.Expr:
    """Pick a phase shift for equations like sin(2x + pi/4), scaled by difficulty.

    EASY=0, MEDIUM in {0, pi/6, pi/4, pi/3}, HARD adds pi/2 and pi.
    """
    if difficulty == Difficulty.EASY:
        return Integer(0)
    if difficulty == Difficulty.MEDIUM:
        return rng.choice([Integer(0), pi / 6, pi / 4, pi / 3])
    return rng.choice([Integer(0), pi / 6, pi / 4, pi / 3, pi / 2, pi])


# ---------------------------------------------------------------------------
# 7. Solution finder
# ---------------------------------------------------------------------------

_TWO_PI_FLOAT = float((2 * pi).evalf())


def solve_trig_basic(
    func_name: str,
    value: sympy.Expr,
    multiplier: int = 1,
    phase: sympy.Expr = Integer(0),
) -> list[sympy.Expr]:
    """Find all solutions to func(multiplier*x + phase) = value in [0, 2pi).

    Uses the pre-computed STANDARD_VALUES table for exact matching.
    Returns a sorted list of exact x values.
    """
    # Find base angles theta where func(theta) == value
    base_solutions: list[sympy.Expr] = [
        angle
        for (fname, angle), val in STANDARD_VALUES.items()
        if fname == func_name and simplify(val - value) == 0
    ]

    if not base_solutions:
        return []

    # Period: pi for tan/cot, 2*pi for sin/cos/sec/csc
    period = pi if func_name in ("tan", "cot") else 2 * pi

    solutions: list[sympy.Expr] = []
    for theta in base_solutions:
        # Solve: multiplier*x + phase = theta + period*k
        # => x = (theta - phase + period*k) / multiplier
        for k in range(-2 * multiplier, 2 * multiplier + 1):
            x = simplify((theta - phase + period * k) / multiplier)
            x_float = float(x.evalf())
            if not (-1e-10 <= x_float < _TWO_PI_FLOAT - 1e-10):
                continue
            # Exclude solutions that are effectively 2*pi
            if abs(x_float - _TWO_PI_FLOAT) < 1e-10:
                continue
            # Normalise near-zero negatives
            if abs(x_float) < 1e-10:
                x = Integer(0)
            # Deduplicate
            if not any(simplify(x - s) == 0 for s in solutions):
                solutions.append(x)

    return sorted(solutions, key=lambda s: float(s.evalf()))


# ---------------------------------------------------------------------------
# 8. LaTeX formatting helpers
# ---------------------------------------------------------------------------


def format_angle_latex(angle: sympy.Expr) -> str:
    """Format a standard angle as LaTeX."""
    return latex(angle)


def format_solution_set(solutions: list[sympy.Expr]) -> str:
    r"""Format a list of solutions as a LaTeX set: x \in \{pi/6, 5pi/6\}."""
    if not solutions:
        return r"\text{No solution}"
    sol_strs = [latex(s) for s in solutions]
    return r"x \in \left\{" + ", ".join(sol_strs) + r"\right\}"


def is_defined_at(func_name: str, angle: sympy.Expr) -> bool:
    """Check if a trig function is defined at the given angle."""
    return (func_name, angle) in STANDARD_VALUES


# ---------------------------------------------------------------------------
# 9. Standard trig values for quadratic generation
# ---------------------------------------------------------------------------


def get_standard_func_values(func_name: str) -> list[sympy.Expr]:
    """Get all distinct values that *func_name* takes at standard angles.

    Useful for backward construction of quadratic trig equations:
    pick two values from this list as roots.
    """
    values: set[sympy.Expr] = set()
    for (fname, _angle), val in STANDARD_VALUES.items():
        if fname == func_name:
            values.add(val)
    return sorted(values, key=lambda v: float(v.evalf()))
