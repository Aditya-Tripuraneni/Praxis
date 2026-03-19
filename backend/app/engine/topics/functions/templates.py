"""Functions topic templates for the ProblemGenerator math engine.

Templates: FunctionEvalTemplate, FunctionCompositionTemplate,
           DomainTemplate, InverseFunctionTemplate
"""

from __future__ import annotations

import random

import sympy
from sympy import Rational, Symbol, latex, simplify, sqrt

from app.engine.registry import register_template
from app.engine.types import Difficulty, GeneratedProblem, GenerationError, Topic, TrustedLatex

x = Symbol("x")


# ---------------------------------------------------------------------------
# 1. FunctionEvalTemplate
# ---------------------------------------------------------------------------
@register_template
class FunctionEvalTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "function_evaluation"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Given f(x), find f(a).  Backward: pick answer first."""
        if difficulty == Difficulty.EASY:
            # Linear f(x) = mx + b, small integers
            m = rng.randint(1, 5)
            b = rng.randint(0, 5)
            a = rng.randint(1, 5)
            f_expr = m * x + b
            answer = m * a + b
        elif difficulty == Difficulty.MEDIUM:
            # Quadratic f(x) = ax^2 + bx + c
            c_a = rng.randint(1, 5)
            c_b = rng.randint(-10, 10)
            c_c = rng.randint(-10, 10)
            a = rng.randint(-5, 5)
            f_expr = c_a * x**2 + c_b * x + c_c
            answer = c_a * a**2 + c_b * a + c_c
        else:
            # Rational f(x) = (px + q) / (rx + s), ensure no division by zero at a
            p = rng.randint(1, 10)
            q = rng.randint(-10, 10)
            r = rng.randint(1, 5)
            s = rng.randint(1, 15)
            # Pick a such that r*a + s != 0
            a = rng.choice([v for v in range(-5, 6) if r * v + s != 0])
            f_expr = (p * x + q) / (r * x + s)
            answer = Rational(p * a + q, r * a + s)

        answer_val = sympy.nsimplify(answer)
        question = f"Let $f(x) = {latex(f_expr)}$. Find $f({a})$."

        steps = [
            TrustedLatex(f"$f(x) = {latex(f_expr)}$"),
            TrustedLatex(f"$f({a}) = {latex(answer_val)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${latex(answer_val)}$"),
            topic=Topic.FUNCTIONS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"function": latex(f_expr), "input": a},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 2. FunctionCompositionTemplate
# ---------------------------------------------------------------------------
@register_template
class FunctionCompositionTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "function_composition"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Find f(g(a)).  Backward: pick answer, build g then f."""
        if difficulty == Difficulty.EASY:
            # f linear, g linear, small integers
            answer = rng.randint(1, 5)
            # g(a) = intermediate
            a = rng.randint(1, 5)
            g_m = rng.randint(1, 3)
            g_b = rng.randint(0, 3)
            intermediate = g_m * a + g_b
            # f such that f(intermediate) = answer => f(x) = x + (answer - intermediate)
            f_b = answer - intermediate
            f_expr = x + f_b
            g_expr = g_m * x + g_b
        elif difficulty == Difficulty.MEDIUM:
            answer = rng.randint(5, 15)
            a = rng.randint(1, 5)
            # g(x) = x^2 + c
            g_c = rng.randint(-3, 3)
            intermediate = a**2 + g_c
            # f(x) = mx + b, solve m*intermediate + b = answer
            f_m = rng.randint(1, 3)
            f_b = answer - f_m * intermediate
            f_expr = f_m * x + f_b
            g_expr = x**2 + g_c
        else:
            answer = rng.randint(10, 30)
            a = rng.randint(1, 4)
            # g(x) = x^2 + px + q
            g_p = rng.randint(-3, 3)
            g_q = rng.randint(-3, 3)
            intermediate = a**2 + g_p * a + g_q
            # f(x) = x^2 + r => r = answer - intermediate^2
            f_r = answer - intermediate**2
            f_expr = x**2 + f_r
            g_expr = x**2 + g_p * x + g_q

        question = f"Let $f(x) = {latex(f_expr)}$ and $g(x) = {latex(g_expr)}$. Find $f(g({a}))$."

        steps = [
            TrustedLatex(f"$f(x) = {latex(f_expr)}, \\quad g(x) = {latex(g_expr)}$"),
            TrustedLatex(f"$g({a}) = {latex(intermediate)}$"),
            TrustedLatex(f"$f({latex(intermediate)}) = {latex(sympy.Integer(answer))}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${latex(sympy.Integer(answer))}$"),
            topic=Topic.FUNCTIONS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"f": latex(f_expr), "g": latex(g_expr), "input": a},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 3. Domain templates moved to domain.py (5 specialized classes)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 4. InverseFunctionTemplate
