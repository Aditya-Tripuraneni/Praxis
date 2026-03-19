"""Rational expression and equation templates.

Templates: RationalSimplifyTemplate, RationalAddSubTemplate,
           RationalMultiplyDivideTemplate, RationalEquationsTemplate,
           RationalExtraneousTemplate, ComplexFractionsTemplate

All use backward construction — the answer is generated first, then the
question is built from it by introducing common factors, splitting fractions,
or constructing equations with known solutions.
"""

from __future__ import annotations

import random

from sympy import (
    Eq,
    Rational,
    Symbol,
    cancel,
    expand,
    factor,
    latex,
    solve,
    together,
)

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _nonzero_int(rng: random.Random, lo: int, hi: int) -> int:
    """Random nonzero integer in [-hi, -lo] | [lo, hi]."""
    val = rng.randint(lo, hi)
    return val if rng.random() < 0.5 else -val


def _pos_int(rng: random.Random, lo: int, hi: int) -> int:
    return rng.randint(lo, hi)


def _distinct_ints(rng: random.Random, lo: int, hi: int, n: int) -> list[int]:
    """Return n distinct nonzero integers from [-hi,-lo] | [lo,hi]."""
    pool = list(range(lo, hi + 1)) + list(range(-hi, -lo + 1))
    if 0 in pool:
        pool.remove(0)
    rng.shuffle(pool)
    return pool[:n]


def _frac_latex(numer_expr, denom_expr) -> str:
    """Build LaTeX fraction from expanded numerator and denominator,
    preventing SymPy auto-cancellation."""
    return f"\\frac{{{latex(expand(numer_expr))}}}{{{latex(expand(denom_expr))}}}"


def _restrictions(denom_expr) -> list:
    """Find values that make the denominator zero."""
    return sorted(solve(denom_expr, x), key=lambda v: complex(v).real)


def _make_problem(
    question_text: str,
    answer_text: str,
    difficulty: Difficulty,
    subtopic: str,
    steps: list[TrustedLatex],
    metadata: dict | None = None,
) -> GeneratedProblem:
    return GeneratedProblem(
        question_latex=TrustedLatex(question_text),
        answer_latex=TrustedLatex(answer_text),
        topic=Topic.ALGEBRA,
        difficulty=difficulty,
        subtopic=subtopic,
        solution_steps=tuple(steps),
        metadata=metadata or {},
    )


