"""Unit tests for deterministic algebra solution wording policies."""

from app.engine.solution_wording import explain_steps
from app.engine.types import Difficulty, TrustedLatex


def test_quadratic_formula_uses_specific_wording():
    steps = [
        TrustedLatex("$ax^2 + bx + c = 0$"),
        TrustedLatex("$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$"),
        TrustedLatex("$x = 1, \\; x = 2$"),
    ]

    explained = explain_steps(
        steps,
        subtopic="quadratic_formula",
        difficulty=Difficulty.EASY,
    )

    assert "Identify coefficients" in explained[0].value
    assert "Apply the quadratic formula" in explained[1].value
    assert "State both roots" in explained[2].value


def test_unknown_subtopic_falls_back_to_generic_wording():
    steps = [TrustedLatex("$x + 1 = 2$"), TrustedLatex("$x = 1$")]
    explained = explain_steps(
        steps,
        subtopic="unknown_subtopic",
        difficulty=Difficulty.EASY,
    )

    assert "Start from the given expression" in explained[0].value
    assert "State the final answer" in explained[1].value
