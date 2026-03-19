"""Tests for step-by-step solution generation across topic templates."""

import random

import pytest

import app.engine.topics  # noqa: F401 — triggers registration
from app.engine.registry import registry
from app.engine.topics.algebra.templates import (
    ExponentSimplifyTemplate,
    LinearEquationTemplate,
    PolynomialAddSubTemplate,
    PolynomialMultiplyTemplate,
    QuadraticFactoringTemplate,
    QuadraticFormulaTemplate,
    RadicalSimplifyTemplate,
    SystemOf2LinearTemplate,
    TwoStepLinearTemplate,
)
from app.engine.topics.calculus.templates import (
    BasicIntegralTemplate,
    ChainRuleTemplate,
    DerivativeBasicTemplate,
    LimitTemplate,
)
from app.engine.topics.domain.advanced import (
    CompositeDomainTemplate,
    LogDomainTemplate,
    TrigDomainTemplate,
)
from app.engine.topics.domain.basic import (
    RadicalDomainTemplate,
    RationalDomainTemplate,
)
from app.engine.topics.functions.templates import (
    FunctionCompositionTemplate,
    FunctionEvalTemplate,
    InverseFunctionTemplate,
)
from app.engine.topics.geometry.lines import (
    LineEquationTemplate,
    ParallelPerpSlopeTemplate,
    SlopeFromPointsTemplate,
    SlopeInterceptTemplate,
)
from app.engine.topics.geometry.shapes import (
    DistanceFormulaTemplate,
    MidpointFormulaTemplate,
    PerpendicularBisectorTemplate,
    TriangleAreaCoordsTemplate,
)
from app.engine.types import Difficulty, Topic, TrustedLatex

ALL_ALGEBRA_TEMPLATES = [
    LinearEquationTemplate,
    TwoStepLinearTemplate,
    QuadraticFactoringTemplate,
    QuadraticFormulaTemplate,
    PolynomialAddSubTemplate,
    PolynomialMultiplyTemplate,
    SystemOf2LinearTemplate,
    ExponentSimplifyTemplate,
    RadicalSimplifyTemplate,
]

ALL_CALCULUS_TEMPLATES = [
    LimitTemplate,
    DerivativeBasicTemplate,
    ChainRuleTemplate,
    BasicIntegralTemplate,
]

ALL_FUNCTIONS_TEMPLATES = [
    FunctionEvalTemplate,
    FunctionCompositionTemplate,
    InverseFunctionTemplate,
]

ALL_GEOMETRY_TEMPLATES = [
    SlopeFromPointsTemplate,
    SlopeInterceptTemplate,
    ParallelPerpSlopeTemplate,
    LineEquationTemplate,
    DistanceFormulaTemplate,
    MidpointFormulaTemplate,
    TriangleAreaCoordsTemplate,
    PerpendicularBisectorTemplate,
]


