"""Domain problem templates — advanced function families.

Covers logarithmic, composite, and trigonometric domain problems.

Templates:
    LogDomainTemplate        (subtopic = "domain_logarithmic")
    CompositeDomainTemplate  (subtopic = "domain_composite")
    TrigDomainTemplate       (subtopic = "domain_trigonometric")
"""

from __future__ import annotations

import random

from sympy import (
    Rational,
    Symbol,
    acos,
    asin,
    csc,
    latex,
    oo,
    sec,
    sqrt,
    tan,
)

from app.engine.registry import register_template
from app.engine.topics.domain._helpers import (
    _distinct_pair,
    fmt_interval,
    fmt_periodic_exclusion,
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
# LogDomainTemplate — subtopic "domain_logarithmic"
# ---------------------------------------------------------------------------


@register_template
class LogDomainTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "domain_logarithmic"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["log_base10_or_e", "log_base_b"])

        if variant == "log_base10_or_e":
            # log(ax + b) base 10 or e  =>  (-b/a, inf)
            a = rng.randint(1, 5)
            b = rng.randint(-10, 10)
            use_ln = rng.choice([True, False])
            if use_ln:
                expr_latex = f"\\ln({latex(a * x + b)})"
            else:
                expr_latex = f"\\log({latex(a * x + b)})"
            bound = Rational(-b, a)
            answer = fmt_interval(bound, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"${latex(a * x + b)} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # log_b(ax + c) with b in {2, 3, 5, 10}
            base = rng.choice([2, 3, 5, 10])
            a = rng.randint(1, 5)
            c = rng.randint(-10, 10)
            expr_latex = f"\\log_{{{base}}}({latex(a * x + c)})"
            bound = Rational(-c, a)
            answer = fmt_interval(bound, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"${latex(a * x + c)} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["log_quadratic", "log_abs"])

        if variant == "log_quadratic":
            # log(x^2 - a^2)  =>  (-inf, -a) union (a, inf)
            a = rng.randint(1, 7)
            arg = x**2 - a**2
            use_ln = rng.choice([True, False])
            if use_ln:
                expr_latex = f"\\ln({latex(arg)})"
            else:
                expr_latex = f"\\log({latex(arg)})"
            answer = fmt_union(
                [
                    fmt_interval(-oo, -a, lower_inclusive=False, upper_inclusive=False),
                    fmt_interval(a, oo, lower_inclusive=False, upper_inclusive=False),
                ]
            )
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"${latex(arg)} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # log(|x - a|)  =>  R \ {a}
            a = rng.randint(1, 9)
            use_ln = rng.choice([True, False])
            if use_ln:
                expr_latex = f"\\ln(|x - {a}|)"
            else:
                expr_latex = f"\\log(|x - {a}|)"
            answer = fmt_set_minus([a])
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"$|x - {a}| > 0,\\; x \\neq {a}$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["log_fraction", "log_log"])

        if variant == "log_fraction":
            # ln((x-a)/(x-b)), a < b  =>  (-inf, a) union (b, inf)
            a, b = _distinct_pair(rng, 1, 8)
            expr_latex = f"\\ln\\!\\left(\\frac{{x - {a}}}{{x - {b}}}\\right)"
            answer = fmt_union(
                [
                    fmt_interval(-oo, a, lower_inclusive=False, upper_inclusive=False),
                    fmt_interval(b, oo, lower_inclusive=False, upper_inclusive=False),
                ]
            )
            frac_ltx = f"\\frac{{x - {a}}}{{x - {b}}}"
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"${frac_ltx} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # log(log(x - a))  =>  (a + 1, inf)
            a = rng.randint(0, 5)
            expr_latex = f"\\log(\\log(x - {a}))"
            bound = a + 1
            answer = fmt_interval(bound, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"$\\log(x - {a}) > 0,\\; x - {a} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# CompositeDomainTemplate — subtopic "domain_composite"
# ---------------------------------------------------------------------------


@register_template
class CompositeDomainTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "domain_composite"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["reciprocal_sqrt", "log_sqrt"])

        if variant == "reciprocal_sqrt":
            # 1/sqrt(ax + b)  =>  (-b/a, inf)  (strict inequality)
            a = rng.randint(1, 5)
            b = rng.randint(-10, 10)
            expr = 1 / sqrt(a * x + b)
            bound = Rational(-b, a)
            answer = fmt_interval(bound, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"${latex(a * x + b)} > 0$"),
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

        else:
            # log(sqrt(x - a))  =>  (a, inf)
            a = rng.randint(0, 8)
            use_ln = rng.choice([True, False])
            if use_ln:
                expr_latex = f"\\ln(\\sqrt{{x - {a}}})"
            else:
                expr_latex = f"\\log(\\sqrt{{x - {a}}})"
            answer = fmt_interval(a, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"$x - {a} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

            return GeneratedProblem(
                question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
                answer_latex=TrustedLatex(f"${answer}$"),
                topic=Topic.FUNCTIONS,
                difficulty=Difficulty.EASY,
                subtopic=self.subtopic,
                solution_steps=tuple(steps),
            )

    # -- MEDIUM -------------------------------------------------------------

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["sqrt_reciprocal", "sqrt_log", "reciprocal_log"])

        if variant == "sqrt_reciprocal":
            # sqrt(1/(x - a))  =>  (a, inf)
            a = rng.randint(1, 8)
            expr = sqrt(1 / (x - a))
            answer = fmt_interval(a, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$x - {a} > 0$"),
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

        elif variant == "sqrt_log":
            # sqrt(log(x)) or sqrt(ln(x))  =>  [1, inf)
            use_ln = rng.choice([True, False])
            if use_ln:
                expr_latex = "\\sqrt{\\ln(x)}"
                log_fn = "\\ln"
            else:
                expr_latex = "\\sqrt{\\log(x)}"
                log_fn = "\\log"
            answer = fmt_interval(1, oo, lower_inclusive=True, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"${log_fn}(x) \\geq 0,\\; x \\geq 1$"),
                TrustedLatex(f"${answer}$"),
            ]

            return GeneratedProblem(
                question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
                answer_latex=TrustedLatex(f"${answer}$"),
                topic=Topic.FUNCTIONS,
                difficulty=Difficulty.MEDIUM,
                subtopic=self.subtopic,
                solution_steps=tuple(steps),
            )

        else:
            # 1/log(x - a)  =>  (a, inf) \ {a + 1}
            a = rng.randint(0, 6)
            use_ln = rng.choice([True, False])
            if use_ln:
                expr_latex = f"\\frac{{1}}{{\\ln(x - {a})}}"
                log_fn = "\\ln"
            else:
                expr_latex = f"\\frac{{1}}{{\\log(x - {a})}}"
                log_fn = "\\log"
            excluded = a + 1
            inner_interval = fmt_interval(a, oo, lower_inclusive=False, upper_inclusive=False)
            answer = f"{inner_interval} \\setminus \\{{{excluded}\\}}"
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"$x - {a} > 0,\\; {log_fn}(x - {a}) \\neq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

            return GeneratedProblem(
                question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
                answer_latex=TrustedLatex(f"${answer}$"),
                topic=Topic.FUNCTIONS,
                difficulty=Difficulty.MEDIUM,
                subtopic=self.subtopic,
                solution_steps=tuple(steps),
            )

    # -- HARD ---------------------------------------------------------------

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        variant = rng.choice(["sqrt_ln_reciprocal", "ln_over_linear", "sqrt_plus_log"])

        if variant == "sqrt_ln_reciprocal":
            # sqrt(ln(1/(x-a)))  =>  (a, a+1]
            a = rng.randint(0, 6)
            expr_latex = f"\\sqrt{{\\ln\\!\\left(\\frac{{1}}{{x - {a}}}\\right)}}"
            answer = fmt_interval(a, a + 1, lower_inclusive=False, upper_inclusive=True)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(
                    f"$\\ln\\!\\left(\\frac{{1}}{{x - {a}}}\\right) \\geq 0,\\; x - {a} > 0$"
                ),
                TrustedLatex(f"${answer}$"),
            ]

        elif variant == "ln_over_linear":
            # ln(x-a)/(x-b)  =>  (a, inf) \ {b}
            a = rng.randint(0, 5)
            for _ in range(50):
                b = rng.randint(1, 8)
                if b != a:
                    break
            else:
                raise GenerationError("Parameter sampling exhausted")
            expr_latex = f"\\frac{{\\ln(x - {a})}}{{x - {b}}}"
            inner_interval = fmt_interval(a, oo, lower_inclusive=False, upper_inclusive=False)
            answer = f"{inner_interval} \\setminus \\{{{b}\\}}"
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"$x - {a} > 0,\\; x \\neq {b}$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # sqrt(x-a) + log(x-b)
            a = rng.randint(0, 5)
            for _ in range(50):
                b = rng.randint(0, 5)
                if b != a:
                    break
            else:
                raise GenerationError("Parameter sampling exhausted")
            use_ln = rng.choice([True, False])
            log_fn = "\\ln" if use_ln else "\\log"
            expr_latex = f"\\sqrt{{x - {a}}} + {log_fn}(x - {b})"
            if a >= b:
                # sqrt needs x >= a, log needs x > b; since a > b, [a, inf) works
                answer = fmt_interval(a, oo, lower_inclusive=True, upper_inclusive=False)
            else:
                # b > a: sqrt needs x >= a, log needs x > b; stricter is x > b
                answer = fmt_interval(b, oo, lower_inclusive=False, upper_inclusive=False)
            steps = [
                TrustedLatex(f"$f(x) = {expr_latex}$"),
                TrustedLatex(f"$x - {a} \\geq 0,\\; x - {b} > 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Find the domain of $f(x) = {expr_latex}$."),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.FUNCTIONS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# TrigDomainTemplate — subtopic "domain_trigonometric"
# ---------------------------------------------------------------------------


@register_template
class TrigDomainTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "domain_trigonometric"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    # -- EASY ---------------------------------------------------------------

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        # tan(x)  =>  R \ {pi/2 + n*pi | n in Z}
        expr = tan(x)
        answer = fmt_periodic_exclusion("\\frac{\\pi}{2}", "\\pi")
        steps = [
            TrustedLatex(f"$f(x) = {latex(expr)}$"),
            TrustedLatex("$\\cos(x) \\neq 0$"),
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
        variant = rng.choice(["sec", "csc", "arcsin_linear"])

        if variant == "sec":
            # sec(x) = 1/cos(x)  =>  R \ {pi/2 + n*pi | n in Z}
            expr = sec(x)
            answer = fmt_periodic_exclusion("\\frac{\\pi}{2}", "\\pi")
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex("$\\cos(x) \\neq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        elif variant == "csc":
            # csc(x) = 1/sin(x)  =>  R \ {n*pi | n in Z}
            expr = csc(x)
            answer = fmt_periodic_exclusion("0", "\\pi")
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex("$\\sin(x) \\neq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # arcsin(ax + b)  =>  [(-1-b)/a, (1-b)/a]
            a = rng.randint(1, 4)
            b_val = rng.randint(-3, 3)
            expr = asin(a * x + b_val)
            lower_bound = Rational(-1 - b_val, a)
            upper_bound = Rational(1 - b_val, a)
            answer = fmt_interval(
                lower_bound,
                upper_bound,
                lower_inclusive=True,
                upper_inclusive=True,
            )
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$-1 \\leq {latex(a * x + b_val)} \\leq 1$"),
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
        variant = rng.choice(["arcsin_reciprocal", "arccos_shifted"])

        if variant == "arcsin_reciprocal":
            # arcsin(1/x)  =>  (-inf, -1] union [1, inf)
            expr = asin(1 / x)
            answer = fmt_union(
                [
                    fmt_interval(-oo, -1, lower_inclusive=False, upper_inclusive=True),
                    fmt_interval(1, oo, lower_inclusive=True, upper_inclusive=False),
                ]
            )
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex("$-1 \\leq \\frac{1}{x} \\leq 1,\\; x \\neq 0$"),
                TrustedLatex(f"${answer}$"),
            ]

        else:
            # arccos((x-a)/b)  =>  [a-b, a+b]
            a = rng.randint(1, 6)
            b = rng.randint(1, 5)
            expr = acos((x - a) / b)
            lower_bound = a - b
            upper_bound = a + b
            answer = fmt_interval(
                lower_bound,
                upper_bound,
                lower_inclusive=True,
                upper_inclusive=True,
            )
            frac_ltx = latex((x - a) / b)
            steps = [
                TrustedLatex(f"$f(x) = {latex(expr)}$"),
                TrustedLatex(f"$-1 \\leq {frac_ltx} \\leq 1$"),
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
