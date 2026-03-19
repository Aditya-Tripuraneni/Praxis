import pytest

from app.engine.types import Difficulty, GeneratedProblem, GenerationConfig, Topic, TrustedLatex


class TestDifficulty:
    def test_enum_values(self):
        assert Difficulty.EASY == "easy"
        assert Difficulty.MEDIUM == "medium"
        assert Difficulty.HARD == "hard"

    def test_all_difficulties(self):
        assert len(Difficulty) == 3


class TestTopic:
    def test_enum_values(self):
        assert Topic.ALGEBRA == "algebra"
        assert Topic.FUNCTIONS == "functions"
        assert Topic.TRIGONOMETRY == "trigonometry"
        assert Topic.CALCULUS == "calculus"


class TestGeneratedProblem:
    def test_create(self):
        p = GeneratedProblem(
            question_latex=TrustedLatex("x + 1 = 2"),
            answer_latex=TrustedLatex("x = 1"),
            topic=Topic.ALGEBRA,
            difficulty=Difficulty.EASY,
            subtopic="linear",
        )
        assert p.question_latex.value == "x + 1 = 2"
        assert p.answer_latex.value == "x = 1"

    def test_frozen(self):
        p = GeneratedProblem(
            question_latex=TrustedLatex("q"),
            answer_latex=TrustedLatex("a"),
            topic=Topic.ALGEBRA,
            difficulty=Difficulty.EASY,
        )
        with pytest.raises(AttributeError):
            p.question_latex = "changed"

    def test_rejects_raw_str(self):
        """TrustedLatex enforcement: raw strings must be rejected."""
        with pytest.raises(TypeError, match="must be TrustedLatex"):
            GeneratedProblem(
                question_latex="raw string",
                answer_latex=TrustedLatex("ok"),
                topic=Topic.ALGEBRA,
                difficulty=Difficulty.EASY,
            )

    def test_rejects_raw_str_answer(self):
        with pytest.raises(TypeError, match="must be TrustedLatex"):
            GeneratedProblem(
                question_latex=TrustedLatex("ok"),
                answer_latex="raw string",
                topic=Topic.ALGEBRA,
                difficulty=Difficulty.EASY,
            )

    def test_generated_problem_solution_steps_default(self):
        """solution_steps defaults to empty tuple when not provided."""
        p = GeneratedProblem(
            question_latex=TrustedLatex("q"),
            answer_latex=TrustedLatex("a"),
            topic=Topic.ALGEBRA,
            difficulty=Difficulty.EASY,
        )
        assert p.solution_steps == ()

    def test_generated_problem_solution_steps_provided(self):
        """solution_steps is accessible when explicitly provided."""
        steps = (TrustedLatex("$x=1$"),)
        p = GeneratedProblem(
            question_latex=TrustedLatex("q"),
            answer_latex=TrustedLatex("a"),
            topic=Topic.ALGEBRA,
            difficulty=Difficulty.EASY,
            solution_steps=steps,
        )
        assert p.solution_steps == steps
        assert p.solution_steps[0].value == "$x=1$"


class TestGenerationConfig:
    def test_valid(self):
        config = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10)
        assert config.count == 10

    def test_count_too_low(self):
        with pytest.raises(ValueError, match="1-50"):
            GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=0)

    def test_count_too_high(self):
        with pytest.raises(ValueError, match="1-50"):
            GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=100)

    def test_empty_topics(self):
        with pytest.raises(ValueError, match="At least one topic"):
            GenerationConfig(topics=[], difficulty=Difficulty.EASY, count=10)

    def test_seed(self):
        config = GenerationConfig(
            topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=5, seed=42
        )
        assert config.seed == 42
