"""Domain problem templates — basic function families.

Covers rational and radical domain problems.

Templates:
    RationalDomainTemplate   (subtopic = "domain_rational")
    RadicalDomainTemplate    (subtopic = "domain_radical")
"""

from __future__ import annotations

import random

from sympy import (
    Abs,
    Pow,
    Rational,
    Symbol,
    latex,
    oo,
    sqrt,
)

from app.engine.registry import register_template
from app.engine.topics.domain._helpers import (
    _distinct_pair,
    fmt_all_reals,
    fmt_interval,
    fmt_set_minus,
    fmt_union,
)
from app.engine.types import (
    ALL_DIFFICULTIES,
    Difficulty,
    GeneratedProblem,
    GenerationError,
    Topic,
    TrustedLatex,
)

x = Symbol("x")


# ---------------------------------------------------------------------------
# RationalDomainTemplate — subtopic "domain_rational"
# ---------------------------------------------------------------------------


@register_template
class RationalDomainTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "domain_rational"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["simple_reciprocal", "linear_reciprocal"])

        if variant == "simple_reciprocal":
            # f(x) = 1/(x - a)  =>  R \ {a}
            a = rng.randint(1, 10)
            expr = 1 / (x - a)
            answer = fmt_set_minus([a])
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x \\neq {latex(a)}$"),
                TrustedLatex(f"${answer}$"),
            ]
        else:
            # f(x) = c/(ax + b)  =>  R \ {-b/a}
            a_coeff = rng.randint(1, 5)
            b_coeff = rng.randint(1, 10)
            c_coeff = rng.randint(1, 5)
            # randomly negate b to get some variety
            if rng.random() < 0.5:
                b_coeff = -b_coeff
            expr = c_coeff / (a_coeff * x + b_coeff)
            excluded = Rational(-b_coeff, a_coeff)
            answer = fmt_set_minus([excluded])
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x \\neq {latex(excluded)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {latex(expr)}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(
            [
                "two_linear_factors",
                "numerator_no_cancel",
                "sum_of_squares",
            ]
        )

        if variant == "two_linear_factors":
            # f(x) = 1/((x-a)(x-b))  =>  R \ {a, b}
            a, b = _distinct_pair(rng, 1, 8)
            expr = 1 / ((x - a) * (x - b))
            answer = fmt_set_minus([a, b])
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x \\neq {latex(a)}, \\; x \\neq {latex(b)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        elif variant == "numerator_no_cancel":
            # f(x) = (x+c)/((x-a)(x-b)), c != a and c != b  =>  R \ {a, b}
            a, b = _distinct_pair(rng, 1, 8)
            for _ in range(50):
                c = rng.randint(1, 10)
                if c != a and c != b:
                    break
            else:
                raise GenerationError("Parameter sampling exhausted")
            expr = (x + c) / ((x - a) * (x - b))
            answer = fmt_set_minus([a, b])
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x \\neq {latex(a)}, \\; x \\neq {latex(b)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # f(x) = 1/(x^2 + a), a > 0  =>  R  (trick: no real roots)
            a_val = rng.randint(1, 9)
            expr = 1 / (x**2 + a_val)
            answer = fmt_all_reals()
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x^2 + {latex(a_val)} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {latex(expr)}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["three_excluded", "cancellation_trap"])

        if variant == "three_excluded":
            # f(x) = 1/(x(x^2 - a^2))  =>  R \ {0, a, -a}
            a = rng.randint(1, 7)
            expr = 1 / (x * (x**2 - a**2))
            answer = fmt_set_minus([-a, 0, a])
            q_latex = f"Find the domain of $f(x) = {latex(expr)}$."
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x \\neq {latex(-a)}, \\; x \\neq 0, \\; x \\neq {latex(a)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # f(x) = (x-a)/((x-a)(x-b))  =>  R \ {a, b}  (cancellation trap)
            # Build LaTeX manually to prevent SymPy from auto-simplifying
            # the expression to 1/(x-b), which would hide the removable
            # discontinuity at x = a.
            a, b = _distinct_pair(rng, 1, 8)
            answer = fmt_set_minus([a, b])
            q_latex = (
                rf"Find the domain of $f(x) = \frac{{x - {a}}}"
                rf"{{(x - {a})(x - {b})}}$."
            )
            steps = [
                TrustedLatex(f"$f(x) = \\frac{{x - {a}}}{{(x - {a})(x - {b})}}$"),
                TrustedLatex(f"$x \\neq {latex(a)}, \\; x \\neq {latex(b)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(q_latex),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# RadicalDomainTemplate — subtopic "domain_radical"
# ---------------------------------------------------------------------------


@register_template
class RadicalDomainTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "domain_radical"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["square_root_linear", "cube_root_linear"])

        if variant == "square_root_linear":
            # f(x) = sqrt(ax + b), a > 0  =>  [-b/a, inf)
            a = rng.randint(1, 5)
            b = rng.randint(-10, 10)
            expr = sqrt(a * x + b)
            bound = Rational(-b, a)
            answer = fmt_interval(bound, oo, lower_inclusive=True, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"${latex(a * x + b)} \\geq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # f(x) = cbrt(ax + b)  =>  R  (odd root, trick question)
            a = rng.randint(1, 5)
            b = rng.randint(-10, 10)
            expr = Pow(a * x + b, Rational(1, 3))
            answer = fmt_all_reals()
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {latex(expr)}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["quadratic_product", "circle_form"])

        if variant == "quadratic_product":
            # f(x) = sqrt((x-a)(x-b)), a < b  =>  (-inf, a] union [b, inf)
            a, b = _distinct_pair(rng, 1, 8)
            expr = sqrt((x - a) * (x - b))
            answer = fmt_union(
                [
                    fmt_interval(-oo, a, lower_inclusive=False, upper_inclusive=True),
                    fmt_interval(b, oo, lower_inclusive=True, upper_inclusive=False),
                ]
            )
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$(x - {latex(a)})(x - {latex(b)}) \\geq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # f(x) = sqrt(a^2 - x^2)  =>  [-a, a]
            a = rng.randint(1, 9)
            expr = sqrt(a**2 - x**2)
            answer = fmt_interval(-a, a, lower_inclusive=True, upper_inclusive=True)
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"${latex(a)}^2 - x^2 \\geq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {latex(expr)}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["nested_radical", "absolute_value_radical"])

        if variant == "nested_radical":
            # f(x) = sqrt(sqrt(x) - a), a > 0  =>  [a^2, inf)
            a = rng.randint(1, 5)
            expr = sqrt(sqrt(x) - a)
            bound = a**2
            answer = fmt_interval(bound, oo, lower_inclusive=True, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$\\sqrt{{x}} \\geq {latex(a)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # f(x) = sqrt(|x| - a), a > 0  =>  (-inf, -a] union [a, inf)
            a = rng.randint(1, 7)
            expr = sqrt(Abs(x) - a)
            answer = fmt_union(
                [
                    fmt_interval(-oo, -a, lower_inclusive=False, upper_inclusive=True),
                    fmt_interval(a, oo, lower_inclusive=True, upper_inclusive=False),
                ]
            )
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$|x| \\geq {latex(a)}$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {latex(expr)}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )
