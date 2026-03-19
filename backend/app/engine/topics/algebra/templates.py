"""Algebra topic templates (T008-T012).

Every template uses backward construction: generate the answer first,
then build the problem from it.  This guarantees solvability for all
difficulty levels.
"""

from __future__ import annotations

import math
import random

import sympy
from sympy import Eq, Rational, Symbol, latex, sqrt

from app.engine.registry import register_template
from app.engine.types import (
    ALL_DIFFICULTIES,
    Difficulty,
    GeneratedProblem,
    GenerationError,
    Topic,
    TrustedLatex,
)

x = Symbol("x")
y_sym = Symbol("y")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _int_range(difficulty: Difficulty) -> tuple[int, int]:
    """Return (lo, hi) for coefficient sampling based on difficulty."""
    if difficulty == Difficulty.EASY:
        return 1, 5
    if difficulty == Difficulty.MEDIUM:
        return 5, 15
    return 10, 30


def _nonzero_int(rng: random.Random, lo: int, hi: int) -> int:
    """Return a random nonzero integer in [-hi, -lo] | [lo, hi]."""
    val = rng.randint(lo, hi)
    return val if rng.random() < 0.5 else -val


# ---------------------------------------------------------------------------
# T008 — Linear Equation: ax + b = c
# ---------------------------------------------------------------------------


@register_template
class LinearEquationTemplate:
    topic = Topic.ALGEBRA
    subtopic = "linear_equations"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        lo, hi = _int_range(difficulty)

        # Backward: pick x first
        x_val = _nonzero_int(rng, lo, hi)
        a = _nonzero_int(rng, lo, hi)
        b = _nonzero_int(rng, lo, hi)
        c = a * x_val + b  # guarantees ax + b = c

        lhs = a * x + b
        question = latex(Eq(lhs, c))
        answer = latex(Eq(x, x_val))

        # Build solution steps
        steps = [TrustedLatex(f"${latex(Eq(a * x + b, c))}$")]
        steps.append(TrustedLatex(f"${latex(Eq(a * x, c - b))}$"))
        if a != 1 and a != -1:
            steps.append(TrustedLatex(f"${latex(Eq(x, Rational(c - b, a)))}$"))

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Solve for $x$: ${question}$"),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T009 — Two-Step Linear: ax + b = cx + d
# ---------------------------------------------------------------------------


@register_template
class TwoStepLinearTemplate:
    topic = Topic.ALGEBRA
    subtopic = "two_step_linear"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        lo, hi = _int_range(difficulty)

        # Backward: pick x, a, b, c (a != c), compute d
        if difficulty == Difficulty.EASY:
            x_val = rng.randint(1, 5)
        elif difficulty == Difficulty.MEDIUM:
            # allow fractional answers
            num = _nonzero_int(rng, 1, 10)
            den = rng.choice([2, 3, 4, 5])
            x_val = Rational(num, den)
        else:
            num = _nonzero_int(rng, 5, 20)
            den = rng.choice([3, 7, 11, 13])
            x_val = Rational(num, den)

        a = _nonzero_int(rng, lo, hi)
        for _ in range(50):
            c = _nonzero_int(rng, lo, hi)
            if c != a:
                break
        else:
            raise GenerationError("Parameter sampling exhausted")
        b = _nonzero_int(rng, lo, hi)
        d = a * x_val + b - c * x_val  # ax + b = cx + d  =>  d = (a-c)x + b

        lhs = a * x + b
        rhs = c * x + d
        question = latex(Eq(lhs, rhs))
        answer = latex(Eq(x, x_val))

        # Build solution steps
        steps = [TrustedLatex(f"${latex(Eq(a * x + b, c * x + d))}$")]
        # Collect x terms on left, constants on right
        coeff_diff = a - c
        const_diff = d - b
        steps.append(TrustedLatex(f"${latex(Eq(coeff_diff * x, const_diff))}$"))
        if coeff_diff != 1 and coeff_diff != -1:
            steps.append(TrustedLatex(f"${latex(Eq(x, Rational(const_diff, coeff_diff)))}$"))

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Solve for $x$: ${question}$"),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T010 — Quadratic Factoring: x^2 + bx + c = 0
# ---------------------------------------------------------------------------