# ---------------------------------------------------------------------------
# 1. RationalSimplifyTemplate
# ---------------------------------------------------------------------------
@register_template
class RationalSimplifyTemplate:
    """Factor and cancel common factors in a rational expression."""

    topic = Topic.ALGEBRA
    subtopic = "rational_simplify"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng, difficulty)
        elif difficulty == Difficulty.MEDIUM:
            return self._medium(rng, difficulty)
        else:
            return self._hard(rng, difficulty)

    def _easy(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Monomial common factor or difference of squares
        variant = rng.choice(["monomial", "diff_squares"])
        if variant == "monomial":
            a = _pos_int(rng, 2, 6)
            b = _pos_int(rng, 2, 6)
            n = rng.randint(1, 3)
            m = rng.randint(n + 1, n + 3)
            # Answer: (a/b) * x^(m-n)  but keep integer: use a*x^m / (b*x^n)
            numer = a * x**m
            denom = b * x**n
            answer_expr = cancel(numer / denom)
        else:
            # (x^2 - a^2)/(x - a) = x + a
            a = _pos_int(rng, 1, 6)
            numer = x**2 - a**2
            denom = x - a
            answer_expr = cancel(numer / denom)

        q_latex = f"Simplify: ${_frac_latex(numer, denom)}$"
        a_latex = f"${latex(answer_expr)}$"

        steps = [
            TrustedLatex(f"${_frac_latex(numer, denom)}$"),
            TrustedLatex(f"$= \\frac{{{latex(factor(numer))}}}{{{latex(factor(denom))}}}$"),
            TrustedLatex(f"$= {latex(answer_expr)}$"),
        ]

        return _make_problem(q_latex, a_latex, difficulty, self.subtopic, steps)

    def _medium(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Quadratic numerator, linear common factor
        # Answer = (x + a), common factor = (x + b)
        a, b = _distinct_ints(rng, 1, 8, 2)
        answer = x + a
        common = x + b
        numer = expand(answer * common)
        denom = expand(common)

        answer_expr = cancel(numer / denom)
        restrictions = _restrictions(denom)

        q_latex = f"Simplify: ${_frac_latex(numer, denom)}$"
        a_latex = f"${latex(answer_expr)}$"

        steps = [
            TrustedLatex(f"${_frac_latex(numer, denom)}$"),
            TrustedLatex(f"$= \\frac{{{latex(factor(numer))}}}{{{latex(factor(denom))}}}$"),
            TrustedLatex(f"$= {latex(answer_expr)}, \\quad x \\neq {latex(restrictions[0])}$"),
        ]

        return _make_problem(
            q_latex,
            a_latex,
            difficulty,
            self.subtopic,
            steps,
            metadata={"restrictions": [str(r) for r in restrictions]},
        )

    def _hard(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Both quadratic (or higher), common factor is linear or quadratic
        a, b, c = _distinct_ints(rng, 1, 8, 3)
        # Answer = (x + a)/(x + b), common = (x + c)
        ans_numer = x + a
        ans_denom = x + b
        common = x + c
        numer = expand(ans_numer * common)
        denom = expand(ans_denom * common)

        answer_expr = cancel(numer / denom)
        restrictions = _restrictions(expand(ans_denom * common))

        q_latex = f"Simplify: ${_frac_latex(numer, denom)}$"
        a_latex = f"${latex(answer_expr)}$"

        steps = [
            TrustedLatex(f"${_frac_latex(numer, denom)}$"),
            TrustedLatex(f"$= \\frac{{{latex(factor(numer))}}}{{{latex(factor(denom))}}}$"),
            TrustedLatex(f"$= {latex(answer_expr)}$"),
        ]

        return _make_problem(
            q_latex,
            a_latex,
            difficulty,
            self.subtopic,
            steps,
            metadata={"restrictions": [str(r) for r in restrictions]},
        )


# ---------------------------------------------------------------------------
# 2. RationalAddSubTemplate
# ---------------------------------------------------------------------------
@register_template
class RationalAddSubTemplate:
    """Add or subtract rational expressions."""

    topic = Topic.ALGEBRA
    subtopic = "rational_add_sub"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng, difficulty)
        elif difficulty == Difficulty.MEDIUM:
            return self._medium(rng, difficulty)
        else:
            return self._hard(rng, difficulty)

    def _build_add_sub_steps(
        self,
        p,
        q,
        d1,
        d2,
        op: str,
        answer,
        lcd,
    ) -> list[TrustedLatex]:
        """Build detailed solution steps for addition/subtraction."""
        d1_l, d2_l = latex(d1), latex(d2)
        sign = "+" if op == "+" else "-"
        q_inner = f"\\frac{{{latex(p)}}}{{{d1_l}}} {sign} \\frac{{{latex(q)}}}{{{d2_l}}}"

        # Step: rewrite each fraction with LCD
        term1 = expand(p * d2)
        term2 = expand(q * d1)
        rewritten = (
            f"\\frac{{{latex(p)}({d2_l})}}{{{latex(lcd)}}}"
            f" {sign} \\frac{{{latex(q)}({d1_l})}}{{{latex(lcd)}}}"
        )

        # Step: combine numerators
        if op == "+":
            combined_num = expand(term1 + term2)
        else:
            combined_num = expand(term1 - term2)
        combined = f"\\frac{{{latex(combined_num)}}}{{{latex(lcd)}}}"

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{LCD}} = {latex(lcd)}$"),
            TrustedLatex(f"$= {rewritten}$"),
            TrustedLatex(f"$= {combined}$"),
        ]
        # Only add simplification step if cancel changes the expression
        if answer != together(p / d1 + q / d2 if op == "+" else p / d1 - q / d2):
            steps.append(TrustedLatex(f"$= {latex(answer)}$"))
        else:
            steps.append(TrustedLatex(f"$= {latex(answer)}$"))
        return steps, q_inner

    def _easy(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        a, b = _distinct_ints(rng, 1, 5, 2)
        p = _pos_int(rng, 1, 5)
        q = _pos_int(rng, 1, 5)
        op = rng.choice(["+", "-"])

        d1 = x + a
        d2 = x + b
        lcd = expand(d1 * d2)

        if op == "+":
            answer = cancel(Rational(p) / d1 + Rational(q) / d2)
        else:
            answer = cancel(Rational(p) / d1 - Rational(q) / d2)

        steps, q_inner = self._build_add_sub_steps(p, q, d1, d2, op, answer, lcd)

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )

    def _medium(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        a, b = _distinct_ints(rng, 1, 8, 2)
        p = _nonzero_int(rng, 1, 6)
        q = _nonzero_int(rng, 1, 6)
        op = rng.choice(["+", "-"])

        d1 = x + a
        d2 = x + b
        lcd = expand(d1 * d2)

        if op == "+":
            answer = cancel(Rational(p) / d1 + Rational(q) / d2)
        else:
            answer = cancel(Rational(p) / d1 - Rational(q) / d2)

        steps, q_inner = self._build_add_sub_steps(p, q, d1, d2, op, answer, lcd)

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )

    def _hard(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Three fractions or quadratic denominators
        a, b, c = _distinct_ints(rng, 1, 6, 3)
        p = _nonzero_int(rng, 1, 5)
        q = _nonzero_int(rng, 1, 5)
        r = _nonzero_int(rng, 1, 5)

        d1 = x + a
        d2 = x + b
        d3 = x + c
        ops = [rng.choice(["+", "-"]), rng.choice(["+", "-"])]

        f1 = Rational(p) / d1
        f2 = Rational(q) / d2
        f3 = Rational(r) / d3

        if ops[0] == "+":
            partial = f1 + f2
        else:
            partial = f1 - f2
        if ops[1] == "+":
            expr = partial + f3
        else:
            expr = partial - f3

        answer = cancel(expr)
        lcd = expand(d1 * d2 * d3)
        q_inner = (
            f"\\frac{{{latex(p)}}}{{{latex(d1)}}} {ops[0]} "
            f"\\frac{{{latex(q)}}}{{{latex(d2)}}} {ops[1]} "
            f"\\frac{{{latex(r)}}}{{{latex(d3)}}}"
        )

        # Rewrite each fraction with LCD
        t1_num = expand(p * d2 * d3)
        t2_num = expand(q * d1 * d3)
        t3_num = expand(r * d1 * d2)
        lcd_l = latex(lcd)
        rewritten = (
            f"\\frac{{{latex(t1_num)}}}{{{lcd_l}}} {ops[0]} "
            f"\\frac{{{latex(t2_num)}}}{{{lcd_l}}} {ops[1]} "
            f"\\frac{{{latex(t3_num)}}}{{{lcd_l}}}"
        )

        # Combine numerators
        if ops[0] == "+":
            combined = t1_num + t2_num
        else:
            combined = t1_num - t2_num
        if ops[1] == "+":
            combined = combined + t3_num
        else:
            combined = combined - t3_num
        combined = expand(combined)

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{LCD}} = {lcd_l}$"),
            TrustedLatex(f"$= {rewritten}$"),
            TrustedLatex(f"$= \\frac{{{latex(combined)}}}{{{lcd_l}}}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )


# ---------------------------------------------------------------------------
# 3. RationalMultiplyDivideTemplate
# ---------------------------------------------------------------------------
@register_template
class RationalMultiplyDivideTemplate:
    """Multiply or divide rational expressions."""

    topic = Topic.ALGEBRA
    subtopic = "rational_multiply_divide"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng, difficulty)
        elif difficulty == Difficulty.MEDIUM:
            return self._medium(rng, difficulty)
        else:
            return self._hard(rng, difficulty)

    def _easy(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Monomial × monomial with cancellation, ensure non-trivial answer
        for _ in range(50):
            a = _pos_int(rng, 2, 6)
            b = _pos_int(rng, 2, 6)
            c = _pos_int(rng, 2, 6)
            d = _pos_int(rng, 2, 6)
            if a * c != b * d:
                break
        n1 = a * x
        d1 = Rational(b)
        n2 = Rational(c)
        d2 = d * x

        is_div = rng.choice([True, False])
        if is_div:
            answer = cancel((n1 / d1) / (d2 / n2))
            n1_l, d1_l = latex(n1), latex(d1)
            d2_l, n2_l = latex(d2), latex(n2)
            q_inner = f"\\frac{{{n1_l}}}{{{d1_l}}} \\div \\frac{{{d2_l}}}{{{n2_l}}}"
            op_step = f"$= \\frac{{{n1_l}}}{{{d1_l}}} \\cdot \\frac{{{n2_l}}}{{{d2_l}}}$"
        else:
            answer = cancel((n1 / d1) * (n2 / d2))
            n1_l, d1_l = latex(n1), latex(d1)
            n2_l, d2_l = latex(n2), latex(d2)
            q_inner = f"\\frac{{{n1_l}}}{{{d1_l}}} \\cdot \\frac{{{n2_l}}}{{{d2_l}}}"
            op_step = None

        steps: list[TrustedLatex] = [TrustedLatex(f"${q_inner}$")]
        if op_step:
            steps.append(TrustedLatex(op_step))
        steps.append(TrustedLatex(f"$= {latex(answer)}$"))

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )

    def _medium(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Linear factors cancel across fractions
        a, b, c = _distinct_ints(rng, 1, 7, 3)
        # (x+a)/(x+b) · (x+b)/(x+c) = (x+a)/(x+c)
        n1, d1 = x + a, x + b
        n2, d2 = x + b, x + c

        is_div = rng.choice([True, False])
        if is_div:
            # (x+a)/(x+b) ÷ (x+c)/(x+b) = (x+a)/(x+b) · (x+b)/(x+c) = (x+a)/(x+c)
            presented_n2 = x + c
            presented_d2 = x + b
            answer = cancel((n1 / d1) / (presented_n2 / presented_d2))
            q_inner = (
                f"\\frac{{{latex(n1)}}}{{{latex(d1)}}} \\div"
                f" \\frac{{{latex(presented_n2)}}}{{{latex(presented_d2)}}}"
            )
        else:
            answer = cancel((n1 / d1) * (n2 / d2))
            q_inner = (
                f"\\frac{{{latex(n1)}}}{{{latex(d1)}}} \\cdot \\frac{{{latex(n2)}}}{{{latex(d2)}}}"
            )

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )

    def _hard(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Quadratic expressions that need factoring to see cancellations
        a, b, c, d = _distinct_ints(rng, 1, 6, 4)
        # frac1 = (x+a)(x+b) / (x+c)(x+b)  ·  frac2 = (x+c)(x+d) / (x+a)(x+d) = 1
        # Make it non-trivial by adjusting
        n1 = expand((x + a) * (x + b))
        d1 = expand((x + c) * (x + b))
        n2 = expand((x + c))
        d2 = expand((x + a))
        # Product: (x+a)(x+b)(x+c) / ((x+c)(x+b)(x+a)) = 1, too trivial
        # Better: leave one factor uncancelled
        n1 = expand((x + a) * (x + b))
        d1 = expand((x + c) * (x + d))
        n2 = expand((x + c))
        d2 = expand((x + b))
        # Product = (x+a)(x+b)(x+c) / ((x+c)(x+d)(x+b)) = (x+a)/(x+d)
        answer = cancel((n1 * n2) / (d1 * d2))

        q_inner = (
            f"\\frac{{{latex(n1)}}}{{{latex(d1)}}} \\cdot \\frac{{{latex(n2)}}}{{{latex(d2)}}}"
        )

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(
                f"$= \\frac{{{latex(factor(n1))} \\cdot {latex(factor(n2))}}}"
                f"{{{latex(factor(d1))} \\cdot {latex(factor(d2))}}}$"
            ),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )


