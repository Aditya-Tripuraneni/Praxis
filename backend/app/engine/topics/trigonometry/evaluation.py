"""Trigonometry evaluation templates — trig functions and inverse trig.

Templates:
    TrigEvalTemplate   — Evaluate any of the 6 trig functions at standard angles.
    InverseTrigTemplate — Evaluate inverse trig functions and compositions.

Both use backward construction: the answer is determined first, then the
question is assembled around it.  Difficulty scales the function pool, angle
pool, and question complexity.
"""

from __future__ import annotations

import random

import sympy
from sympy import (
    Integer,
    Rational,
    acos,
    asin,
    atan,
    latex,
    pi,
    simplify,
    sqrt,
)

from app.engine.registry import register_template
from app.engine.topics.trigonometry._helpers import (
    STANDARD_VALUES,
    TRIG_FUNCTIONS,
    format_angle_latex,
    pick_angle,
    pick_trig_func,
)
from app.engine.types import (
    Difficulty,
    GeneratedProblem,
    GenerationError,
    Topic,
    TrustedLatex,
)

_MAX_RETRIES = 50

# ---------------------------------------------------------------------------
# Coterminal-angle shifts used for HARD trig evaluation
# ---------------------------------------------------------------------------
_COTERMINAL_SHIFTS: list[sympy.Expr] = [
    -4 * pi,
    -2 * pi,
    2 * pi,
    4 * pi,
]

# ---------------------------------------------------------------------------
# Inverse trig — principal-range lookup tables
# ---------------------------------------------------------------------------
# Map (inv_func_name, input_value) -> principal angle.  Built from
# STANDARD_VALUES so we stay consistent with the helpers module.

_INVERSE_FUNCS: dict[str, tuple[sympy.core.function.Function, str]] = {
    "arcsin": (asin, r"\arcsin"),
    "arccos": (acos, r"\arccos"),
    "arctan": (atan, r"\arctan"),
}

# Pre-compute the values each inverse function can accept at EASY / MEDIUM.
_EASY_INV_VALUES: list[sympy.Expr] = [
    Integer(0),
    Integer(1),
    Integer(-1),
]

_MEDIUM_INV_VALUES: list[sympy.Expr] = [
    sqrt(2) / 2,
    -sqrt(2) / 2,
    sqrt(3) / 2,
    -sqrt(3) / 2,
    Rational(1, 2),
    Rational(-1, 2),
]

# ---------------------------------------------------------------------------
# Pythagorean triples for HARD inverse trig compositions
# ---------------------------------------------------------------------------
# Each triple (a, b, c) satisfies a^2 + b^2 = c^2.
_PYTHAGOREAN_TRIPLES: list[tuple[int, int, int]] = [
    (3, 4, 5),
    (5, 12, 13),
    (8, 15, 17),
    (7, 24, 25),
]


# ---------------------------------------------------------------------------
# 1. TrigEvalTemplate
# ---------------------------------------------------------------------------


