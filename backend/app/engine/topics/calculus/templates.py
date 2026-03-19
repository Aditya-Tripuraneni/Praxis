"""Calculus topic templates for the ProblemGenerator math engine.

Templates: LimitTemplate, DerivativeBasicTemplate,
           ChainRuleTemplate, BasicIntegralTemplate
"""

from __future__ import annotations

import random

from sympy import (
    Add,
    Derivative,
    Integral,
    Mul,
    Pow,
    Rational,
    Symbol,
    asin,
    atan,
    cancel,
    cos,
    diff,
    exp,
    factor,
    integrate,
    latex,
    limit,
    log,
    sec,
    simplify,
    sin,
    sqrt,
    tan,
)

from app.engine.registry import register_template
from app.engine.types import Difficulty, GeneratedProblem, GenerationError, Topic, TrustedLatex

x = Symbol("x")


# ---------------------------------------------------------------------------
# 1. LimitTemplate
# ---------------------------------------------------------------------------
@register_template
class LimitTemplate:
    topic = Topic.CALCULUS
    subtopic = "limits"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Compute lim(x->a) f(x)."""
        if difficulty == Difficulty.EASY:
            # Direct substitution with a polynomial
            a = rng.randint(1, 5)
            coeffs = [rng.randint(1, 5) for _ in range(rng.randint(2, 3))]
            f_expr = sum(c * x**i for i, c in enumerate(coeffs))
            approach = a
        elif difficulty == Difficulty.MEDIUM:
            # 0/0 form that factors: (x^2 - a^2)/(x - a) => x + a
            a = rng.randint(1, 5)
            b = rng.randint(1, 3)
            # f(x) = (b*x^2 - b*a^2)/(x - a) = b*(x+a) for x != a
            f_expr = (b * x**2 - b * a**2) / (x - a)
            approach = a
        else:
            # Rationalization: (sqrt(x+c) - sqrt(c)) / x  as x -> 0
            c = rng.choice([1, 4, 9, 16, 25])  # perfect squares for nicer answers
            f_expr = (sqrt(x + c) - sqrt(c)) / x
            approach = 0

        answer_val = limit(f_expr, x, approach)
        approach_latex = latex(approach)

        # -- Build solution steps --
        lim_pre = f"\\displaystyle\\lim_{{x \\to {approach_latex}}}"
        if difficulty == Difficulty.EASY:
            steps: list[TrustedLatex] = [
                TrustedLatex(f"${lim_pre} {latex(f_expr)}$"),
            ]
            substituted = f_expr.subs(x, approach)
            steps.append(TrustedLatex(f"$= {latex(substituted)}$"))
            if substituted != answer_val:
                steps.append(TrustedLatex(f"$= {latex(answer_val)}$"))
        elif difficulty == Difficulty.MEDIUM:
            numer = b * x**2 - b * a**2
            factored_numer = factor(numer)
            # Unevaluated fraction to show factoring step
            factored_frac = Mul(
                factored_numer,
                Pow(x - a, -1),
                evaluate=False,
            )
            cancelled = cancel(f_expr)
            steps = [
                TrustedLatex(f"${lim_pre} {latex(f_expr)}$"),
                TrustedLatex(f"$= {lim_pre} {latex(factored_frac)}$"),
                TrustedLatex(f"$= {lim_pre} {latex(cancelled)}$"),
                TrustedLatex(f"$= {latex(answer_val)}$"),
            ]
        else:
            conjugate = sqrt(x + c) + sqrt(c)
            rationalized = 1 / conjugate
            steps = [
                TrustedLatex(f"${lim_pre} {latex(f_expr)}$"),
            ]
            numer_tex = f"(\\sqrt{{x+{c}}}-\\sqrt{{{c}}})(\\sqrt{{x+{c}}}+\\sqrt{{{c}}})"
            denom_tex = f"x(\\sqrt{{x+{c}}}+\\sqrt{{{c}}})"
            steps.append(TrustedLatex(f"$= {lim_pre} \\frac{{{numer_tex}}}{{{denom_tex}}}$"))
            steps.append(TrustedLatex(f"$= {lim_pre} {latex(rationalized)}$"))
            steps.append(TrustedLatex(f"$= {latex(answer_val)}$"))

        question = f"Evaluate $\\displaystyle\\lim_{{x \\to {approach_latex}}} {latex(f_expr)}$."
        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${latex(answer_val)}$"),
            topic=Topic.CALCULUS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "function": latex(f_expr),
                "approach": approach_latex,
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 2. DerivativeBasicTemplate
# ---------------------------------------------------------------------------
@register_template
class DerivativeBasicTemplate:
    topic = Topic.CALCULUS
    subtopic = "derivative_basic"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Find f'(x) using the power rule.  Backward: pick derivative, integrate to get f."""
        if difficulty == Difficulty.EASY:
            # Monomial: f(x) = a*x^n, n in {2,3,4,5}
            a = rng.randint(1, 5)
            n = rng.randint(2, 5)
            f_expr = a * x**n
        elif difficulty == Difficulty.MEDIUM:
            # Polynomial degree 3-4
            degree = rng.randint(3, 4)
            terms = []
            for i in range(degree, -1, -1):
                c = rng.randint(-10, 10)
                if i == degree and c == 0:
                    c = rng.randint(1, 5)
                if c != 0:
                    terms.append(c * x**i)
            f_expr = sum(terms) if terms else x
        else:
            # Negative or fractional exponents
            variant = rng.choice(["negative", "fractional"])
            if variant == "negative":
                # f(x) = a*x^(-n) + b*x^(-m)
                a_c = rng.randint(1, 5)
                b_c = rng.randint(1, 5)
                n = rng.randint(1, 3)
                m = rng.randint(1, 3)
                for _ in range(50):
                    if m != n:
                        break
                    m = rng.randint(1, 3)
                else:
                    raise GenerationError("Parameter sampling exhausted")
                f_expr = a_c * x ** (-n) + b_c * x ** (-m)
            else:
                # f(x) = a*x^(p/q)
                a_c = rng.randint(1, 5)
                p = rng.choice([1, 3, 5])
                q = rng.choice([2, 3])
                f_expr = a_c * x ** Rational(p, q)

        deriv = diff(f_expr, x)

        # -- Build solution steps --
        ordered = f_expr.as_ordered_terms()
        if len(ordered) > 1:
            unevaluated = Add(
                *[Derivative(t, x) for t in ordered],
                evaluate=False,
            )
            steps: list[TrustedLatex] = [
                TrustedLatex(f"$f(x) = {latex(f_expr)}$"),
                TrustedLatex(f"$f'(x) = {latex(unevaluated)}$"),
                TrustedLatex(f"$f'(x) = {latex(deriv)}$"),
            ]
        else:
            steps = [
                TrustedLatex(f"$f(x) = {latex(f_expr)}$"),
                TrustedLatex(f"$f'(x) = {latex(deriv)}$"),
            ]

        question = f"Find the derivative of $f(x) = {latex(f_expr)}$."
        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"$f'(x) = {latex(deriv)}$"),
            topic=Topic.CALCULUS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "f": latex(f_expr),
                "derivative": latex(deriv),
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 3. ChainRuleTemplate — 38 variants across 3 difficulty levels
# ---------------------------------------------------------------------------
@register_template
class ChainRuleTemplate:
    """Differentiate composite functions using the chain rule.

    Uses a variant pool pattern: each difficulty has a list of variant names,
    each mapping to a ``_build_{name}`` method that returns ``(f_expr, inner)``.
    The generic chain rule computation (u-substitution for solution steps)
    works identically for every composition.
    """

    topic = Topic.CALCULUS
    subtopic = "chain_rule"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    # -- variant pools per difficulty ----------------------------------------

    _EASY_VARIANTS = [
        "power_linear",
        "sqrt_linear",
        "recip_linear",
        "neg_power_linear",
        "frac_power_linear",
        "cbrt_linear",
        "exp_simple",
        "sin_simple",
        "cos_simple",
        "ln_linear",
    ]

    _MEDIUM_VARIANTS = [
        "sin_linear",
        "cos_linear",
        "tan_linear",
        "sec_linear",
        "exp_linear",
        "exp_neg",
        "ln_quad",
        "sqrt_quad",
        "power_quad",
        "sin_quad_pure",
        "cos_quad_pure",
        "exp_quad_pure",
        "arctan_linear",
        "arcsin_linear",
        "recip_quad",
    ]

    _HARD_VARIANTS = [
        "sin_quad_shift",
        "exp_quad_shift",
        "frac_power_quad",
        "power_sin",
        "power_cos",
        "power_tan",
        "sqrt_sin",
        "exp_sin",
        "ln_cos",
        "sin_exp",
        "exp_sqrt",
        "sin_ln",
        "cos_cubic",
    ]

    _MAX_VARIANT_RETRIES = 10

    # -- public API ----------------------------------------------------------

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            variants = self._EASY_VARIANTS
        elif difficulty == Difficulty.MEDIUM:
            variants = self._MEDIUM_VARIANTS
        else:
            variants = self._HARD_VARIANTS

        last_err: Exception | None = None
        for _ in range(self._MAX_VARIANT_RETRIES):
            variant = rng.choice(variants)
            builder = getattr(self, f"_build_{variant}")
            try:
                f_expr, inner = builder(rng)
                return self._finish(f_expr, inner, variant, difficulty)
            except Exception as exc:
                last_err = exc
                continue

        raise GenerationError(
            f"ChainRule: all retries failed for {difficulty.value}"
        ) from last_err

    # -- generic chain rule computation --------------------------------------

    def _finish(
        self,
        f_expr,
        inner,
        variant: str,
        difficulty: Difficulty,
    ) -> GeneratedProblem:
        deriv = diff(f_expr, x)

        # Build solution steps via u-substitution
        u = Symbol("u")
        f_of_u = f_expr.subs(inner, u)
        outer_diff = simplify(diff(f_of_u, u)).subs(u, inner)
        chain_step = outer_diff * Derivative(inner, x)

        steps: list[TrustedLatex] = [
            TrustedLatex(f"$f(x) = {latex(f_expr)}$"),
            TrustedLatex(f"$f'(x) = {latex(chain_step)}$"),
            TrustedLatex(f"$f'(x) = {latex(deriv)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the derivative of $f(x) = {latex(f_expr)}$."),
            answer_latex=TrustedLatex(f"$f'(x) = {latex(deriv)}$"),
            topic=Topic.CALCULUS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "variant": variant,
                "f": latex(f_expr),
                "derivative": latex(deriv),
            },
            solution_steps=tuple(steps),
        )

    # ========================================================================
    # EASY builders — linear inner, simple outer
    # ========================================================================

    def _build_power_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        n = rng.randint(2, 6)
        inner = a_c * x + b_c
        return inner**n, inner

    def _build_sqrt_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        inner = a_c * x + b_c
        return sqrt(inner), inner

    def _build_recip_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        inner = a_c * x + b_c
        return 1 / inner, inner

    def _build_neg_power_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        n = rng.randint(2, 4)
        inner = a_c * x + b_c
        return inner ** (-n), inner

    def _build_frac_power_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        p, q = rng.choice([(2, 3), (3, 2), (4, 3)])
        inner = a_c * x + b_c
        return inner ** Rational(p, q), inner

    def _build_cbrt_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        inner = a_c * x + b_c
        return inner ** Rational(1, 3), inner

    def _build_exp_simple(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        inner = a_c * x
        return exp(inner), inner

    def _build_sin_simple(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        inner = a_c * x
        return sin(inner), inner

    def _build_cos_simple(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        inner = a_c * x
        return cos(inner), inner

    def _build_ln_linear(self, rng: random.Random):
        a_c = rng.randint(2, 5)
        b_c = rng.randint(1, 5)
        inner = a_c * x + b_c
        return log(inner), inner

    # ========================================================================
    # MEDIUM builders — trig/exp/log outer + linear inner, or simple outer
    #                    + quadratic inner
    # ========================================================================

    def _build_sin_linear(self, rng: random.Random):
        a_c = rng.randint(1, 5)
        b_c = rng.randint(1, 5) * rng.choice([-1, 1])
        inner = a_c * x + b_c
        return sin(inner), inner

    def _build_cos_linear(self, rng: random.Random):
        a_c = rng.randint(1, 5)
        b_c = rng.randint(1, 5) * rng.choice([-1, 1])
        inner = a_c * x + b_c
        return cos(inner), inner

    def _build_tan_linear(self, rng: random.Random):
        a_c = rng.randint(1, 4)
        b_c = rng.randint(1, 5) * rng.choice([-1, 1])
        inner = a_c * x + b_c
        return tan(inner), inner

    def _build_sec_linear(self, rng: random.Random):
        a_c = rng.randint(1, 4)
        b_c = rng.randint(1, 5) * rng.choice([-1, 1])
        inner = a_c * x + b_c
        return sec(inner), inner

    def _build_exp_linear(self, rng: random.Random):
        a_c = rng.randint(1, 5)
        b_c = rng.randint(1, 5) * rng.choice([-1, 1])
        inner = a_c * x + b_c
        return exp(inner), inner

    def _build_exp_neg(self, rng: random.Random):
        a_c = rng.randint(1, 5)
        inner = -a_c * x
        return exp(inner), inner

    def _build_ln_quad(self, rng: random.Random):
        c = rng.randint(1, 5)
        inner = x**2 + c
        return log(inner), inner

    def _build_sqrt_quad(self, rng: random.Random):
        c = rng.randint(1, 5)
        inner = x**2 + c
        return sqrt(inner), inner

    def _build_power_quad(self, rng: random.Random):
        c = rng.randint(1, 5)
        n = rng.randint(2, 4)
        inner = x**2 + c
        return inner**n, inner

    def _build_sin_quad_pure(self, rng: random.Random):
        inner = x**2
        return sin(inner), inner

    def _build_cos_quad_pure(self, rng: random.Random):
        inner = x**2
        return cos(inner), inner

    def _build_exp_quad_pure(self, rng: random.Random):
        inner = x**2
        return exp(inner), inner

    def _build_arctan_linear(self, rng: random.Random):
        a_c = rng.randint(1, 5)
        inner = a_c * x
        return atan(inner), inner

    def _build_arcsin_linear(self, rng: random.Random):
        a_c = rng.randint(1, 4)
        inner = a_c * x
        return asin(inner), inner

    def _build_recip_quad(self, rng: random.Random):
        c = rng.randint(1, 5)
        inner = x**2 + c
        return 1 / inner, inner

    # ========================================================================
    # HARD builders — non-linear inner, nested compositions, power-of-trig
    # ========================================================================

    def _build_sin_quad_shift(self, rng: random.Random):
        c = rng.randint(1, 5)
        inner = x**2 + c
        return sin(inner), inner

    def _build_exp_quad_shift(self, rng: random.Random):
        c = rng.randint(1, 5)
        inner = x**2 + c
        return exp(inner), inner

    def _build_frac_power_quad(self, rng: random.Random):
        c = rng.randint(1, 5)
        n = rng.choice([Rational(3, 2), Rational(5, 2)])
        inner = x**2 + c
        return inner**n, inner

    def _build_power_sin(self, rng: random.Random):
        n = rng.randint(2, 5)
        inner = sin(x)
        return inner**n, inner

    def _build_power_cos(self, rng: random.Random):
        n = rng.randint(2, 5)
        inner = cos(x)
        return inner**n, inner

    def _build_power_tan(self, rng: random.Random):
        n = rng.randint(2, 4)
        inner = tan(x)
        return inner**n, inner

    def _build_sqrt_sin(self, rng: random.Random):
        inner = sin(x)
        return sqrt(inner), inner

    def _build_exp_sin(self, rng: random.Random):
        inner = sin(x)
        return exp(inner), inner

    def _build_ln_cos(self, rng: random.Random):
        inner = cos(x)
        return log(inner), inner

    def _build_sin_exp(self, rng: random.Random):
        inner = exp(x)
        return sin(inner), inner

    def _build_exp_sqrt(self, rng: random.Random):
        inner = sqrt(x)
        return exp(inner), inner

    def _build_sin_ln(self, rng: random.Random):
        inner = log(x)
        return sin(inner), inner

    def _build_cos_cubic(self, rng: random.Random):
        inner = x**3
        return cos(inner), inner


# ---------------------------------------------------------------------------
# 4. BasicIntegralTemplate
# ---------------------------------------------------------------------------
@register_template
class BasicIntegralTemplate:
    topic = Topic.CALCULUS
    subtopic = "basic_integral"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Backward: pick antiderivative F, differentiate to get f."""
        if difficulty == Difficulty.EASY:
            # Single power term: F(x) = a*x^n => f(x) = a*n*x^(n-1)
            a = rng.randint(1, 5)
            n = rng.randint(2, 5)
            antideriv = a * x**n
            integrand = diff(antideriv, x)
        elif difficulty == Difficulty.MEDIUM:
            # Sum of power terms
            num_terms = rng.randint(2, 3)
            terms = []
            used_powers = set()
            for _ in range(num_terms):
                c = rng.randint(1, 5)
                p = rng.randint(2, 6)
                for _ in range(50):
                    if p not in used_powers:
                        break
                    p = rng.randint(2, 6)
                else:
                    raise GenerationError("Parameter sampling exhausted")
                used_powers.add(p)
                terms.append(c * x**p)
            antideriv = sum(terms)
            integrand = diff(antideriv, x)
        else:
            # Simple substitution: F(x) = (ax + b)^n / (a*n)
            a_c = rng.randint(1, 5)
            b_c = rng.randint(1, 5)
            n = rng.randint(2, 4)
            inner = a_c * x + b_c
            antideriv = inner**n / (a_c * n)
            integrand = simplify(diff(antideriv, x))

        # Compute integral to verify and get canonical form
        result = integrate(integrand, x)

        # -- Build solution steps --
        int_tex = f"\\int {latex(integrand)} \\, dx"
        if difficulty == Difficulty.EASY:
            steps: list[TrustedLatex] = [
                TrustedLatex(f"${int_tex}$"),
                TrustedLatex(f"$= {latex(result)} + C$"),
            ]
        elif difficulty == Difficulty.MEDIUM:
            ordered = integrand.as_ordered_terms()
            if len(ordered) > 1:
                split = Add(
                    *[Integral(t, x) for t in ordered],
                    evaluate=False,
                )
                steps = [
                    TrustedLatex(f"${int_tex}$"),
                    TrustedLatex(f"$= {latex(split)}$"),
                    TrustedLatex(f"$= {latex(result)} + C$"),
                ]
            else:
                steps = [
                    TrustedLatex(f"${int_tex}$"),
                    TrustedLatex(f"$= {latex(result)} + C$"),
                ]
        else:
            u = Symbol("u")
            du_dx = diff(inner, x)
            u_integrand = simplify(integrand.subs(inner, u) / du_dx)
            u_result = integrate(u_integrand, u)
            coeff = Rational(1, du_dx)
            steps = [
                TrustedLatex(f"${int_tex}$"),
                TrustedLatex(f"$u = {latex(inner)}, \\quad du = {latex(du_dx)} \\, dx$"),
                TrustedLatex(
                    f"$= {latex(coeff)} \\int"
                    f" {latex(u_integrand * du_dx)}"
                    f" \\, du = {latex(u_result)}$"
                ),
                TrustedLatex(f"$= {latex(result)} + C$"),
            ]

        question = f"Evaluate $\\displaystyle\\int {latex(integrand)} \\, dx$."
        answer_str = f"${latex(result)} + C$"
        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(answer_str),
            topic=Topic.CALCULUS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={
                "integrand": latex(integrand),
                "antiderivative": latex(result),
            },
            solution_steps=tuple(steps),
        )