class TestAlgebraSolutionSteps:
    """Verify that all algebra templates produce valid step-by-step solutions."""

    @pytest.mark.parametrize(
        "template_cls",
        ALL_ALGEBRA_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_ALGEBRA_TEMPLATES],
    )
    @pytest.mark.parametrize("difficulty", list(Difficulty), ids=[d.value for d in Difficulty])
    def test_all_algebra_templates_produce_steps(self, template_cls, difficulty):
        """Each algebra template must produce non-empty solution steps at every difficulty."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(difficulty, rng)

        assert problem.solution_steps, (
            f"{template_cls.__name__} at {difficulty.value} produced empty solution_steps"
        )
        for i, step in enumerate(problem.solution_steps):
            assert isinstance(step, TrustedLatex), (
                f"{template_cls.__name__} step {i} is {type(step).__name__}, expected TrustedLatex"
            )
            assert step.value, f"{template_cls.__name__} step {i} has empty .value"

    @pytest.mark.parametrize(
        "template_cls",
        ALL_ALGEBRA_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_ALGEBRA_TEMPLATES],
    )
    def test_steps_first_matches_question_pattern(self, template_cls):
        """The first solution step should contain a $ delimiter (LaTeX math mode)."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(Difficulty.EASY, rng)

        first_step = problem.solution_steps[0]
        assert "$" in first_step.value, (
            f"{template_cls.__name__} first step lacks LaTeX delimiter: {first_step.value!r}"
        )

    def test_steps_are_deterministic(self):
        """Same seed must produce identical solution_steps."""
        template = LinearEquationTemplate()

        rng1 = random.Random(42)
        problem1 = template.generate(Difficulty.EASY, rng1)

        rng2 = random.Random(42)
        problem2 = template.generate(Difficulty.EASY, rng2)

        assert problem1.solution_steps == problem2.solution_steps

    def test_all_registered_templates_have_steps(self):
        """Every registered template now produces non-empty solution_steps."""
        for topic in Topic:
            templates = registry.get_templates(topic, Difficulty.EASY)
            for tmpl in templates:
                rng = random.Random(42)
                problem = tmpl.generate(Difficulty.EASY, rng)
                assert problem.solution_steps, f"{topic.value}/{tmpl.subtopic} has empty steps"

    @pytest.mark.parametrize(
        "template_cls",
        ALL_ALGEBRA_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_ALGEBRA_TEMPLATES],
    )
    def test_steps_minimum_count(self, template_cls):
        """Each algebra template at MEDIUM difficulty must produce at least 2 steps."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(Difficulty.MEDIUM, rng)

        assert len(problem.solution_steps) >= 2, (
            f"{template_cls.__name__} at MEDIUM produced only "
            f"{len(problem.solution_steps)} step(s), expected >= 2"
        )


class TestCalculusSolutionSteps:
    """Verify that all calculus templates produce valid step-by-step solutions."""

    @pytest.mark.parametrize(
        "template_cls",
        ALL_CALCULUS_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_CALCULUS_TEMPLATES],
    )
    @pytest.mark.parametrize(
        "difficulty",
        list(Difficulty),
        ids=[d.value for d in Difficulty],
    )
    def test_all_calculus_templates_produce_steps(self, template_cls, difficulty):
        """Each calculus template must produce non-empty solution steps."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(difficulty, rng)

        assert problem.solution_steps, (
            f"{template_cls.__name__} at {difficulty.value} produced empty solution_steps"
        )
        for i, step in enumerate(problem.solution_steps):
            assert isinstance(step, TrustedLatex), (
                f"{template_cls.__name__} step {i} is {type(step).__name__}, expected TrustedLatex"
            )
            assert step.value, f"{template_cls.__name__} step {i} has empty .value"

    @pytest.mark.parametrize(
        ("difficulty", "min_steps"),
        [
            (Difficulty.EASY, 2),
            (Difficulty.MEDIUM, 3),
            (Difficulty.HARD, 3),
        ],
        ids=["easy>=2", "medium>=3", "hard>=3"],
    )
    def test_limit_steps_count(self, difficulty, min_steps):
        """LimitTemplate must produce a minimum number of steps."""
        template = LimitTemplate()
        rng = random.Random(42)
        problem = template.generate(difficulty, rng)

        assert len(problem.solution_steps) >= min_steps, (
            f"LimitTemplate at {difficulty.value} produced"
            f" {len(problem.solution_steps)} step(s),"
            f" expected >= {min_steps}"
        )

    def test_chain_rule_shows_derivative_notation(self):
        """ChainRuleTemplate EASY steps must show unevaluated derivative."""
        template = ChainRuleTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.EASY, rng)

        has_deriv_notation = any("\\frac{d}{d x}" in step.value for step in problem.solution_steps)
        assert has_deriv_notation, (
            "ChainRuleTemplate EASY: no step contains '\\frac{d}{d x}' notation"
        )

    def test_integral_hard_shows_substitution_variable(self):
        """BasicIntegralTemplate HARD steps must reference u-substitution."""
        template = BasicIntegralTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.HARD, rng)

        has_u = any("u" in step.value for step in problem.solution_steps)
        assert has_u, "BasicIntegralTemplate HARD: no step contains 'u'"

    def test_calculus_steps_deterministic(self):
        """Same seed must produce identical solution_steps."""
        template = LimitTemplate()

        rng1 = random.Random(42)
        problem1 = template.generate(Difficulty.EASY, rng1)

        rng2 = random.Random(42)
        problem2 = template.generate(Difficulty.EASY, rng2)

        assert problem1.solution_steps == problem2.solution_steps