# ---------------------------------------------------------------------------
# 4. RationalEquationsTemplate
# ---------------------------------------------------------------------------
@register_template
class RationalEquationsTemplate:
    """Solve rational equations by clearing fractions."""

    topic = Topic.ALGEBRA
    subtopic = "rational_equations"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng, difficulty)
        elif difficulty == Difficulty.MEDIUM:
            return self._medium(rng, difficulty)
        else:
            return self._hard(rng, difficulty)

    def _easy(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Proportion: a/x = b/c, solution x = ac/b
        a = _pos_int(rng, 2, 8)
        c = _pos_int(rng, 2, 6)
        b = _pos_int(rng, 2, 6)
        # Ensure integer solution
        x_val = a * c
        # a/x = b/c => x = ac/b, want integer => ac divisible by b
        for _ in range(50):
            if (a * c) % b == 0:
                break
            b = _pos_int(rng, 2, 6)
        x_val = Rational(a * c, b)

        q_inner = f"\\frac{{{a}}}{{{latex(x)}}} = \\frac{{{b}}}{{{c}}}"
        answer = x_val

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{Cross multiply: }} {a} \\cdot {c} = {b} \\cdot x$"),
            TrustedLatex(f"$x = {latex(answer)}$"),
        ]

        return _make_problem(
            f"Solve: ${q_inner}$",
            f"$x = {latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
            metadata={"solution": str(answer)},
        )

    def _medium(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Two rational terms, quadratic after clearing, two valid solutions
        # a/(x+p) + b/(x+q) = c, pick solutions first
        x1, x2 = _distinct_ints(rng, 1, 8, 2)
        p = _nonzero_int(rng, 1, 6)
        # Ensure x1+p != 0 and x2+p != 0
        for _ in range(50):
            if x1 + p != 0 and x2 + p != 0:
                break
            p = _nonzero_int(rng, 1, 6)

        # k/x + x = n => k + x^2 = nx => x^2 - nx + k = 0, roots x1, x2
        n_coeff = x1 + x2
        k = x1 * x2
        if k == 0:
            k = 1
            x1, x2 = 2, 3
            n_coeff = 5
            k = 6

        q_inner = f"\\frac{{{k}}}{{{latex(x)}}} + {latex(x)} = {n_coeff}"
        answer_str = f"x = {latex(x1)}, \\; x = {latex(x2)}"

        # Use SymPy for clean polynomial formatting
        poly = x**2 - n_coeff * x + k
        poly_eq = latex(Eq(poly, 0))

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{Multiply by }} x: {k} + x^2 = {n_coeff}x$"),
            TrustedLatex(f"${poly_eq}$"),
            TrustedLatex(f"${latex(factor(poly))} = 0$"),
            TrustedLatex(f"${answer_str}$"),
        ]

        return _make_problem(
            f"Solve: ${q_inner}$",
            f"${answer_str}$",
            difficulty,
            self.subtopic,
            steps,
            metadata={"solutions": [str(x1), str(x2)]},
        )

    def _hard(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Two rational terms with different linear denominators
        # a/(x+p) + b/(x+q) = c, clearing gives quadratic
        p, q = _distinct_ints(rng, 1, 6, 2)
        x_val = rng.randint(1, 10)
        # Ensure x_val + p != 0 and x_val + q != 0
        for _ in range(50):
            if x_val + p != 0 and x_val + q != 0:
                break
            x_val = rng.randint(1, 10)

        a_c = _nonzero_int(rng, 1, 8)
        # Compute c from: a/(x_val+p) + b/(x_val+q) = c
        b_c = _nonzero_int(rng, 1, 8)
        c_val = Rational(a_c, x_val + p) + Rational(b_c, x_val + q)

        d1 = x + p
        d2 = x + q
        lhs = Rational(a_c) / d1 + Rational(b_c) / d2
        solutions = solve(Eq(lhs, c_val), x)
        solutions = [s for s in solutions if s + p != 0 and s + q != 0]

        if not solutions:
            raise GenerationError("No valid solutions for rational equation")

        q_inner = (
            f"\\frac{{{a_c}}}{{{latex(d1)}}} + \\frac{{{b_c}}}{{{latex(d2)}}} = {latex(c_val)}"
        )
        answer_str = ", \\; ".join(f"x = {latex(s)}" for s in sorted(solutions))

        lcd = expand(d1 * d2)
        # Show the cleared equation: a_c*(d2) + b_c*(d1) = c_val * lcd
        lhs_cleared = expand(a_c * d2 + b_c * d1)
        rhs_cleared = expand(c_val * lcd)
        # Move to standard form
        poly = expand(lhs_cleared - rhs_cleared)
        poly_eq = latex(Eq(poly, 0))

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{LCD}} = {latex(lcd)}$"),
            TrustedLatex(
                f"$\\text{{Multiply: }}"
                f" {a_c}({latex(d2)}) + {b_c}({latex(d1)})"
                f" = {latex(c_val)} \\cdot ({latex(lcd)})$"
            ),
            TrustedLatex(f"${latex(lhs_cleared)} = {latex(rhs_cleared)}$"),
            TrustedLatex(f"${poly_eq}$"),
            TrustedLatex(f"${answer_str}$"),
        ]

        return _make_problem(
            f"Solve: ${q_inner}$",
            f"${answer_str}$",
            difficulty,
            self.subtopic,
            steps,
            metadata={"solutions": [str(s) for s in solutions]},
        )