@register_template
class TrigEvalTemplate:
    """Evaluate a trig function at a standard angle.

    Supports all 6 functions (sin, cos, tan, cot, sec, csc) with
    difficulty-gated selection.  HARD mode adds coterminal-angle shifts so
    the student must reduce before evaluating.
    """

    topic = Topic.TRIGONOMETRY
    subtopic = "trig_evaluation"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        for _ in range(_MAX_RETRIES):
            result = self._try_generate(difficulty, rng)
            if result is not None:
                return result
        raise GenerationError("Parameter sampling exhausted")

    # -- private -----------------------------------------------------------

    def _try_generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem | None:
        # 1. Pick a base angle (always from the 16 standard angles).
        base_angle = pick_angle(difficulty, rng)

        # 2. Pick a function that is defined at the base angle.
        func_name, _func, latex_cmd = pick_trig_func(
            difficulty,
            rng,
            exclude_undefined_at=base_angle,
        )

        # 3. Verify the (func, base_angle) pair is in the lookup table.
        answer_val = STANDARD_VALUES.get((func_name, base_angle))
        if answer_val is None:
            return None  # retry

        # 4. For HARD, add a coterminal shift so the displayed angle is
        #    outside [0, 2pi).  The answer stays the same.
        if difficulty == Difficulty.HARD:
            shift = rng.choice(_COTERMINAL_SHIFTS)
            display_angle = base_angle + shift
        else:
            display_angle = base_angle

        # 5. Format LaTeX.
        angle_ltx = format_angle_latex(display_angle)
        question = f"Evaluate ${latex_cmd}\\left({angle_ltx}\\right)$."
        answer = f"${latex(answer_val)}$"

        if display_angle != base_angle:
            base_ltx = format_angle_latex(base_angle)
            steps = [
                TrustedLatex(f"${latex_cmd}\\left({angle_ltx}\\right)$"),
                TrustedLatex(f"$= {latex_cmd}\\left({base_ltx}\\right)$"),
                TrustedLatex(f"${latex(answer_val)}$"),
            ]
        else:
            steps = [
                TrustedLatex(f"${latex_cmd}\\left({angle_ltx}\\right)$"),
                TrustedLatex(f"${latex(answer_val)}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(answer),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "function": func_name,
                "angle": angle_ltx,
                "base_angle": format_angle_latex(base_angle),
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 2. InverseTrigTemplate
# ---------------------------------------------------------------------------


@register_template
class InverseTrigTemplate:
    """Evaluate inverse trig functions and compositions.

    EASY / MEDIUM: direct inverse evaluation (arcsin, arccos, arctan).
    HARD: compositions using Pythagorean triples, e.g. sec(arccos(3/5)).
    """

    topic = Topic.TRIGONOMETRY
    subtopic = "inverse_trig"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.HARD:
            return self._generate_composition(rng)
        return self._generate_direct(difficulty, rng)

    # -- direct inverse evaluation -----------------------------------------

    def _generate_direct(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """arcsin(v), arccos(v), or arctan(v) for a standard value."""
        if difficulty == Difficulty.EASY:
            value_pool = _EASY_INV_VALUES
            func_names = ["arcsin", "arccos", "arctan"]
        else:
            value_pool = _MEDIUM_INV_VALUES
            func_names = ["arcsin", "arccos", "arctan"]

        for _ in range(_MAX_RETRIES):
            inv_name = rng.choice(func_names)
            value = rng.choice(value_pool)
            inv_func, inv_latex_cmd = _INVERSE_FUNCS[inv_name]

            # Ensure the value is in the domain of the chosen function.
            # arcsin/arccos require |v| <= 1; arctan accepts all reals.
            if inv_name in ("arcsin", "arccos"):
                v_float = float(value.evalf())
                if abs(v_float) > 1.0 + 1e-12:
                    continue

            answer_val = simplify(inv_func(value))
            # Only accept results that are "nice" standard angles.
            if not answer_val.is_finite:
                continue
            # Reject non-standard angles (e.g. atan(sqrt(2)/2) is not
            # a rational multiple of pi and can't be simplified on paper)
            ratio = simplify(answer_val / pi)
            if answer_val != 0 and not ratio.is_rational:
                continue

            value_ltx = latex(value)
            question = f"Evaluate ${inv_latex_cmd}\\left({value_ltx}\\right)$."
            answer = f"${latex(answer_val)}$"

            steps = [
                TrustedLatex(f"${inv_latex_cmd}\\left({value_ltx}\\right)$"),
                TrustedLatex(f"${latex(answer_val)}$"),
            ]

            return GeneratedProblem(
                question_latex=TrustedLatex(question),
                answer_latex=TrustedLatex(answer),
                topic=Topic.TRIGONOMETRY,
                difficulty=difficulty,
                subtopic=self.subtopic,
                metadata={
                    "function": inv_name,
                    "value": value_ltx,
                },
                solution_steps=tuple(steps),
            )

        raise GenerationError("Parameter sampling exhausted")

    # -- composition with Pythagorean triples (HARD) -----------------------

    def _generate_composition(self, rng: random.Random) -> GeneratedProblem:
        """Generate e.g. sec(arccos(3/5)) using a Pythagorean triple."""
        for _ in range(_MAX_RETRIES):
            result = self._try_composition(rng)
            if result is not None:
                return result
        raise GenerationError("Parameter sampling exhausted")

    def _try_composition(self, rng: random.Random) -> GeneratedProblem | None:
        # 1. Pick a Pythagorean triple.
        a, b, c = rng.choice(_PYTHAGOREAN_TRIPLES)  # a^2 + b^2 = c^2

        # 2. Pick the inner inverse function and build the reference
        #    triangle sides (adj, opp, hyp) from the triple.
        inner_choice = rng.choice(["arcsin", "arccos", "arctan"])

        if inner_choice == "arcsin":
            # arcsin(opp/hyp) => opp, adj, hyp
            opp, adj, hyp = a, b, c
            inner_value = Rational(opp, hyp)
            inner_latex_cmd = r"\arcsin"
        elif inner_choice == "arccos":
            # arccos(adj/hyp) => adj, opp, hyp
            adj, opp, hyp = a, b, c
            inner_value = Rational(adj, hyp)
            inner_latex_cmd = r"\arccos"
        else:
            # arctan(opp/adj) => opp, adj, hyp
            opp, adj, hyp = a, b, c
            inner_value = Rational(opp, adj)
            inner_latex_cmd = r"\arctan"

        # 3. Pick an outer trig function (any of the 6).
        outer_name = rng.choice(list(TRIG_FUNCTIONS.keys()))
        _, outer_latex_cmd = TRIG_FUNCTIONS[outer_name]

        # 4. Compute the answer from the triangle.
        answer_val = _triangle_trig(outer_name, opp, adj, hyp)
        if answer_val is None:
            return None  # undefined combo (e.g. cot when opp=0 — won't happen with our triples)

        # 5. Format.
        inner_ltx = latex(inner_value)
        question = (
            f"Evaluate ${outer_latex_cmd}\\left("
            f"{inner_latex_cmd}\\left({inner_ltx}\\right)"
            f"\\right)$."
        )
        answer = f"${latex(answer_val)}$"

        comp_ltx = f"{outer_latex_cmd}\\left({inner_latex_cmd}\\left({inner_ltx}\\right)\\right)"
        steps = [
            TrustedLatex(f"${comp_ltx}$"),
            TrustedLatex(f"${latex(answer_val)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(answer),
            topic=Topic.TRIGONOMETRY,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "outer_function": outer_name,
                "inner_function": inner_choice,
                "value": inner_ltx,
                "triple": f"({a},{b},{c})",
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# Helpers — triangle-based trig value computation
# ---------------------------------------------------------------------------


def _triangle_trig(
    func_name: str,
    opp: int,
    adj: int,
    hyp: int,
) -> sympy.Expr | None:
    """Compute a trig function from opposite, adjacent, hypotenuse sides.

    Returns a simplified SymPy Rational (or expression with sqrt for
    sec/csc when the triple doesn't cancel nicely — but our triples are
    integer, so results are always Rational).

    Returns ``None`` if the function is undefined (division by zero).
    """
    if func_name == "sin":
        return Rational(opp, hyp)
    if func_name == "cos":
        return Rational(adj, hyp)
    if func_name == "tan":
        if adj == 0:
            return None
        return Rational(opp, adj)
    if func_name == "cot":
        if opp == 0:
            return None
        return Rational(adj, opp)
    if func_name == "sec":
        if adj == 0:
            return None
        return Rational(hyp, adj)
    if func_name == "csc":
        if opp == 0:
            return None
        return Rational(hyp, opp)
    return None  # pragma: no cover
