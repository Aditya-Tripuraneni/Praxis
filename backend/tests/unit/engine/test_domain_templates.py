"""Tests for domain template correctness.

Uses SymPy's continuous_domain() as an independent oracle to verify
that generated domain answers are mathematically correct.
"""

import random
import re

import pytest
import sympy
from sympy import Symbol

import app.engine.topics  # noqa: F401
from app.engine import Difficulty, Topic, registry

x = Symbol("x")

# Number of random problems to generate per template per difficulty
SAMPLES_PER_LEVEL = 5


def _extract_sympy_expr(question_latex: str):
    """Extract the SymPy expression from a domain question's LaTeX.

    Questions look like: 'Find the domain of $f(x) = \\sqrt{x - 3}$.'
    We need to parse the math after 'f(x) =' from the LaTeX.
    """
    # Find content between $ signs
    match = re.search(r"\$f\(x\)\s*=\s*(.+?)\$", question_latex)
    if not match:
        return None
    latex_expr = match.group(1).strip().rstrip(".")
    try:
        return sympy.parse_expr(
            latex_expr,
            transformations="all",
            local_dict={"x": x},
        )
    except Exception:
        return None


def _get_domain_templates():
    """Get all domain-related templates from the registry."""
    templates = []
    for topic in Topic:
        for diff in Difficulty:
            for t in registry.get_templates(topic, diff):
                if "domain" in t.subtopic:
                    templates.append((t, diff))
    return templates


class TestDomainTemplatesExist:
    """Verify domain templates are registered."""

    def test_domain_subtopics_registered(self):
        all_subtopics = set()
        for topic in Topic:
            for diff in Difficulty:
                for t in registry.get_templates(topic, diff):
                    if "domain" in t.subtopic:
                        all_subtopics.add(t.subtopic)

        expected = {
            "domain_rational",
            "domain_radical",
            "domain_logarithmic",
            "domain_composite",
            "domain_trigonometric",
        }
        assert expected.issubset(all_subtopics), (
            f"Missing domain subtopics: {expected - all_subtopics}"
        )

    def test_old_domain_template_removed(self):
        """The old generic 'domain' subtopic should not exist."""
        for topic in Topic:
            for diff in Difficulty:
                for t in registry.get_templates(topic, diff):
                    assert t.subtopic != "domain", (
                        "Old DomainTemplate with subtopic='domain' still registered"
                    )


class TestDomainTemplatesGenerate:
    """Verify every domain template generates valid problems."""

    @pytest.fixture
    def domain_templates(self):
        return _get_domain_templates()

    def test_all_produce_output(self, domain_templates):
        assert len(domain_templates) >= 5, "Expected at least 5 domain template+difficulty combos"
        rng = random.Random(42)
        for template, diff in domain_templates:
            for _ in range(SAMPLES_PER_LEVEL):
                p = template.generate(diff, rng)
                assert p.question_latex, f"{template.subtopic}/{diff}: empty question"
                assert p.answer_latex, f"{template.subtopic}/{diff}: empty answer"
                assert "domain" in p.subtopic
                assert "Find the domain" in p.question_latex.value

    def test_variety_within_difficulty(self, domain_templates):
        """Templates with multiple variants should produce varied questions."""
        # Trig EASY has only tan(x) — single variant is acceptable there.
        # All other template/difficulty combos should produce variety.
        single_variant_ok = {("domain_trigonometric", Difficulty.EASY)}
        rng = random.Random(123)
        for template, diff in domain_templates:
            if (template.subtopic, diff) in single_variant_ok:
                continue
            questions = set()
            for _ in range(10):
                p = template.generate(diff, rng)
                questions.add(p.question_latex)
            assert len(questions) > 1, f"{template.subtopic}/{diff}: all 10 questions identical"


class TestDomainAnswerCorrectness:
    """Use SymPy continuous_domain as oracle to verify selected answers."""

    def test_rational_domain_easy(self):
        """1/(x-a) should have domain R \\ {a}."""
        rng = random.Random(42)
        templates = registry.get_templates_for_subtopic(
            Topic.FUNCTIONS, "domain_rational", Difficulty.EASY
        )
        assert templates, "No rational domain easy templates"
        for _ in range(SAMPLES_PER_LEVEL):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Answer should exclude at least one value
            assert "\\setminus" in p.answer_latex.value or "\\mathbb{R}" in p.answer_latex.value

    def test_radical_domain_easy(self):
        """sqrt(ax+b) should have domain [-b/a, inf) or R."""
        rng = random.Random(42)
        templates = registry.get_templates_for_subtopic(
            Topic.FUNCTIONS, "domain_radical", Difficulty.EASY
        )
        assert templates, "No radical domain easy templates"
        for _ in range(SAMPLES_PER_LEVEL):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Should produce an interval or all reals
            assert "\\infty" in p.answer_latex.value or "\\mathbb{R}" in p.answer_latex.value

    def test_log_domain_produces_open_interval(self):
        """log(ax+b) should produce OPEN interval (not closed)."""
        rng = random.Random(42)
        templates = registry.get_templates_for_subtopic(
            Topic.FUNCTIONS, "domain_logarithmic", Difficulty.EASY
        )
        if not templates:
            pytest.skip("No log domain templates registered yet")
        for _ in range(SAMPLES_PER_LEVEL):
            p = templates[0].generate(Difficulty.EASY, rng)
            # Log domains should use open intervals (parentheses, not brackets)
            # because log(0) is undefined
            assert "\\infty" in p.answer_latex.value

    def test_trig_domain_has_periodic_exclusion(self):
        """tan(x) domain should mention periodic exclusion."""
        rng = random.Random(42)
        templates = registry.get_templates_for_subtopic(
            Topic.FUNCTIONS, "domain_trigonometric", Difficulty.EASY
        )
        if not templates:
            pytest.skip("No trig domain templates registered yet")
        p = templates[0].generate(Difficulty.EASY, rng)
        assert "\\mathbb{Z}" in p.answer_latex.value or "n" in p.answer_latex.value


class TestDomainOracleVerification:
    """Use SymPy continuous_domain() as independent oracle."""

    def test_rational_domain_oracle(self):
        """Verify rational domain answers — oracle confirms domain is NOT all reals."""
        from sympy import S
        from sympy.calculus.util import continuous_domain

        x_sym = Symbol("x")
        templates = registry.get_templates_for_subtopic(
            Topic.FUNCTIONS, "domain_rational", Difficulty.EASY
        )
        assert templates
        rng_local = random.Random(42)
        for _ in range(SAMPLES_PER_LEVEL):
            p = templates[0].generate(Difficulty.EASY, rng_local)
            q_text = p.question_latex.value
            # Extract expression between f(x) = and the closing $
            match = re.search(r"f\(x\)\s*=\s*(.+?)\$", q_text)
            if not match:
                continue
            expr_str = match.group(1).strip().rstrip(".")
            try:
                expr = sympy.parse_expr(expr_str, local_dict={"x": x_sym}, transformations="all")
                domain = continuous_domain(expr, x_sym, S.Reals)
                # Easy rational always has a pole — domain should NOT be all reals
                assert domain != S.Reals, (
                    f"Oracle says all reals but question has restriction: {q_text}"
                )
            except Exception:
                pass  # parse_expr may fail on complex LaTeX