# ---------------------------------------------------------------------------
# 5. RationalExtraneousTemplate
# ---------------------------------------------------------------------------
@register_template
class RationalExtraneousTemplate:
    """Rational equations where one solution is extraneous.

    Construction: f(x)/(x - b) = k
    where f(x) = (x - b)[c(x - a) + k], so:
      - Cross-multiplying gives roots x = a (valid) and x = b (extraneous)
      - x = b zeros the denominator (x - b)
    """

    topic = Topic.ALGEBRA
    subtopic = "rational_extraneous"
    supported_difficulties = [Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng, difficulty)
        else:
            return self._hard(rng, difficulty)

    def _medium(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # One valid + one extraneous, small coefficients
        valid = rng.randint(3, 8)
        extra = rng.randint(1, 4)
        for _ in range(50):
            if extra != valid:
                break
            extra = rng.randint(1, 4)
        c = _pos_int(rng, 1, 3)
        k = c * (valid - extra) + c * (valid - extra)  # just use k = c*(valid - extra) + k...
        # f(x) = (x - extra)[c(x - valid) + k]
        # For the equation to work: f(x)/(x-extra) = k
        # => c(x - valid) + k = k => c(x-valid) = 0 => x = valid
        # Cross-multiply: f(x) = k(x - extra)
        # f(x) - k(x-extra) = (x-extra)[c(x-valid)+k] - k(x-extra) = (x-extra)[c(x-valid)+k-k]
        #                    = (x-extra) * c * (x-valid) = 0
        # Roots: x = extra (extraneous) and x = valid. Perfect!
        k = _pos_int(rng, 1, 5)
        f_x = (x - extra) * (c * (x - valid) + k)
        f_expanded = expand(f_x)
        denom = x - extra

        # Equation: f(x)/(x-extra) = k
        q_inner = f"{_frac_latex(f_expanded, denom)} = {k}"

        # Cross multiply: f(x) = k(x-extra) => f(x) - k(x-extra) = 0
        cleared = expand(f_expanded - k * (x - extra))
        all_roots = solve(cleared, x)

        valid_roots = [r for r in all_roots if r != extra]
        extra_roots = [r for r in all_roots if r == extra]

        if not valid_roots or not extra_roots:
            raise GenerationError("Extraneous construction failed")

        answer_str = ", \\; ".join(f"x = {latex(r)}" for r in sorted(valid_roots))

        denom_l = latex(denom)
        f_exp_l = latex(f_expanded)
        extra_l = latex(extra)
        valid_l = latex(valid_roots[0])
        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{Multiply by }} ({denom_l}): {f_exp_l} = {k}({denom_l})$"),
            TrustedLatex(f"${latex(Eq(cleared, 0))}$"),
            TrustedLatex(f"$\\text{{Solutions: }} x = {extra_l} \\text{{ and }} x = {valid_l}$"),
            TrustedLatex(f"$x = {extra_l} \\text{{ is extraneous}}$"),
            TrustedLatex(f"${answer_str}$"),
        ]

        return _make_problem(
            f"Solve (check for extraneous): ${q_inner}$",
            f"${answer_str}$",
            difficulty,
            self.subtopic,
            steps,
            metadata={
                "valid": [str(r) for r in valid_roots],
                "extraneous": [str(r) for r in extra_roots],
            },
        )

    def _hard(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Two denominators, one extraneous from each potential restriction
        # a/(x - p) + b/(x - q) = c, where one root equals p or q
        p, q = _distinct_ints(rng, 1, 6, 2)
        p, q = abs(p), abs(q)
        valid = rng.randint(p + q + 1, p + q + 8)
        # Make sure valid != p and valid != q
        for _ in range(50):
            if valid != p and valid != q:
                break
            valid = rng.randint(1, 15)

        # We want x = p to be extraneous (zeros first denom)
        # Build: a/(x-p) + b/(x-q) = c
        # Clear: a(x-q) + b(x-p) = c(x-p)(x-q)
        # This is quadratic in x. We want roots: valid and p.
        # (x - valid)(x - p) = 0 => x^2 - (valid+p)x + valid*p
        # Equate: c(x-p)(x-q) - a(x-q) - b(x-p) = (x-valid)(x-p) * something
        # Simpler: just use the f(x)/(x-b)=k pattern with larger coefficients
        extra = p
        c_v = _pos_int(rng, 1, 4)
        k = _pos_int(rng, 2, 8)
        f_x = (x - extra) * (c_v * (x - valid) + k)
        f_expanded = expand(f_x)
        denom = x - extra

        q_inner = f"{_frac_latex(f_expanded, denom)} = {k}"
        cleared = expand(f_expanded - k * (x - extra))
        all_roots = solve(cleared, x)

        valid_roots = [r for r in all_roots if r != extra]
        extra_roots = [r for r in all_roots if r == extra]

        if not valid_roots or not extra_roots:
            raise GenerationError("Extraneous construction failed")

        answer_str = ", \\; ".join(f"x = {latex(r)}" for r in sorted(valid_roots))

        denom_l = latex(denom)
        f_exp_l = latex(f_expanded)
        extra_l = latex(extra)
        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{Multiply by }} ({denom_l}): {f_exp_l} = {k}({denom_l})$"),
            TrustedLatex(f"${latex(Eq(cleared, 0))}$"),
            TrustedLatex(f"$\\text{{Check: }} x = {extra_l} \\text{{ — extraneous}}$"),
            TrustedLatex(f"${answer_str}$"),
        ]

        return _make_problem(
            f"Solve (check for extraneous solutions): ${q_inner}$",
            f"${answer_str}$",
            difficulty,
            self.subtopic,
            steps,
            metadata={
                "valid": [str(r) for r in valid_roots],
                "extraneous": [str(r) for r in extra_roots],
            },
        )


