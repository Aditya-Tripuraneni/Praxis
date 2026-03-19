"""Trigonometry topic templates for the ProblemGenerator math engine.

Templates: TrigEvalTemplate, InverseTrigTemplate,
           TrigSimplifyTemplate, TrigEquationTemplate
"""

from __future__ import annotations

import random

import sympy
from sympy import (
    Rational,
    Symbol,
    acos,
    asin,
    atan,
    cos,
    latex,
    pi,
    simplify,
    sin,
    sqrt,
    tan,
)

from app.engine.registry import register_template
from app.engine.types import Difficulty, GeneratedProblem, GenerationError, Topic, TrustedLatex

x = Symbol("x")

# Standard angles in [0, 2*pi)
STANDARD_ANGLES = [
    0,
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

# Trig function choices for evaluation
_TRIG_FUNCS = [
    ("\\sin", sin),
    ("\\cos", cos),
    ("\\tan", tan),
]


# ---------------------------------------------------------------------------
# 1. TrigEvalTemplate
# ---------------------------------------------------------------------------
@register_template
class TrigEvalTemplate:
    topic = Topic.TRIGONOMETRY
    subtopic = "trig_evaluation"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Evaluate sin/cos/tan at a standard angle."""
        if difficulty == Difficulty.EASY:
            # Angles: 0, pi/2, pi
            angle = rng.choice([sympy.Integer(0), pi / 2, pi])
            # Avoid tan at pi/2
            if angle == pi / 2:
                func_name, func = rng.choice([("\\sin", sin), ("\\cos", cos)])
            else:
                func_name, func = rng.choice(_TRIG_FUNCS)
        elif difficulty == Difficulty.MEDIUM:
            angle = rng.choice([pi / 6, pi / 4, pi / 3])
            func_name, func = rng.choice(_TRIG_FUNCS)
        else:
            # Hard: angles beyond 2*pi or negative
            base_angle = rng.choice(STANDARD_ANGLES[1:])  # exclude 0
            shift = rng.choice([-2 * pi, 2 * pi, 4 * pi, -4 * pi])
            angle = base_angle + shift
            func_name, func = rng.choice(_TRIG_FUNCS)
            # Avoid undefined tan at odd multiples of pi/2
            for _ in range(50):
                if not (func_name == "\\tan" and simplify(cos(angle)) == 0):
                    break
                func_name, func = rng.choice([("\\sin", sin), ("\\cos", cos)])
            else:
                raise GenerationError("Parameter sampling exhausted")

        answer_val = simplify(func(angle))
        angle_latex = latex(angle)

        question = f"Evaluate ${func_name}\\left({angle_latex}\\right)$."
        ans_ltx = latex(answer_val)

        if difficulty == Difficulty.HARD:
            base_ltx = latex(base_angle)
            steps: list[TrustedLatex] = [
                TrustedLatex(f"${func_name}\\left({angle_latex}\\right)$"),
                TrustedLatex(f"$= {func_name}\\left({base_ltx}\\right)$"),
                TrustedLatex(f"${ans_ltx}$"),
            ]
        else:
            steps = [
                TrustedLatex(f"${func_name}\\left({angle_latex}\\right)$"),
                TrustedLatex(f"${ans_ltx}$"),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${ans_ltx}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"function": func_name, "angle": angle_latex},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 2. InverseTrigTemplate
# ---------------------------------------------------------------------------
@register_template
class InverseTrigTemplate:
    topic = Topic.TRIGONOMETRY
    subtopic = "inverse_trig"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Find arcsin(v), arccos(v), arctan(v)."""
        if difficulty == Difficulty.EASY:
            # Values: 0, 1, -1
            value = rng.choice([sympy.Integer(0), sympy.Integer(1), sympy.Integer(-1)])
            inv_func_name, inv_func = rng.choice(
                [
                    ("\\arcsin", asin),
                    ("\\arccos", acos),
                    ("\\arctan", atan),
                ]
            )
        elif difficulty == Difficulty.MEDIUM:
            value = rng.choice(
                [
                    sqrt(2) / 2,
                    -sqrt(2) / 2,
                    sqrt(3) / 2,
                    -sqrt(3) / 2,
                    Rational(1, 2),
                    Rational(-1, 2),
                ]
            )
            inv_func_name, inv_func = rng.choice(
                [
                    ("\\arcsin", asin),
                    ("\\arccos", acos),
                ]
            )
        else:
            # Composition like sin(arccos(x)) with a known value
            # Pick a rational value v in [-1,1], compute sin(arccos(v)) = sqrt(1 - v^2)
            v_choices = [
                Rational(3, 5),
                Rational(4, 5),
                Rational(1, 2),
                Rational(0),
                Rational(-3, 5),
                Rational(-4, 5),
            ]
            v = rng.choice(v_choices)
            # Choose outer and inner functions
            combo = rng.choice(["sin_arccos", "cos_arcsin"])
            if combo == "sin_arccos":
                answer_val = simplify(sin(acos(v)))
                question = f"Evaluate $\\sin(\\arccos({latex(v)}))$."
                expr_ltx = f"\\sin(\\arccos({latex(v)}))"
            else:
                answer_val = simplify(cos(asin(v)))
                question = f"Evaluate $\\cos(\\arcsin({latex(v)}))$."
                expr_ltx = f"\\cos(\\arcsin({latex(v)}))"

            steps: list[TrustedLatex] = [
                TrustedLatex(f"${expr_ltx}$"),
                TrustedLatex(f"${latex(answer_val)}$"),
            ]
            return GeneratedProblem(
                question_latex=TrustedLatex(question),
                answer_latex=TrustedLatex(f"${latex(answer_val)}$"),
                topic=Topic.TRIGONOMETRY,
                difficulty=difficulty,
                subtopic=self.subtopic,
                metadata={"value": latex(v)},
                solution_steps=tuple(steps),
            )

        answer_val = simplify(inv_func(value))
        val_ltx = latex(value)
        question = f"Evaluate ${inv_func_name}\\left({val_ltx}\\right)$."
        steps = [
            TrustedLatex(f"${inv_func_name}\\left({val_ltx}\\right)$"),
            TrustedLatex(f"${latex(answer_val)}$"),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${latex(answer_val)}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"function": inv_func_name, "value": val_ltx},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 3. TrigSimplifyTemplate
# ---------------------------------------------------------------------------
@register_template
class TrigSimplifyTemplate:
    topic = Topic.TRIGONOMETRY
    subtopic = "trig_simplify"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Simplify a trig expression using identities."""
        t = Symbol("\\theta", real=True)

        if difficulty == Difficulty.EASY:
            # Pythagorean identity: sin^2 + cos^2 = 1
            # Ask to simplify sin^2(t) + cos^2(t) or variants
            variant = rng.choice(["basic", "rearranged"])
            if variant == "basic":
                expr = sin(t) ** 2 + cos(t) ** 2
                answer_val = sympy.Integer(1)
            else:
                # 1 - sin^2(t) = cos^2(t)
                expr = 1 - sin(t) ** 2
                answer_val = cos(t) ** 2
        elif difficulty == Difficulty.MEDIUM:
            # Double-angle formulas
            variant = rng.choice(["sin2", "cos2"])
            if variant == "sin2":
                # 2*sin(t)*cos(t) = sin(2t)
                expr = 2 * sin(t) * cos(t)
                answer_val = sin(2 * t)
            else:
                # cos^2(t) - sin^2(t) = cos(2t)
                expr = cos(t) ** 2 - sin(t) ** 2
                answer_val = cos(2 * t)
        else:
            # Sum/difference formulas
            variant = rng.choice(["sum_sin", "sum_cos"])
            a_angle = rng.choice([pi / 6, pi / 4, pi / 3])
            b_angle = rng.choice([pi / 6, pi / 4, pi / 3])
            if variant == "sum_sin":
                # sin(a)cos(b) + cos(a)sin(b) = sin(a+b)
                expr = sin(a_angle) * cos(b_angle) + cos(a_angle) * sin(b_angle)
                answer_val = simplify(sin(a_angle + b_angle))
            else:
                # cos(a)cos(b) - sin(a)sin(b) = cos(a+b)
                expr = cos(a_angle) * cos(b_angle) - sin(a_angle) * sin(b_angle)
                answer_val = simplify(cos(a_angle + b_angle))

        expr_ltx = latex(expr)
        ans_ltx = latex(answer_val)
        question = f"Simplify ${expr_ltx}$."
        steps = [
            TrustedLatex(f"${expr_ltx}$"),
            TrustedLatex(f"${ans_ltx}$"),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${ans_ltx}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"expression": expr_ltx},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# 4. TrigEquationTemplate
# ---------------------------------------------------------------------------
@register_template
class TrigEquationTemplate:
    topic = Topic.TRIGONOMETRY
    subtopic = "trig_equation"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        """Solve a trig equation on [0, 2*pi)."""
        if difficulty == Difficulty.EASY:
            # sin(x) = v or cos(x) = v for standard values
            func_choice = rng.choice(["sin", "cos"])
            if func_choice == "sin":
                # sin(x) = 0, 1, -1, 1/2, -1/2
                val = rng.choice(
                    [
                        sympy.Integer(0),
                        sympy.Integer(1),
                        sympy.Integer(-1),
                    ]
                )
                solutions = sorted([a for a in STANDARD_ANGLES if simplify(sin(a) - val) == 0])
                eq_ltx = f"\\sin(x) = {latex(val)}"
                question = f"Solve ${eq_ltx}$ on $[0, 2\\pi)$."
            else:
                val = rng.choice(
                    [
                        sympy.Integer(0),
                        sympy.Integer(1),
                        sympy.Integer(-1),
                    ]
                )
                solutions = sorted([a for a in STANDARD_ANGLES if simplify(cos(a) - val) == 0])
                eq_ltx = f"\\cos(x) = {latex(val)}"
                question = f"Solve ${eq_ltx}$ on $[0, 2\\pi)$."

        elif difficulty == Difficulty.MEDIUM:
            variant = rng.choice(["sin_factor", "cos_factor"])
            if variant == "sin_factor":
                eq_ltx = "2\\sin^{2}(x) - \\sin(x) = 0"
                question = f"Solve ${eq_ltx}$ on $[0, 2\\pi)$."
                solutions = [
                    sympy.Integer(0),
                    pi / 6,
                    5 * pi / 6,
                    pi,
                ]
            else:
                eq_ltx = "2\\cos^{2}(x) - \\cos(x) = 0"
                question = f"Solve ${eq_ltx}$ on $[0, 2\\pi)$."
                solutions = [
                    pi / 3,
                    pi / 2,
                    3 * pi / 2,
                    5 * pi / 3,
                ]
        else:
            variant = rng.choice(["sincos_1", "sincos_neg1"])
            if variant == "sincos_1":
                eq_ltx = "\\sin(x) + \\cos(x) = 1"
                question = f"Solve ${eq_ltx}$ on $[0, 2\\pi)$."
                solutions = [sympy.Integer(0), pi / 2]
            else:
                eq_ltx = "\\sin(x) + \\cos(x) = -1"
                question = f"Solve ${eq_ltx}$ on $[0, 2\\pi)$."
                solutions = [pi, 3 * pi / 2]

        sol_ltx = ", ".join(latex(s) for s in solutions)
        answer_str = f"x \\in \\{{{sol_ltx}\\}}"
        steps = [
            TrustedLatex(f"${eq_ltx}$"),
            TrustedLatex(f"${answer_str}$"),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question),
            answer_latex=TrustedLatex(f"${answer_str}$"),
            topic=Topic.TRIGONOMETRY,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"solutions": [str(s) for s in solutions]},
            solution_steps=tuple(steps),
        )
