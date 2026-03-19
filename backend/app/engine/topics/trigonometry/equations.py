"""Parameterized trig equation templates using backward construction.

Templates:
  TrigEquationBasicTemplate — Solve f(kx + c) = value on [0, 2pi)
  TrigQuadraticTemplate     — Solve af²(x) + bf(x) + c = 0 on [0, 2pi)

Both templates generate massive variety via parameterized backward
construction, replacing the old hardcoded TrigEquationTemplate.
"""

from __future__ import annotations

import random
from math import gcd

import sympy
from sympy import Integer, Rational, latex, simplify

from app.engine.registry import register_template
from app.engine.topics.trigonometry._helpers import (
    STANDARD_VALUES,
    TRIG_FUNCTIONS,
    format_solution_set,
    get_standard_func_values,
    pick_angle_multiplier,
    pick_phase_shift,
    pick_trig_func,
    solve_trig_basic,
)
from app.engine.types import (
    ALL_DIFFICULTIES,
    Difficulty,
    GeneratedProblem,
    GenerationError,
    Topic,
    TrustedLatex,
)

_MAX_RETRIES = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_inner_arg(k: int, phase: sympy.Expr) -> str:
    """Format kx + phase as LaTeX for the equation display.

    Examples: x, 2x, 2x - pi/3, x + pi/4
    """
    if k == 1:
        kx = "x"
    else:
        kx = f"{k}x"

    if phase == 0:
        return kx

    # Determine sign and absolute value of phase
    phase_float = float(phase.evalf())
    if phase_float > 0:
        return kx + " + " + latex(phase)
    else:
        return kx + " - " + latex(-phase)


def _trig_power_latex(latex_cmd: str, arg: str, power: int = 1) -> str:
    r"""Format a trig function with optional power as LaTeX.

    e.g. \sin^{2}(x) or \cos(x)
    """
    if power == 1:
        return rf"{latex_cmd}\left({arg}\right)"
    return rf"{latex_cmd}^{{{power}}}\left({arg}\right)"


def _is_rational(expr: sympy.Expr) -> bool:
    """Check whether a simplified SymPy expression is rational."""
    expr = simplify(expr)
    return expr.is_rational is True


def _clear_fractions_and_reduce(
    a: sympy.Expr,
    b: sympy.Expr,
    c: sympy.Expr,
) -> tuple[int, int, int]:
    """Convert rational coefficients a, b, c to smallest integer triple.

    All three must be rational (use _is_rational to verify beforehand).
    Multiplies through to clear all denominators, then divides by GCD.
    Returns (A, B, C) as Python ints.
    """
    a_r = Rational(simplify(a))
    b_r = Rational(simplify(b))
    c_r = Rational(simplify(c))

    # LCM of all denominators
    denoms = [abs(int(a_r.q)), abs(int(b_r.q)), abs(int(c_r.q))]
    lcm_val = denoms[0]
    for d in denoms[1:]:
        lcm_val = lcm_val * d // gcd(lcm_val, d)

    ai = int(a_r * lcm_val)
    bi = int(b_r * lcm_val)
    ci = int(c_r * lcm_val)

    # Divide by GCD of all three
    g = gcd(gcd(abs(ai), abs(bi)), abs(ci))
    if g > 1:
        ai //= g
        bi //= g
        ci //= g

    # Ensure leading coefficient is positive
    if ai < 0:
        ai, bi, ci = -ai, -bi, -ci

    return ai, bi, ci


def _build_quadratic_latex(
    a: int,
    b: int,
    c: int,
    latex_cmd: str,
    arg: str,
) -> str:
    r"""Build LaTeX for a*f^2(x) + b*f(x) + c = 0.

    Handles coefficient display: suppresses 1, handles negatives, etc.
    """
    parts: list[str] = []

    # a * f^2(x)
    f2 = _trig_power_latex(latex_cmd, arg, 2)
    if a == 1:
        parts.append(f2)
    elif a == -1:
        parts.append(f"-{f2}")
    else:
        parts.append(f"{a}{f2}")

    # b * f(x)
    f1 = _trig_power_latex(latex_cmd, arg, 1)
    if b != 0:
        if b == 1:
            parts.append(f"+ {f1}")
        elif b == -1:
            parts.append(f"- {f1}")
        elif b > 0:
            parts.append(f"+ {b}{f1}")
        else:
            parts.append(f"- {abs(b)}{f1}")

    # c (constant)
    if c != 0:
        if c > 0:
            parts.append(f"+ {c}")
        else:
            parts.append(f"- {abs(c)}")

    return " ".join(parts) + " = 0"


# ---------------------------------------------------------------------------
# Template 1: TrigEquationBasicTemplate — Solve f(kx + c) = value
# ---------------------------------------------------------------------------


