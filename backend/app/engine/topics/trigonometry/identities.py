"""Trigonometry identity / simplification templates.

Template:
    TrigSimplifyTemplate — Simplify a trig expression using identities.

Uses backward construction: start with a simple answer, then "disguise"
it through one or more identities to produce the question expression.
The student must simplify the disguised form back to the answer.

Variant families
----------------
EASY   (single identity, direct application):
    pyth_basic, pyth_rearranged, reciprocal, quotient

MEDIUM (one identity + one algebraic step):
    frac_simplify, double_angle_frac, half_angle_cos2,
    trig_product, sec_tan_pyth, csc_cot_pyth

HARD   (chained identities or multi-step):
    sum_diff_expansion, cos_diff_expansion,
    sec_cos_over_tan, double_angle_tan, sin_sec_product,
    compound_fraction, conjugate_product, multi_step_algebraic,
    factoring, fraction_sum, cofunction, even_odd_compound,
    double_angle_extended
"""

from __future__ import annotations

import random

import sympy
from sympy import (
    Integer,
    Symbol,
    cos,
    cot,
    csc,
    latex,
    pi,
    sec,
    simplify,
    sin,
    tan,
    trigsimp,
)

from app.engine.registry import register_template
from app.engine.types import (
    Difficulty,
    GeneratedProblem,
    GenerationError,
    Topic,
    TrustedLatex,
)

# ---------------------------------------------------------------------------
# Module-level symbol used across all variants
# ---------------------------------------------------------------------------
_theta = Symbol("theta", real=True)

# ---------------------------------------------------------------------------
# Angle pairs for hard sum/difference variants
# ---------------------------------------------------------------------------
_ANGLE_POOL = [pi / 6, pi / 4, pi / 3]

# All ordered pairs (A, B) from the pool, including A == B.
_ANGLE_PAIRS: list[tuple[sympy.Expr, sympy.Expr]] = [
    (a, b) for a in _ANGLE_POOL for b in _ANGLE_POOL
]

# ---------------------------------------------------------------------------
# Variable names for new HARD variants (adds diversity to question text)
# ---------------------------------------------------------------------------
_VARIABLE_NAMES = ["theta", "x", "alpha", "t"]


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------


