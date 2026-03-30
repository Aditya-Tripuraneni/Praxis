"""Minimal tests for algebra quadratic form conversion template."""

import random

import sympy

from app.engine.topics.algebra.templates import QuadraticFormConversionTemplate
from app.engine.types import Difficulty


class TestQuadraticFormConversionTemplate:
    def test_generates_across_difficulties(self):
        template = QuadraticFormConversionTemplate()
        for difficulty in Difficulty:
            problem = template.generate(difficulty, random.Random(42))
            assert problem.subtopic == "quadratic_form_conversion"
            assert problem.question_latex
            assert problem.answer_latex
            assert len(problem.solution_steps) >= 2

    def test_metadata_forms_are_equivalent(self):
        template = QuadraticFormConversionTemplate()
        problem = template.generate(Difficulty.HARD, random.Random(99))

        std = sympy.sympify(problem.metadata["standard_expr"])
        vtx = sympy.sympify(problem.metadata["vertex_expr"])
        fac = sympy.sympify(problem.metadata["factored_expr"])

        assert sympy.simplify(std - vtx) == 0
        assert sympy.simplify(std - fac) == 0
