"""Deterministic wording policies for step-by-step math solutions.

This module keeps explanation text separate from template math generation.
"""

from __future__ import annotations

from app.engine.types import Difficulty, TrustedLatex


class _Policy:
    __slots__ = ("first", "second", "middle", "last")

    def __init__(self, first: str, second: str, middle: str, last: str) -> None:
        self.first = first
        self.second = second
        self.middle = middle
        self.last = last


_DEFAULT_POLICY = _Policy(
    first="Start from the given expression",
    second="Apply an equivalent operation",
    middle="Simplify the expression",
    last="State the final answer",
)


_ALGEBRA_POLICIES: dict[str, _Policy] = {
    "linear_equations": _Policy(
        first="Write the original equation",
        second="Isolate the variable term",
        middle="Simplify both sides",
        last="Solve for x",
    ),
    "two_step_linear": _Policy(
        first="Write the original equation",
        second="Collect like terms",
        middle="Simplify both sides",
        last="Solve for x",
    ),
    "quadratic_factoring": _Policy(
        first="Write in standard form",
        second="Factor the quadratic",
        middle="Use the zero-product rule",
        last="State both roots",
    ),
    "quadratic_formula": _Policy(
        first="Identify coefficients",
        second="Apply the quadratic formula",
        middle="Simplify the radical expression",
        last="State both roots",
    ),
    "quadratic_form_conversion": _Policy(
        first="Identify the source form",
        second="Apply the conversion rule",
        middle="Simplify into target form",
        last="State the target form",
    ),
    "polynomial_add_sub": _Policy(
        first="Write the full expression",
        second="Combine like terms",
        middle="Simplify term by term",
        last="State the simplified polynomial",
    ),
    "polynomial_multiply": _Policy(
        first="Set up distribution",
        second="Expand each product",
        middle="Combine like terms",
        last="State the expanded polynomial",
    ),
    "systems_of_equations": _Policy(
        first="Write both equations",
        second="Eliminate one variable",
        middle="Back-substitute to solve",
        last="State the ordered pair",
    ),
    "exponent_rules": _Policy(
        first="Write the expression",
        second="Apply exponent rules",
        middle="Simplify the exponent",
        last="State the simplified power",
    ),
    "radical_simplify": _Policy(
        first="Write the radical expression",
        second="Extract perfect-square factors",
        middle="Simplify remaining radical",
        last="State the simplified radical",
    ),
    "rational_simplify": _Policy(
        first="Write the rational expression",
        second="Factor numerator and denominator",
        middle="Cancel common factors",
        last="State the simplified result",
    ),
    "rational_add_sub": _Policy(
        first="Write the rational expression",
        second="Use the least common denominator",
        middle="Combine and simplify",
        last="State the simplified result",
    ),
    "rational_multiply_divide": _Policy(
        first="Write the rational expression",
        second="Rewrite and factor as needed",
        middle="Cancel common factors",
        last="State the simplified result",
    ),
    "rational_equations": _Policy(
        first="Write the rational equation",
        second="Clear denominators",
        middle="Solve the resulting equation",
        last="State valid solution(s)",
    ),
    "rational_extraneous": _Policy(
        first="Write the rational equation",
        second="Clear denominators",
        middle="Check candidate solutions",
        last="State valid solution(s)",
    ),
    "complex_fractions": _Policy(
        first="Write the complex fraction",
        second="Multiply by a common factor",
        middle="Simplify numerator and denominator",
        last="State the simplified result",
    ),
}


def _truncate_label(label: str, limit: int = 44) -> str:
    if len(label) <= limit:
        return label
    return label[: limit - 1].rstrip() + "…"


def _label_for_index(policy: _Policy, index: int, total: int) -> str:
    if index == 0:
        return policy.first
    if index == total - 1:
        return policy.last
    if index == 1:
        return policy.second
    return policy.middle


def explain_steps(
    steps: list[TrustedLatex],
    *,
    subtopic: str,
    difficulty: Difficulty,
) -> tuple[TrustedLatex, ...]:
    """Add compact deterministic one-line wording to each solution step."""
    if not steps:
        return ()

    # Future hook: tune phrasing by difficulty without changing call sites.
    _ = difficulty

    policy = _ALGEBRA_POLICIES.get(subtopic, _DEFAULT_POLICY)
    explained: list[TrustedLatex] = []

    total = len(steps)
    for idx, step in enumerate(steps):
        label = _truncate_label(_label_for_index(policy, idx, total))
        text = step.value.strip()

        if text.startswith("$") and text.endswith("$") and len(text) >= 2:
            inner = text[1:-1].strip()
            explained.append(TrustedLatex(f"$\\text{{{label}:}}\\; {inner}$"))
        else:
            explained.append(TrustedLatex(f"$\\text{{{label}:}}\\; {text}$"))

    return tuple(explained)