class TestFunctionsSolutionSteps:
    """Verify that all functions templates produce valid step-by-step solutions."""

    @pytest.mark.parametrize(
        "template_cls",
        ALL_FUNCTIONS_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_FUNCTIONS_TEMPLATES],
    )
    @pytest.mark.parametrize(
        "difficulty",
        list(Difficulty),
        ids=[d.value for d in Difficulty],
    )
    def test_all_functions_templates_produce_steps(self, template_cls, difficulty):
        """Each functions template must produce non-empty solution steps at every difficulty."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(difficulty, rng)

        assert problem.solution_steps, (
            f"{template_cls.__name__} at {difficulty.value} produced empty solution_steps"
        )
        for i, step in enumerate(problem.solution_steps):
            assert isinstance(step, TrustedLatex), (
                f"{template_cls.__name__} step {i} is {type(step).__name__}, expected TrustedLatex"
            )
            assert step.value, f"{template_cls.__name__} step {i} has empty .value"

    def test_composition_shows_intermediate(self):
        """FunctionCompositionTemplate EASY steps must show inner function evaluation."""
        template = FunctionCompositionTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.EASY, rng)

        has_inner = any("g(" in step.value for step in problem.solution_steps)
        assert has_inner, (
            "FunctionCompositionTemplate EASY: no step contains 'g(' showing inner evaluation"
        )

    def test_inverse_shows_y_equation(self):
        """InverseFunctionTemplate EASY step 0 must contain 'y =' setup."""
        template = InverseFunctionTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.EASY, rng)

        assert "y =" in problem.solution_steps[0].value, (
            "InverseFunctionTemplate EASY: step 0 does not"
            f" contain 'y =': {problem.solution_steps[0].value!r}"
        )

    def test_functions_steps_deterministic(self):
        """Same seed must produce identical solution_steps."""
        template = FunctionEvalTemplate()

        rng1 = random.Random(42)
        problem1 = template.generate(Difficulty.EASY, rng1)

        rng2 = random.Random(42)
        problem2 = template.generate(Difficulty.EASY, rng2)

        assert problem1.solution_steps == problem2.solution_steps


class TestGeometrySolutionSteps:
    """Verify that all geometry templates produce valid step-by-step solutions."""

    @pytest.mark.parametrize(
        "template_cls",
        ALL_GEOMETRY_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_GEOMETRY_TEMPLATES],
    )
    @pytest.mark.parametrize(
        "difficulty",
        list(Difficulty),
        ids=[d.value for d in Difficulty],
    )
    def test_all_geometry_templates_produce_steps(self, template_cls, difficulty):
        """Each geometry template must produce non-empty solution steps at every difficulty."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(difficulty, rng)

        assert problem.solution_steps, (
            f"{template_cls.__name__} at {difficulty.value} produced empty solution_steps"
        )
        for i, step in enumerate(problem.solution_steps):
            assert isinstance(step, TrustedLatex), (
                f"{template_cls.__name__} step {i} is {type(step).__name__}, expected TrustedLatex"
            )
            assert step.value, f"{template_cls.__name__} step {i} has empty .value"

    def test_slope_shows_fraction(self):
        """SlopeFromPointsTemplate MEDIUM steps must contain a \\frac."""
        template = SlopeFromPointsTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.MEDIUM, rng)

        has_frac = any("\\frac" in step.value for step in problem.solution_steps)
        assert has_frac, "SlopeFromPointsTemplate MEDIUM: no step contains '\\frac'"

    def test_distance_shows_sqrt(self):
        """DistanceFormulaTemplate MEDIUM steps must contain a \\sqrt."""
        template = DistanceFormulaTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.MEDIUM, rng)

        has_sqrt = any("\\sqrt" in step.value for step in problem.solution_steps)
        assert has_sqrt, "DistanceFormulaTemplate MEDIUM: no step contains '\\sqrt'"

    def test_geometry_steps_deterministic(self):
        """Same seed must produce identical solution_steps."""
        template = MidpointFormulaTemplate()

        rng1 = random.Random(42)
        problem1 = template.generate(Difficulty.EASY, rng1)

        rng2 = random.Random(42)
        problem2 = template.generate(Difficulty.EASY, rng2)

        assert problem1.solution_steps == problem2.solution_steps