# ---------------------------------------------------------------------------
# 6. ComplexFractionsTemplate
# ---------------------------------------------------------------------------
@register_template
class ComplexFractionsTemplate:
    """Simplify complex fractions (fractions within fractions)."""

    topic = Topic.ALGEBRA
    subtopic = "complex_fractions"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng, difficulty)
        elif difficulty == Difficulty.MEDIUM:
            return self._medium(rng, difficulty)
        else:
            return self._hard(rng, difficulty)

    def _easy(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # (a/b) / (c/d) = ad/bc or (x/a) / (x/b) = b/a
        variant = rng.choice(["numeric", "variable"])
        if variant == "numeric":
            for _ in range(50):
                a = _pos_int(rng, 1, 6)
                b = _pos_int(rng, 2, 6)
                c = _pos_int(rng, 1, 6)
                d = _pos_int(rng, 2, 6)
                if a * d != b * c:  # ensure answer != 1
                    break
            answer = Rational(a * d, b * c)
            q_inner = f"\\dfrac{{\\dfrac{{{a}}}{{{b}}}}}{{\\dfrac{{{c}}}{{{d}}}}}"
        else:
            for _ in range(50):
                a = _pos_int(rng, 2, 6)
                b = _pos_int(rng, 2, 6)
                if a != b:  # ensure answer != 1
                    break
            answer = Rational(b, a)
            q_inner = f"\\dfrac{{\\dfrac{{{latex(x)}}}{{{a}}}}}{{\\dfrac{{{latex(x)}}}{{{b}}}}}"

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )

    def _medium(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # Two variants for more diversity
        variant = rng.choice(["add_over_single", "coeff_over_coeff"])
        a = _pos_int(rng, 1, 6)

        if variant == "add_over_single":
            # (p/x + 1/a) / (1/x)  = p + x/a
            p = _pos_int(rng, 1, 5)
            numer_inner = Rational(p) / x + Rational(1, a)
            denom_inner = Rational(1) / x
            answer = cancel(numer_inner / denom_inner)
            q_inner = (
                f"\\dfrac{{\\dfrac{{{p}}}{{{latex(x)}}} + \\dfrac{{1}}{{{a}}}}}"
                f"{{\\dfrac{{1}}{{{latex(x)}}}}}"
            )
            # After multiplying by x: (p + x/a) / 1
            numer_mult = latex(expand(p + x / a))
            after_mult = f"\\frac{{{numer_mult}}}{{1}}"
        else:
            # (a/x) / (b/x + 1) where b != a
            b = _pos_int(rng, 1, 5)
            for _ in range(20):
                if b != a:
                    break
                b = _pos_int(rng, 1, 5)
            numer_inner = Rational(a) / x
            denom_inner = Rational(b) / x + 1
            answer = cancel(numer_inner / denom_inner)
            q_inner = (
                f"\\dfrac{{\\dfrac{{{a}}}{{{latex(x)}}}}}{{\\dfrac{{{b}}}{{{latex(x)}}} + 1}}"
            )
            # After multiplying by x: a / (b + x)
            after_mult = f"\\frac{{{a}}}{{{latex(b + x)}}}"

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{Multiply num. and denom. by }} {latex(x)}$"),
            TrustedLatex(f"$= {after_mult}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )

    def _hard(self, rng: random.Random, difficulty: Difficulty) -> GeneratedProblem:
        # (1/x - 1/y) / (1/x + 1/y) type with x variable and y = constant
        a = _pos_int(rng, 1, 6)
        op_n = rng.choice(["+", "-"])
        op_d = "+" if op_n == "-" else "-"

        if op_n == "+":
            numer_inner = Rational(1) / x + Rational(1, a)
            n_latex = f"\\dfrac{{1}}{{{latex(x)}}} + \\dfrac{{1}}{{{a}}}"
        else:
            numer_inner = Rational(1) / x - Rational(1, a)
            n_latex = f"\\dfrac{{1}}{{{latex(x)}}} - \\dfrac{{1}}{{{a}}}"

        if op_d == "+":
            denom_inner = Rational(1) / x + Rational(1, a)
            d_latex = f"\\dfrac{{1}}{{{latex(x)}}} + \\dfrac{{1}}{{{a}}}"
        else:
            denom_inner = Rational(1) / x - Rational(1, a)
            d_latex = f"\\dfrac{{1}}{{{latex(x)}}} - \\dfrac{{1}}{{{a}}}"

        answer = cancel(numer_inner / denom_inner)
        q_inner = f"\\dfrac{{{n_latex}}}{{{d_latex}}}"
        lcd_val = a * x

        # Show what the num and denom become after multiplying by lcd
        numer_mult = expand(numer_inner * lcd_val)
        denom_mult = expand(denom_inner * lcd_val)
        after_mult = f"\\frac{{{latex(numer_mult)}}}{{{latex(denom_mult)}}}"

        steps = [
            TrustedLatex(f"${q_inner}$"),
            TrustedLatex(f"$\\text{{Multiply num. and denom. by }} {latex(lcd_val)}$"),
            TrustedLatex(f"$= {after_mult}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return _make_problem(
            f"Simplify: ${q_inner}$",
            f"${latex(answer)}$",
            difficulty,
            self.subtopic,
            steps,
        )