@register_template
class TrigEquationBasicTemplate:
    """Solve f(kx + c) = value on [0, 2pi).

    Backward construction: pick function, multiplier, phase, target angle,
    compute value, then find all solutions.
    """

    topic = Topic.TRIGONOMETRY
    subtopic = "trig_equation"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(
        self,
        difficulty: Difficulty,
        rng: random.Random,
    ) -> GeneratedProblem:
        for _ in range(_MAX_RETRIES):
            result = self._try_generate(difficulty, rng)
            if result is not None:
                return result
        raise GenerationError("TrigEquationBasicTemplate: parameter sampling exhausted")

    def _try_generate(
        self,
        difficulty: Difficulty,
        rng: random.Random,
    ) -> GeneratedProblem | None:
        # 1. Pick function
        func_name, _func, latex_cmd = pick_trig_func(difficulty, rng)

        # 2. Pick multiplier and phase shift
        k = pick_angle_multiplier(difficulty, rng)
        phase = pick_phase_shift(difficulty, rng)

        # For easy: force k=1, phase=0, basic funcs
        if difficulty == Difficulty.EASY:
            k = 1
            phase = Integer(0)

        # 3. Pick a target angle where the function is defined
        candidate_angles = [
            angle for (fname, angle), _val in STANDARD_VALUES.items() if fname == func_name
        ]
        if not candidate_angles:
            return None

        theta0 = rng.choice(candidate_angles)

        # 4. Compute value = f(theta0)
        value = STANDARD_VALUES[(func_name, theta0)]

        # 5. Find all solutions
        solutions = solve_trig_basic(func_name, value, k, phase)

        # Must have at least one solution
        if not solutions:
            return None

        # 6. Build the question
        inner_arg = _format_inner_arg(k, phase)
        value_latex = latex(value)

        question = (
            f"Solve ${latex_cmd}\\left({inner_arg}\\right) = {value_latex}$ on $[0, 2\\pi)$."
        )

        answer = format_solution_set(solutions)

        eq_ltx = f"{latex_cmd}\\left({inner_arg}\\right) = {value_latex}"
        sol_ltx = answer
        steps = [
            TrustedLatex(f"${eq_ltx}$"),
            TrustedLatex(f"${sol_ltx}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "function": func_name,
                "multiplier": k,
                "phase": str(phase),
                "value": str(value),
                "num_solutions": len(solutions),
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# Template 2: TrigQuadraticTemplate — af²(x) + bf(x) + c = 0
# ---------------------------------------------------------------------------


@register_template
class TrigQuadraticTemplate:
    """Solve a quadratic trig equation on [0, 2pi).

    Backward construction: pick a trig function and two roots from its
    standard values, build the quadratic (f - r1)(f - r2) = 0, expand
    with integer coefficients, and collect all solutions.
    """

    topic = Topic.TRIGONOMETRY
    subtopic = "trig_quadratic"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(
        self,
        difficulty: Difficulty,
        rng: random.Random,
    ) -> GeneratedProblem:
        for _ in range(_MAX_RETRIES):
            result = self._try_generate(difficulty, rng)
            if result is not None:
                return result
        raise GenerationError("TrigQuadraticTemplate: parameter sampling exhausted")

    def _try_generate(
        self,
        difficulty: Difficulty,
        rng: random.Random,
    ) -> GeneratedProblem | None:
        # 1. Pick base function
        func_name = self._pick_func(difficulty, rng)
        _func, latex_cmd = TRIG_FUNCTIONS[func_name]

        # 2. Get all achievable standard values for this function
        all_values = get_standard_func_values(func_name)
        if len(all_values) < 2:
            return None

        # 3. Pick roots based on difficulty
        r1, r2, has_extraneous = self._pick_roots(
            difficulty,
            rng,
            func_name,
            all_values,
        )
        if r1 is None:
            return None

        # 4. Build quadratic coefficients: (f - r1)(f - r2) = f² - (r1+r2)f + r1*r2
        sum_roots = simplify(r1 + r2)
        prod_roots = simplify(r1 * r2)

        a_coeff = Integer(1)
        b_coeff = simplify(-sum_roots)
        c_coeff = prod_roots

        # Coefficients must all be rational for integer presentation
        if not all(_is_rational(v) for v in (a_coeff, b_coeff, c_coeff)):
            return None

        # 5. Clear fractions and reduce to smallest integers
        try:
            a_int, b_int, c_int = _clear_fractions_and_reduce(
                a_coeff,
                b_coeff,
                c_coeff,
            )
        except (ValueError, TypeError, ZeroDivisionError):
            return None

        # Skip trivial cases (a=0 means not quadratic)
        if a_int == 0:
            return None

        # 6. Collect solutions
        solutions: list[sympy.Expr] = []

        # Solutions for f(x) = r1 (always valid for the chosen function)
        sols_r1 = solve_trig_basic(func_name, r1)
        solutions.extend(sols_r1)

        # Solutions for f(x) = r2
        if not has_extraneous:
            sols_r2 = solve_trig_basic(func_name, r2)
            for s in sols_r2:
                if not any(simplify(s - existing) == 0 for existing in solutions):
                    solutions.append(s)

        if not solutions:
            return None

        solutions.sort(key=lambda s: float(s.evalf()))

        # 7. Build LaTeX
        eq_latex = _build_quadratic_latex(
            a_int,
            b_int,
            c_int,
            latex_cmd,
            "x",
        )
        question = f"Solve ${eq_latex}$ on $[0, 2\\pi)$."

        answer = format_solution_set(solutions)

        sol_ltx = answer
        steps = [
            TrustedLatex(f"${eq_latex}$"),
            TrustedLatex(f"${sol_ltx}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "function": func_name,
                "roots": [str(r1), str(r2)],
                "has_extraneous": has_extraneous,
                "num_solutions": len(solutions),
            },
            solution_steps=tuple(steps),
        )

    @staticmethod
    def _pick_func(difficulty: Difficulty, rng: random.Random) -> str:
        """Pick the base trig function for the quadratic."""
        if difficulty == Difficulty.EASY:
            return rng.choice(["sin", "cos"])
        if difficulty == Difficulty.MEDIUM:
            return rng.choice(["sin", "cos"])
        # Hard: allow tan
        return rng.choice(["sin", "cos", "tan"])

    @staticmethod
    def _pick_roots(
        difficulty: Difficulty,
        rng: random.Random,
        func_name: str,
        all_values: list[sympy.Expr],
    ) -> tuple[sympy.Expr | None, sympy.Expr | None, bool]:
        """Pick two roots for the quadratic based on difficulty.

        Returns (r1, r2, has_extraneous).
        has_extraneous is True when r2 is outside the function's range
        (only for hard difficulty with sin/cos).

        Roots are chosen so that the expanded quadratic has rational
        (hence integer-presentable) coefficients.  This means we either
        pick two rational roots, or a conjugate pair ±v whose sum is 0
        and product is rational.
        """
        is_bounded = func_name in ("sin", "cos")

        # Split values into rational and irrational
        rational_vals = [v for v in all_values if v.is_rational]
        # Conjugate pairs: values v where -v is also in the list,
        # and v*(-v) = -v² is rational.  For standard trig values this
        # covers ±sqrt(2)/2 and ±sqrt(3)/2.
        conjugate_pairs: list[tuple[sympy.Expr, sympy.Expr]] = []
        seen: set[int] = set()
        for i, v in enumerate(all_values):
            if i in seen or v.is_rational:
                continue
            for j, w in enumerate(all_values):
                if j <= i or j in seen:
                    continue
                if simplify(v + w) == 0 and _is_rational(v * w):
                    conjugate_pairs.append((v, w))
                    seen.add(i)
                    seen.add(j)
                    break

        def _pick_rational_pair() -> tuple[sympy.Expr | None, sympy.Expr | None]:
            """Pick two roots that give rational coefficients."""
            # Strategy 1: two rational roots
            # Strategy 2: a conjugate pair
            options: list[str] = []
            if len(rational_vals) >= 2:
                options.append("rational")
            if conjugate_pairs:
                options.append("conjugate")
            if not options:
                return None, None
            choice = rng.choice(options)
            if choice == "rational":
                chosen = rng.sample(rational_vals, 2)
                return chosen[0], chosen[1]
            pair = rng.choice(conjugate_pairs)
            return pair[0], pair[1]

        if difficulty == Difficulty.EASY:
            # One root is 0 (for easy factoring: f(x) * (af(x) + b) = 0)
            zero = Integer(0)
            # Other root must be rational for clean coefficients
            other_rational = [v for v in rational_vals if simplify(v) != 0]
            if not other_rational:
                return None, None, False
            r2 = rng.choice(other_rational)
            return zero, r2, False

        if difficulty == Difficulty.MEDIUM:
            r1, r2 = _pick_rational_pair()
            if r1 is None:
                return None, None, False
            return r1, r2, False

        # Hard difficulty
        if is_bounded:
            use_extraneous = rng.random() < 0.5

            if use_extraneous:
                # Pick one valid rational root, one extraneous root
                if not rational_vals:
                    return None, None, False
                r1 = rng.choice(rational_vals)
                extraneous_choices = [
                    Integer(-2),
                    Integer(2),
                    Integer(3),
                    Rational(-3, 2),
                    Rational(3, 2),
                ]
                r2 = rng.choice(extraneous_choices)
                return r1, r2, True

            # Two valid roots with rational coefficients
            r1, r2 = _pick_rational_pair()
            if r1 is None:
                return None, None, False
            return r1, r2, False

        # tan: all real values are valid, pick rational pair
        r1, r2 = _pick_rational_pair()
        if r1 is None:
            return None, None, False
        return r1, r2, False