class TestTrigonometrySolutionSteps:
    """Verify that all trig templates produce valid step-by-step solutions."""

    def test_all_trig_templates_produce_steps(self):
        """Every registered trig template produces non-empty steps."""
        topics_templates = []
        for diff in Difficulty:
            templates = registry.get_templates(Topic.TRIGONOMETRY, diff)
            for tmpl in templates:
                topics_templates.append((tmpl, diff))

        assert topics_templates, "No trig templates registered"

        for tmpl, diff in topics_templates:
            rng = random.Random(42)
            problem = tmpl.generate(diff, rng)
            assert problem.solution_steps, f"{tmpl.subtopic} at {diff.value} has empty steps"
            for step in problem.solution_steps:
                assert isinstance(step, TrustedLatex)
                assert step.value

    def test_trig_steps_deterministic(self):
        """Same seed must produce identical steps."""
        templates = registry.get_templates(Topic.TRIGONOMETRY, Difficulty.EASY)
        assert templates
        tmpl = templates[0]

        p1 = tmpl.generate(Difficulty.EASY, random.Random(42))
        p2 = tmpl.generate(Difficulty.EASY, random.Random(42))
        assert p1.solution_steps == p2.solution_steps


ALL_DOMAIN_TEMPLATES = [
    RationalDomainTemplate,
    RadicalDomainTemplate,
    LogDomainTemplate,
    CompositeDomainTemplate,
    TrigDomainTemplate,
]


class TestDomainSolutionSteps:
    """Verify that all domain templates produce valid step-by-step solutions."""

    @pytest.mark.parametrize(
        "template_cls",
        ALL_DOMAIN_TEMPLATES,
        ids=[cls.__name__ for cls in ALL_DOMAIN_TEMPLATES],
    )
    @pytest.mark.parametrize(
        "difficulty",
        list(Difficulty),
        ids=[d.value for d in Difficulty],
    )
    def test_all_domain_templates_produce_steps(self, template_cls, difficulty):
        """Each domain template must produce non-empty solution steps."""
        template = template_cls()
        rng = random.Random(42)
        problem = template.generate(difficulty, rng)

        assert problem.solution_steps, (
            f"{template_cls.__name__} at {difficulty.value} produced empty solution_steps"
        )
        for i, step in enumerate(problem.solution_steps):
            assert isinstance(step, TrustedLatex), (
                f"{template_cls.__name__} step {i} is {type(step).__name__}, expected TrustedLatex"
            )
            assert step.value, f"{template_cls.__name__} step {i} has empty .value"

    def test_domain_shows_constraint(self):
        """RationalDomainTemplate EASY steps must contain a constraint."""
        template = RationalDomainTemplate()
        rng = random.Random(42)
        problem = template.generate(Difficulty.EASY, rng)

        has_neq = any("\\neq" in step.value for step in problem.solution_steps)
        assert has_neq, "RationalDomainTemplate EASY: no step contains '\\neq' constraint"

    def test_domain_steps_deterministic(self):
        """Same seed must produce identical solution_steps."""
        template = RadicalDomainTemplate()

        rng1 = random.Random(42)
        problem1 = template.generate(Difficulty.EASY, rng1)

        rng2 = random.Random(42)
        problem2 = template.generate(Difficulty.EASY, rng2)

        assert problem1.solution_steps == problem2.solution_steps