@register_template
class QuadraticFactoringTemplate:
    topic = Topic.ALGEBRA
    subtopic = "quadratic_factoring"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        lo, hi = _int_range(difficulty)

        # Backward: pick roots r1, r2, expand (x - r1)(x - r2)
        r1 = _nonzero_int(rng, lo, hi)
        r2 = _nonzero_int(rng, lo, hi)
        if difficulty == Difficulty.EASY:
            # keep roots positive and small for easy
            r1, r2 = abs(r1), abs(r2)

        poly = sympy.expand((x - r1) * (x - r2))
        question = latex(Eq(poly, 0))

        # Sorted roots for a canonical answer
        roots_sorted = sorted([r1, r2])
        factored = latex((x - roots_sorted[0]) * (x - roots_sorted[1]))
        answer_roots = f"x = {latex(roots_sorted[0])}, \\; x = {latex(roots_sorted[1])}"

        # Build solution steps
        steps = [
            TrustedLatex(f"${latex(Eq(poly, 0))}$"),
            TrustedLatex(f"${factored} = 0$"),
            TrustedLatex(f"${answer_roots}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Factor and solve: ${question}$"),
            answer_latex=TrustedLatex(f"${factored} = 0$, so ${answer_roots}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T010b — Quadratic Formula
# ---------------------------------------------------------------------------


@register_template
class QuadraticFormulaTemplate:
    topic = Topic.ALGEBRA
    subtopic = "quadratic_formula"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            # Perfect-square discriminant, integer roots
            r1 = rng.randint(1, 5)
            r2 = rng.randint(1, 5)
            a = 1
            b_coeff = -(r1 + r2)
            c_coeff = r1 * r2
        elif difficulty == Difficulty.MEDIUM:
            # Perfect-square discriminant, but a != 1 => fractional roots
            a = rng.choice([2, 3])
            r1 = rng.randint(-8, 8) or 1
            r2 = rng.randint(-8, 8) or 1
            b_coeff = -(r1 + r2)
            c_coeff = r1 * r2
            # scale: a*x^2 + a*b*x + a*c = 0  =>  same roots
            b_coeff *= a
            c_coeff *= a
        else:
            # Irrational roots — non-perfect-square discriminant
            a = rng.choice([1, 2, 3])
            b_coeff = _nonzero_int(rng, 3, 12)
            # choose c so discriminant > 0 but not a perfect square
            disc = -1
            for _ in range(50):
                c_coeff = _nonzero_int(rng, 1, 10)
                disc = b_coeff**2 - 4 * a * c_coeff
                if disc > 0 and not _is_perfect_square(disc):
                    break
            else:
                raise GenerationError("Parameter sampling exhausted")

        poly = a * x**2 + b_coeff * x + c_coeff
        question = latex(Eq(poly, 0))

        # Compute symbolic roots
        roots = sympy.solve(poly, x)
        roots_sorted = sorted(roots, key=lambda r: float(r.evalf()))
        answer = ", \\; ".join(f"x = {latex(r)}" for r in roots_sorted)

        # Build solution steps
        disc = b_coeff**2 - 4 * a * c_coeff
        steps = [TrustedLatex(f"${latex(Eq(poly, 0))}$")]
        # Show the quadratic formula substitution
        disc_expr = sympy.Integer(disc)
        sqrt_disc = sqrt(disc_expr, evaluate=False)
        neg_b = sympy.Integer(-b_coeff)
        two_a = sympy.Integer(2 * a)
        steps.append(
            TrustedLatex(
                f"$x = \\frac{{{latex(neg_b)} \\pm {latex(sqrt_disc)}}}{{{latex(two_a)}}}$"
            )
        )
        # If discriminant is a perfect square, show the simplified sqrt value
        if disc >= 0 and _is_perfect_square(disc):
            sqrt_val = int(math.isqrt(disc))
            sqrt_int = latex(sympy.Integer(sqrt_val))
            steps.append(
                TrustedLatex(f"$x = \\frac{{{latex(neg_b)} \\pm {sqrt_int}}}{{{latex(two_a)}}}$")
            )
        # Final roots
        answer_step = ", \\; ".join(f"x = {latex(r)}" for r in roots_sorted)
        steps.append(TrustedLatex(f"${answer_step}$"))

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Solve using the quadratic formula: ${question}$"),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


def _is_perfect_square(n: int) -> bool:
    if n < 0:
        return False
    root = int(math.isqrt(n))
    return root * root == n


# ---------------------------------------------------------------------------
# T011 — Polynomial Add / Subtract
# ---------------------------------------------------------------------------


@register_template
class PolynomialAddSubTemplate:
    topic = Topic.ALGEBRA
    subtopic = "polynomial_add_sub"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        lo, hi = _int_range(difficulty)
        op = rng.choice(["+", "-"])

        if difficulty == Difficulty.EASY:
            degree = 2
        elif difficulty == Difficulty.MEDIUM:
            degree = 3
        else:
            degree = rng.randint(4, 5)

        def _rand_poly(deg: int) -> sympy.Expr:
            return sum(_nonzero_int(rng, lo, hi) * x**i for i in range(deg + 1))

        p = _rand_poly(degree)
        q = _rand_poly(degree)

        if op == "+":
            result = sympy.expand(p + q)
            question = f"({latex(p)}) + ({latex(q)})"
        else:
            result = sympy.expand(p - q)
            question = f"({latex(p)}) - ({latex(q)})"

        # Build solution steps
        steps = [
            TrustedLatex(f"${question}$"),
            TrustedLatex(f"${latex(result)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Simplify: ${question}$"),
            answer_latex=TrustedLatex(f"${latex(result)}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T011b — Polynomial Multiply
# ---------------------------------------------------------------------------


@register_template
class PolynomialMultiplyTemplate:
    topic = Topic.ALGEBRA
    subtopic = "polynomial_multiply"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        lo, hi = _int_range(difficulty)

        if difficulty == Difficulty.EASY:
            # Monomial * binomial  or  binomial * binomial (FOIL)
            p = _nonzero_int(rng, lo, hi) * x + _nonzero_int(rng, lo, hi)
            q = _nonzero_int(rng, lo, hi) * x + _nonzero_int(rng, lo, hi)
        elif difficulty == Difficulty.MEDIUM:
            # Binomial * trinomial
            p = _nonzero_int(rng, lo, hi) * x + _nonzero_int(rng, lo, hi)
            q = (
                _nonzero_int(rng, lo, hi) * x**2
                + _nonzero_int(rng, lo, hi) * x
                + _nonzero_int(rng, lo, hi)
            )
        else:
            # Trinomial * trinomial
            p = (
                _nonzero_int(rng, 1, 5) * x**2
                + _nonzero_int(rng, lo, hi) * x
                + _nonzero_int(rng, lo, hi)
            )
            q = (
                _nonzero_int(rng, 1, 5) * x**2
                + _nonzero_int(rng, lo, hi) * x
                + _nonzero_int(rng, lo, hi)
            )

        result = sympy.expand(p * q)
        question = f"({latex(p)}) \\cdot ({latex(q)})"

        # Build solution steps: show distribution then combined result
        # Generate individual term products (FOIL / distribution)
        p_terms = sympy.Add.make_args(sympy.expand(p))
        q_terms = sympy.Add.make_args(sympy.expand(q))
        cross_terms = [pi * qi for pi in p_terms for qi in q_terms]
        distributed_expr = sympy.Add(*cross_terms, evaluate=False)
        steps = [TrustedLatex(f"$({latex(p)}) \\cdot ({latex(q)})$")]
        # Only show intermediate distribution step if it differs from result
        if distributed_expr != result:
            steps.append(TrustedLatex(f"${latex(distributed_expr)}$"))
        steps.append(TrustedLatex(f"${latex(result)}$"))

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Expand: ${question}$"),
            answer_latex=TrustedLatex(f"${latex(result)}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T012 — System of 2 Linear Equations
# ---------------------------------------------------------------------------


@register_template
class SystemOf2LinearTemplate:
    topic = Topic.ALGEBRA
    subtopic = "systems_of_equations"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        lo, hi = _int_range(difficulty)

        # Backward: pick the solution (x, y) first
        if difficulty == Difficulty.EASY:
            x_val = rng.randint(1, 5)
            y_val = rng.randint(1, 5)
        elif difficulty == Difficulty.MEDIUM:
            x_val = _nonzero_int(rng, 1, 10)
            y_val = _nonzero_int(rng, 1, 10)
        else:
            num_x = _nonzero_int(rng, 1, 10)
            den_x = rng.choice([2, 3, 5])
            x_val = Rational(num_x, den_x)
            num_y = _nonzero_int(rng, 1, 10)
            den_y = rng.choice([2, 3, 5])
            y_val = Rational(num_y, den_y)

        # Generate two linearly independent equations
        a1 = _nonzero_int(rng, lo, hi)
        b1 = _nonzero_int(rng, lo, hi)
        a2 = _nonzero_int(rng, lo, hi)
        b2 = _nonzero_int(rng, lo, hi)

        # Ensure the coefficient matrix is non-singular
        for _ in range(50):
            a2 = _nonzero_int(rng, lo, hi)
            b2 = _nonzero_int(rng, lo, hi)
            if a1 * b2 != a2 * b1:
                break
        else:
            raise GenerationError("Parameter sampling exhausted")

        c1 = a1 * x_val + b1 * y_val
        c2 = a2 * x_val + b2 * y_val

        eq1 = latex(Eq(a1 * x + b1 * y_sym, c1))
        eq2 = latex(Eq(a2 * x + b2 * y_sym, c2))

        system = f"\\begin{{cases}} {eq1} \\\\ {eq2} \\end{{cases}}"
        answer = f"x = {latex(x_val)}, \\; y = {latex(y_val)}"

        # Build solution steps — elimination method (Cramer's rule)
        det = a1 * b2 - a2 * b1
        det_x = c1 * b2 - c2 * b1
        steps = [
            TrustedLatex(f"${eq1}, \\quad {eq2}$"),
            TrustedLatex(f"${latex(Eq(sympy.S(det) * x, sympy.S(det_x)))}$"),
            TrustedLatex(f"$x = {latex(x_val)}$"),
            TrustedLatex(f"$y = {latex(y_val)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Solve the system: ${system}$"),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T012b — Exponent Simplify: x^a * x^b / x^c
# ---------------------------------------------------------------------------


@register_template
class ExponentSimplifyTemplate:
    topic = Topic.ALGEBRA
    subtopic = "exponent_rules"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            # x^a * x^b  (no division)
            a = rng.randint(1, 5)
            b = rng.randint(1, 5)
            result_exp = a + b
            question = f"x^{{{a}}} \\cdot x^{{{b}}}"
        elif difficulty == Difficulty.MEDIUM:
            # x^a * x^b / x^c
            a = rng.randint(3, 10)
            b = rng.randint(3, 10)
            c = rng.randint(1, a + b - 1)  # keep exponent positive
            result_exp = a + b - c
            question = f"\\frac{{x^{{{a}}} \\cdot x^{{{b}}}}}{{x^{{{c}}}}}"
        else:
            # (x^a)^b * x^c / x^d — power of a power
            a = rng.randint(2, 6)
            b = rng.randint(2, 5)
            c = rng.randint(1, 10)
            d = rng.randint(1, a * b + c - 1)
            result_exp = a * b + c - d
            question = f"\\frac{{(x^{{{a}}})^{{{b}}} \\cdot x^{{{c}}}}}{{x^{{{d}}}}}"

        if result_exp == 0:
            answer = "1"
        elif result_exp == 1:
            answer = "x"
        else:
            answer = f"x^{{{result_exp}}}"

        # Build solution steps
        steps = [TrustedLatex(f"${question}$")]
        if difficulty == Difficulty.EASY:
            # x^a * x^b -> x^{a+b}
            steps.append(TrustedLatex(f"$x^{{{a}+{b}}}$"))
        elif difficulty == Difficulty.MEDIUM:
            # x^a * x^b / x^c -> x^{a+b-c}
            steps.append(TrustedLatex(f"$x^{{{a}+{b}-{c}}}$"))
        else:
            # (x^a)^b * x^c / x^d -> x^{a*b} * x^c / x^d -> x^{a*b+c-d}
            steps.append(TrustedLatex(f"$\\frac{{x^{{{a * b}}} \\cdot x^{{{c}}}}}{{x^{{{d}}}}}$"))
            steps.append(TrustedLatex(f"$x^{{{a * b}+{c}-{d}}}$"))
        steps.append(TrustedLatex(f"${answer}$"))

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Simplify: ${question}$"),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# T012c — Radical Simplify: sqrt(n)
# ---------------------------------------------------------------------------


@register_template
class RadicalSimplifyTemplate:
    topic = Topic.ALGEBRA
    subtopic = "radical_simplify"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            # Perfect square — answer is just an integer
            base = rng.randint(2, 5)
            radicand = base * base
            answer_expr = sympy.Integer(base)
        elif difficulty == Difficulty.MEDIUM:
            # a * sqrt(p) where p is small prime
            a = rng.randint(2, 6)
            p = rng.choice([2, 3, 5, 7])
            radicand = a * a * p
            answer_expr = a * sqrt(p)
        else:
            # a * sqrt(p) with larger numbers, or nested like sqrt(a * b * c)
            a = rng.randint(3, 10)
            p = rng.choice([2, 3, 5, 7, 11, 13])
            extra_square = rng.choice([1, 4, 9])
            radicand = a * a * p * extra_square
            # sympy.sqrt will auto-simplify
            answer_expr = sqrt(radicand)

        question = latex(sqrt(radicand, evaluate=False))
        answer = latex(answer_expr)

        # Build solution steps
        # Find largest perfect-square factor for the intermediate step
        sq_factor = sympy.integer_nthroot(radicand, 2)
        if sq_factor[1]:
            # radicand is a perfect square
            outer_sq = radicand
            inner = 1
        else:
            # Extract the largest perfect-square factor
            outer_val = 1
            inner_val = radicand
            for prime_factor in sympy.factorint(radicand):
                exp = sympy.factorint(radicand)[prime_factor]
                outer_val *= prime_factor ** (exp // 2)
                inner_val //= prime_factor ** (2 * (exp // 2))
            outer_sq = outer_val * outer_val
            inner = inner_val

        steps = [TrustedLatex(f"${question}$")]
        if inner > 1 and outer_sq > 1:
            factored = sympy.Mul(sympy.Integer(outer_sq), sympy.Integer(inner), evaluate=False)
            steps.append(TrustedLatex(f"${latex(sqrt(factored, evaluate=False))}$"))
        steps.append(TrustedLatex(f"${answer}$"))

        return GeneratedProblem(
            question_latex=TrustedLatex(f"Simplify: ${question}$"),
            answer_latex=TrustedLatex(f"${answer}$"),
            topic=Topic.ALGEBRA,
            difficulty=difficulty,
            subtopic=self.subtopic,
            solution_steps=tuple(steps),
        )