# ---------------------------------------------------------------------------
@register_template
class InverseFunctionTemplate:
    topic = Topic.FUNCTIONS
    subtopic = "inverse_function"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Find f^{-1}(x).  Backward: build invertible f, compute inverse."""
        if difficulty == Difficulty.EASY:
            # f(x) = mx + b  => f^{-1}(x) = (x - b)/m
            m = rng.randint(2, 5)
            b = rng.randint(1, 5)
            f_expr = m * x + b
            inv_expr = (x - b) / sympy.Integer(m)
        elif difficulty == Difficulty.MEDIUM:
            # f(x) = (ax + b)/(cx + d)  =>  inverse by solving y = (ax+b)/(cx+d) for x
            a_c = rng.randint(1, 5)
            b_c = rng.randint(1, 5)
            c_c = rng.randint(1, 3)
            d_c = rng.randint(1, 5)
            # Ensure ad - bc != 0 for invertibility
            for _ in range(50):
                if a_c * d_c - b_c * c_c != 0:
                    break
                d_c = rng.randint(1, 5)
            else:
                raise GenerationError("Parameter sampling exhausted")
            f_expr = (a_c * x + b_c) / (c_c * x + d_c)
            # Inverse: y(cx + d) = ax + b => ycx + yd = ax + b => x(yc - a) = b - yd
            # x = (b - yd)/(yc - a)  => replace y with x
            # f^{-1}(x) = (dx - b) / (a - cx)   [after negation]
            inv_expr = simplify((d_c * x - b_c) / (-c_c * x + a_c))
        else:
            # f(x) = x^2 + c, x >= 0  =>  f^{-1}(x) = sqrt(x - c)
            c = rng.randint(1, 10)
            f_expr = x**2 + c
            inv_expr = sqrt(x - c)

        question_f = latex(f_expr)
        if difficulty == Difficulty.HARD:
            question = f"Let $f(x) = {question_f}$ for $x \\geq 0$. Find $f^{{-1}}(x)$."
        else:
            question = f"Let $f(x) = {question_f}$. Find $f^{{-1}}(x)$."

        # Build solution steps per difficulty
        y = Symbol("y")
        if difficulty == Difficulty.EASY:
            steps = [
                TrustedLatex(f"$y = {latex(f_expr)}$"),
                TrustedLatex(f"${latex(y - b)} = {latex(m * x)}$"),
                TrustedLatex(f"$f^{{-1}}(x) = {latex(inv_expr)}$"),
            ]
        elif difficulty == Difficulty.MEDIUM:
            cross_lhs = y * (c_c * x + d_c)
            cross_rhs = a_c * x + b_c
            x_in_y = (d_c * y - b_c) / (-c_c * y + a_c)
            steps = [
                TrustedLatex(f"$y = {latex(f_expr)}$"),
                TrustedLatex(f"${latex(cross_lhs)} = {latex(cross_rhs)}$"),
                TrustedLatex(f"$x = {latex(x_in_y)}$"),
                TrustedLatex(f"$f^{{-1}}(x) = {latex(inv_expr)}$"),
            ]
        else:
            steps = [
                TrustedLatex(f"$y = {latex(f_expr)}$"),
                TrustedLatex(f"${latex(y - c)} = x^2$"),
                TrustedLatex(f"$f^{{-1}}(x) = {latex(inv_expr)}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"$f^{{-1}}(x) = {latex(inv_expr)}$"),
            topic=Topic.FUNCTIONS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"f": question_f, "inverse": latex(inv_expr)},
            solution_steps=tuple(steps),
        )