@register_template
class TrigSimplifyTemplate:
    """Simplify a trig expression using identities.

    Backward construction: the answer is chosen first, then an identity
    is applied *in reverse* to build a more complex expression that the
    student must simplify.
    """

    topic = Topic.TRIGONOMETRY
    subtopic = "trig_simplify"
    supported_difficulties = [
        Difficulty.EASY,
        Difficulty.MEDIUM,
        Difficulty.HARD,
    ]

    # -- variant dispatch tables -------------------------------------------

    _EASY_VARIANTS = [
        "pyth_basic",
        "pyth_rearranged",
        "reciprocal",
        "quotient",
    ]

    _MEDIUM_VARIANTS = [
        "frac_simplify",
        "double_angle_frac",
        "half_angle_cos2",
        "trig_product",
        "sec_tan_pyth",
        "csc_cot_pyth",
    ]

    _HARD_VARIANTS = [
        # Original families
        "sum_diff_expansion",
        "cos_diff_expansion",
        "sec_cos_over_tan",
        "double_angle_tan",
        "sin_sec_product",
        # New families (150+ unique variants total)
        "compound_fraction",
        "conjugate_product",
        "multi_step_algebraic",
        "factoring",
        "fraction_sum",
        "cofunction",
        "even_odd_compound",
        "double_angle_extended",
    ]

    # -- public API --------------------------------------------------------

    # Maximum retries when a variant produces a trivial / invalid result
    _MAX_VARIANT_RETRIES = 10

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            variants = self._EASY_VARIANTS
        elif difficulty == Difficulty.MEDIUM:
            variants = self._MEDIUM_VARIANTS
        else:
            variants = self._HARD_VARIANTS

        last_err: GenerationError | None = None
        for _ in range(self._MAX_VARIANT_RETRIES):
            variant = rng.choice(variants)
            method = getattr(self, f"_gen_{variant}")
            try:
                return method(difficulty, rng)
            except GenerationError as exc:
                last_err = exc
                continue

        # All retries exhausted — re-raise the last error
        raise last_err  # type: ignore[misc]

    # =====================================================================
    # EASY variants
    # =====================================================================

    def _gen_pyth_basic(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""sin^2(\theta) + cos^2(\theta) -> 1."""
        t = _theta
        expr = sin(t) ** 2 + cos(t) ** 2
        answer = Integer(1)
        return self._build(expr, answer, difficulty, "pyth_basic")

    def _gen_pyth_rearranged(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""1 - sin^2(\theta) -> cos^2(\theta)  (or vice-versa)."""
        t = _theta
        which = rng.choice(["sin", "cos"])
        if which == "sin":
            expr = Integer(1) - sin(t) ** 2
            answer = cos(t) ** 2
        else:
            expr = Integer(1) - cos(t) ** 2
            answer = sin(t) ** 2
        return self._build(expr, answer, difficulty, "pyth_rearranged")

    def _gen_reciprocal(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""sin(\theta) csc(\theta) -> 1  (or cos*sec, tan*cot)."""
        t = _theta
        pair = rng.choice(["sin_csc", "cos_sec", "tan_cot"])
        if pair == "sin_csc":
            expr = sin(t) * csc(t)
        elif pair == "cos_sec":
            expr = cos(t) * sec(t)
        else:
            expr = tan(t) * cot(t)
        answer = Integer(1)
        return self._build(expr, answer, difficulty, "reciprocal")

    def _gen_quotient(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""sin/cos -> tan  (or cos/sin -> cot)."""
        t = _theta
        which = rng.choice(["tan", "cot"])
        if which == "tan":
            expr = sin(t) / cos(t)
            answer = tan(t)
        else:
            expr = cos(t) / sin(t)
            answer = cot(t)
        return self._build(expr, answer, difficulty, "quotient")

    # =====================================================================
    # MEDIUM variants
    # =====================================================================

    def _gen_frac_simplify(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""(1-cos^2)/sin -> sin  OR  (1-sin^2)/cos -> cos."""
        t = _theta
        target = rng.choice(["sin", "cos"])
        if target == "sin":
            expr = (Integer(1) - cos(t) ** 2) / sin(t)
            answer = sin(t)
        else:
            expr = (Integer(1) - sin(t) ** 2) / cos(t)
            answer = cos(t)
        return self._build(expr, answer, difficulty, "frac_simplify")

    def _gen_double_angle_frac(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""sin(2\theta)/(2cos(\theta)) -> sin(\theta)
        OR  sin(2\theta)/(2sin(\theta)) -> cos(\theta)."""
        t = _theta
        target = rng.choice(["sin", "cos"])
        if target == "sin":
            expr = sin(2 * t) / (2 * cos(t))
            answer = sin(t)
        else:
            expr = sin(2 * t) / (2 * sin(t))
            answer = cos(t)
        return self._build(
            expr,
            answer,
            difficulty,
            "double_angle_frac",
        )

    def _gen_half_angle_cos2(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""(cos(2\theta)+1)/2 -> cos^2(\theta)
        OR  (1-cos(2\theta))/2 -> sin^2(\theta)."""
        t = _theta
        target = rng.choice(["cos2", "sin2"])
        if target == "cos2":
            expr = (cos(2 * t) + 1) / 2
            answer = cos(t) ** 2
        else:
            expr = (Integer(1) - cos(2 * t)) / 2
            answer = sin(t) ** 2
        return self._build(
            expr,
            answer,
            difficulty,
            "half_angle_cos2",
        )

    def _gen_trig_product(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""tan(\theta) cos(\theta) -> sin(\theta)
        OR  cot(\theta) sin(\theta) -> cos(\theta)."""
        t = _theta
        which = rng.choice(["tan_cos", "cot_sin"])
        if which == "tan_cos":
            expr = tan(t) * cos(t)
            answer = sin(t)
        else:
            expr = cot(t) * sin(t)
            answer = cos(t)
        return self._build(expr, answer, difficulty, "trig_product")

    def _gen_sec_tan_pyth(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""sec^2(\theta) - tan^2(\theta) -> 1."""
        t = _theta
        expr = sec(t) ** 2 - tan(t) ** 2
        answer = Integer(1)
        return self._build(expr, answer, difficulty, "sec_tan_pyth")

    def _gen_csc_cot_pyth(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""csc^2(\theta) - cot^2(\theta) -> 1."""
        t = _theta
        expr = csc(t) ** 2 - cot(t) ** 2
        answer = Integer(1)
        return self._build(expr, answer, difficulty, "csc_cot_pyth")

    # =====================================================================
    # HARD variants
    # =====================================================================

    def _gen_sum_diff_expansion(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""sin(A+B) or sin(A-B) expansion with specific angles.

        Present the expanded form; answer is the exact numerical value.
        """
        _TRIVIAL = {Integer(0), Integer(1), Integer(-1)}

        for _ in range(20):
            a_angle, b_angle = rng.choice(_ANGLE_PAIRS)
            sign = rng.choice(["plus", "minus"])

            if sign == "plus":
                # sin(A)cos(B) + cos(A)sin(B) = sin(A+B)
                expr = sin(a_angle) * cos(b_angle) + cos(a_angle) * sin(b_angle)
                result_angle = a_angle + b_angle
            else:
                # sin(A)cos(B) - cos(A)sin(B) = sin(A-B)
                expr = sin(a_angle) * cos(b_angle) - cos(a_angle) * sin(b_angle)
                result_angle = a_angle - b_angle

            answer = simplify(sin(result_angle))
            if answer in _TRIVIAL:
                continue  # reject trivial answer for HARD

            return self._build(
                expr,
                answer,
                difficulty,
                "sum_diff_expansion",
                metadata_extra={
                    "angle_a": latex(a_angle),
                    "angle_b": latex(b_angle),
                    "operation": sign,
                },
            )

        raise GenerationError(
            "sum_diff_expansion: all sampled angle pairs produced trivial answers"
        )

    def _gen_cos_diff_expansion(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""cos(A-B) or cos(A+B) expansion with specific angles.

        cos(A)cos(B) + sin(A)sin(B) = cos(A-B)
        cos(A)cos(B) - sin(A)sin(B) = cos(A+B)
        """
        _TRIVIAL = {Integer(0), Integer(1), Integer(-1)}

        for _ in range(20):
            a_angle, b_angle = rng.choice(_ANGLE_PAIRS)
            sign = rng.choice(["plus", "minus"])

            if sign == "plus":
                # cos(A)cos(B) + sin(A)sin(B) = cos(A-B)
                expr = cos(a_angle) * cos(b_angle) + sin(a_angle) * sin(b_angle)
                result_angle = a_angle - b_angle
            else:
                # cos(A)cos(B) - sin(A)sin(B) = cos(A+B)
                expr = cos(a_angle) * cos(b_angle) - sin(a_angle) * sin(b_angle)
                result_angle = a_angle + b_angle

            answer = simplify(cos(result_angle))
            if answer in _TRIVIAL:
                continue  # reject trivial answer for HARD

            return self._build(
                expr,
                answer,
                difficulty,
                "cos_diff_expansion",
                metadata_extra={
                    "angle_a": latex(a_angle),
                    "angle_b": latex(b_angle),
                    "operation": sign,
                },
            )

        raise GenerationError(
            "cos_diff_expansion: all sampled angle pairs produced trivial answers"
        )

    def _gen_sec_cos_over_tan(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""(sec(\theta) - cos(\theta)) / tan(\theta) -> sin(\theta).

        Rewrite sec = 1/cos, common denom, use Pythagorean identity.
        """
        t = _theta
        expr = (sec(t) - cos(t)) / tan(t)
        answer = sin(t)
        return self._build(
            expr,
            answer,
            difficulty,
            "sec_cos_over_tan",
        )

    def _gen_double_angle_tan(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""(1 - cos(2\theta)) / sin(2\theta) -> tan(\theta).

        Use double-angle formulas:
        1 - cos(2t) = 2sin^2(t),  sin(2t) = 2sin(t)cos(t)
        => 2sin^2(t) / (2sin(t)cos(t)) = sin(t)/cos(t) = tan(t).
        """
        t = _theta
        expr = (Integer(1) - cos(2 * t)) / sin(2 * t)
        answer = tan(t)
        return self._build(
            expr,
            answer,
            difficulty,
            "double_angle_tan",
        )

    def _gen_sin_sec_product(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""sin(\theta) sec(\theta) -> tan(\theta)
        OR  cos(\theta) csc(\theta) -> cot(\theta)."""
        t = _theta
        which = rng.choice(["sin_sec", "cos_csc"])
        if which == "sin_sec":
            expr = sin(t) * sec(t)
            answer = tan(t)
        else:
            expr = cos(t) * csc(t)
            answer = cot(t)
        return self._build(
            expr,
            answer,
            difficulty,
            "sin_sec_product",
        )

    # =====================================================================
    # HARD variants — new families (compound, conjugate, etc.)
    # =====================================================================

    @staticmethod
    def _make_symbol(rng: random.Random) -> Symbol:
        """Pick a random variable name for expression variety."""
        name = rng.choice(_VARIABLE_NAMES)
        return Symbol(name, real=True)

    def _gen_compound_fraction(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""Compound fraction identities, e.g.
        (1 + tan^2(nt)) / (1 + cot^2(nt)) -> tan^2(nt).

        5 base patterns x 3 multipliers = 15 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([1, 2, 3])
        nt = n * t if n > 1 else t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (
                (1 + tan(nt) ** 2) / (1 + cot(nt) ** 2),
                tan(nt) ** 2,
            ),
            (
                (sec(nt) ** 2 - 1) / sec(nt) ** 2,
                sin(nt) ** 2,
            ),
            (
                (csc(nt) ** 2 - 1) / csc(nt) ** 2,
                cos(nt) ** 2,
            ),
            (
                tan(nt) ** 2 / (1 + tan(nt) ** 2),
                sin(nt) ** 2,
            ),
            (
                Integer(1) / (1 + tan(nt) ** 2),
                cos(nt) ** 2,
            ),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "compound_fraction",
        )

    def _gen_conjugate_product(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""Conjugate-pair products, e.g.
        (1 - sin(nt))(1 + sin(nt)) -> cos^2(nt).

        6 base patterns x 3 multipliers = 18 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([1, 2, 3])
        nt = n * t if n > 1 else t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (
                (1 - sin(nt)) * (1 + sin(nt)),
                cos(nt) ** 2,
            ),
            (
                (1 - cos(nt)) * (1 + cos(nt)),
                sin(nt) ** 2,
            ),
            (
                (sec(nt) - 1) * (sec(nt) + 1),
                tan(nt) ** 2,
            ),
            (
                (csc(nt) - 1) * (csc(nt) + 1),
                cot(nt) ** 2,
            ),
            (
                (sec(nt) - tan(nt)) * (sec(nt) + tan(nt)),
                Integer(1),
            ),
            (
                (csc(nt) - cot(nt)) * (csc(nt) + cot(nt)),
                Integer(1),
            ),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "conjugate_product",
        )

    def _gen_multi_step_algebraic(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""Multi-step algebraic trig identities, e.g.
        (sin(nt) + cos(nt))^2 - 1 -> sin(2nt).

        6 base patterns x 3 multipliers = 18 variants
        (pattern 4 restricted to n=1).
        """
        t = self._make_symbol(rng)
        n = rng.choice([1, 2, 3])
        nt = n * t if n > 1 else t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (
                (sin(nt) + cos(nt)) ** 2 - 1,
                sin(2 * n * t),
            ),
            (
                (sin(nt) - cos(nt)) ** 2 - 1,
                -sin(2 * n * t),
            ),
            (
                Integer(1) - (sin(nt) - cos(nt)) ** 2,
                sin(2 * n * t),
            ),
            (
                cos(nt) - cos(nt) * sin(nt) ** 2,
                cos(nt) ** 3,
            ),
            (
                sin(nt) - sin(nt) * cos(nt) ** 2,
                sin(nt) ** 3,
            ),
        ]

        # sin*tan+cos = sec only works reliably with n=1
        if n == 1:
            patterns.append(
                (
                    sin(t) * tan(t) + cos(t),
                    sec(t),
                )
            )

        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "multi_step_algebraic",
        )

    def _gen_factoring(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""Factoring-based identities, e.g.
        sin^4(nt) - cos^4(nt) -> -cos(2nt).

        5 base patterns x 3 multipliers = 15 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([1, 2, 3])
        nt = n * t if n > 1 else t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (
                sin(nt) ** 4 - cos(nt) ** 4,
                -cos(2 * n * t),
            ),
            (
                sec(nt) ** 4 - tan(nt) ** 4,
                1 + 2 * tan(nt) ** 2,
            ),
            (
                csc(nt) ** 4 - cot(nt) ** 4,
                1 + 2 * cot(nt) ** 2,
            ),
            (
                tan(nt) ** 4 + 2 * tan(nt) ** 2 + 1,
                sec(nt) ** 4,
            ),
            (
                cot(nt) ** 4 + 2 * cot(nt) ** 2 + 1,
                csc(nt) ** 4,
            ),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "factoring",
        )

    def _gen_fraction_sum(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""Sum-of-fractions identities, e.g.
        1/(1-sin(nt)) + 1/(1+sin(nt)) -> 2sec^2(nt).

        8 base patterns x 3 multipliers = 24 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([1, 2, 3])
        nt = n * t if n > 1 else t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (
                Integer(1) / (1 - sin(nt)) + Integer(1) / (1 + sin(nt)),
                2 * sec(nt) ** 2,
            ),
            (
                Integer(1) / (1 - cos(nt)) + Integer(1) / (1 + cos(nt)),
                2 * csc(nt) ** 2,
            ),
            (
                sin(nt) ** 2 / (1 - cos(nt)),
                1 + cos(nt),
            ),
            (
                sin(nt) ** 2 / (1 + cos(nt)),
                1 - cos(nt),
            ),
            (
                cos(nt) ** 2 / (1 - sin(nt)),
                1 + sin(nt),
            ),
            (
                cos(nt) ** 2 / (1 + sin(nt)),
                1 - sin(nt),
            ),
            (
                cos(nt) / (1 - sin(nt)),
                sec(nt) + tan(nt),
            ),
            (
                sin(nt) / (1 - cos(nt)),
                csc(nt) + cot(nt),
            ),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "fraction_sum",
        )

    def _gen_cofunction(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        r"""Cofunction identities with compound arguments, e.g.
        sin(pi/2 - 2t) -> cos(2t).

        6 base patterns x 2 multipliers (n=2,3) = 12 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([2, 3])  # n=1 is too easy for HARD
        nt = n * t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (sin(pi / 2 - nt), cos(nt)),
            (cos(pi / 2 - nt), sin(nt)),
            (tan(pi / 2 - nt), cot(nt)),
            (cot(pi / 2 - nt), tan(nt)),
            (sec(pi / 2 - nt), csc(nt)),
            (csc(pi / 2 - nt), sec(nt)),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "cofunction",
        )

    def _gen_even_odd_compound(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""Even/odd property combinations, e.g.
        sin(-nt) sec(-nt) -> -tan(nt).

        4 base patterns x 2 multipliers (n=2,3) = 8 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([2, 3])  # avoid n=1 to prevent MEDIUM overlap
        nt = n * t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (sin(-nt) * sec(-nt), -tan(nt)),
            (cos(-nt) * csc(-nt), -cot(nt)),
            (sin(-nt) * sec(nt), -tan(nt)),
            (cos(-nt) * csc(nt), cot(nt)),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "even_odd_compound",
        )

    def _gen_double_angle_extended(
        self, difficulty: Difficulty, rng: random.Random
    ) -> GeneratedProblem:
        r"""Extended double-angle identities with higher multipliers,
        e.g. 2cos^2(2t) - 1 -> cos(4t).

        8 base patterns x 2 multipliers (n=2,3) = 16 variants.
        """
        t = self._make_symbol(rng)
        n = rng.choice([2, 3])  # n=1 already covered by MEDIUM
        nt = n * t

        patterns: list[tuple[sympy.Expr, sympy.Expr]] = [
            (
                2 * cos(nt) ** 2 - 1,
                cos(2 * n * t),
            ),
            (
                1 - 2 * sin(nt) ** 2,
                cos(2 * n * t),
            ),
            (
                2 * sin(nt) * cos(nt),
                sin(2 * n * t),
            ),
            (
                (Integer(1) - cos(2 * n * t)) / sin(2 * n * t),
                tan(nt),
            ),
            (
                sin(2 * n * t) / (1 + cos(2 * n * t)),
                tan(nt),
            ),
            (
                (Integer(1) - cos(2 * n * t)) / 2,
                sin(nt) ** 2,
            ),
            (
                (1 + cos(2 * n * t)) / 2,
                cos(nt) ** 2,
            ),
            (
                sin(2 * n * t) / (Integer(1) - cos(2 * n * t)),
                cot(nt),
            ),
        ]
        expr, answer = rng.choice(patterns)
        return self._build(
            expr,
            answer,
            difficulty,
            "double_angle_extended",
        )

    # =====================================================================
    # Shared builder
    # =====================================================================

    def _build(
        self,
        expr: sympy.Expr,
        answer: sympy.Expr,
        difficulty: Difficulty,
        variant: str,
        *,
        metadata_extra: dict | None = None,
    ) -> GeneratedProblem:
        """Render *expr* and *answer* into a ``GeneratedProblem``.

        Also runs a SymPy sanity check: ``trigsimp(expr - answer) == 0``.
        """
        # Sanity check: the expression must simplify to the answer.
        diff = trigsimp(expr - answer)
        # Some expressions need extra help from simplify
        if diff != 0:
            diff = simplify(diff)
        if diff != 0:
            raise GenerationError(
                f"Identity check failed for variant={variant}: "
                f"trigsimp({latex(expr)} - {latex(answer)}) = {diff}"
            )

        expr_ltx = latex(expr)
        answer_ltx = latex(answer)

        question = f"Simplify ${expr_ltx}$."

        metadata: dict = {"variant": variant, "expression": expr_ltx}
        if metadata_extra:
            metadata.update(metadata_extra)

        steps = [
            TrustedLatex(f"${expr_ltx}$"),
            TrustedLatex(f"${answer_ltx}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${answer_ltx}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata=metadata,
            solution_steps=tuple(steps),
        )
