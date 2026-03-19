import pytest

from app.engine.generator import generate_test
from app.engine.registry import TemplateRegistry
from app.engine.types import (
    Difficulty,
    GeneratedProblem,
    GenerationConfig,
    GenerationError,
    Topic,
    TrustedLatex,
)


class FakeTemplate:
    def __init__(self, topic=Topic.ALGEBRA, subtopic="fake"):
        self.topic = topic
        self.subtopic = subtopic
        self.supported_difficulties = list(Difficulty)

    def generate(self, difficulty, rng):
        val = rng.randint(1, 1_000_000)
        return GeneratedProblem(
            question_latex=TrustedLatex(f"q_{val}"),
            answer_latex=TrustedLatex(f"a_{val}"),
            topic=self.topic,
            difficulty=difficulty,
            subtopic=self.subtopic,
        )


class FailingTemplate:
    """Template that always fails — tests silent retry."""

    def __init__(self):
        self.topic = Topic.ALGEBRA
        self.subtopic = "failing"
        self.supported_difficulties = list(Difficulty)

    def generate(self, difficulty, rng):
        raise RuntimeError("Always fails")


def _make_registry(*templates) -> TemplateRegistry:
    reg = TemplateRegistry()
    for t in templates:
        reg.register(t)
    return reg


class TestGenerateTest:
    def test_correct_count(self):
        reg = _make_registry(FakeTemplate())
        config = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10)
        problems = generate_test(config, reg)
        assert len(problems) == 10

    def test_deterministic_with_seed(self):
        reg = _make_registry(FakeTemplate())
        config = GenerationConfig(
            topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=5, seed=42
        )
        run1 = generate_test(config, reg)
        run2 = generate_test(config, reg)
        assert [p.question_latex for p in run1] == [p.question_latex for p in run2]

    def test_different_without_seed(self):
        reg = _make_registry(FakeTemplate())
        config1 = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10)
        config2 = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10)
        run1 = generate_test(config1, reg)
        run2 = generate_test(config2, reg)
        # Extremely unlikely to be identical with random seeds
        q1 = [p.question_latex for p in run1]
        q2 = [p.question_latex for p in run2]
        assert q1 != q2

    def test_distributes_across_topics(self):
        reg = _make_registry(FakeTemplate(Topic.ALGEBRA), FakeTemplate(Topic.CALCULUS))
        config = GenerationConfig(
            topics=[Topic.ALGEBRA, Topic.CALCULUS], difficulty=Difficulty.EASY, count=10
        )
        problems = generate_test(config, reg)
        topics = {p.topic for p in problems}
        assert Topic.ALGEBRA in topics
        assert Topic.CALCULUS in topics

    def test_all_problems_have_latex(self):
        reg = _make_registry(FakeTemplate())
        config = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=5)
        for p in generate_test(config, reg):
            assert p.question_latex
            assert p.answer_latex

    def test_no_templates_raises(self):
        reg = TemplateRegistry()
        config = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=5)
        with pytest.raises(GenerationError, match="No templates"):
            generate_test(config, reg)

    def test_all_failures_produces_empty(self):
        reg = _make_registry(FailingTemplate())
        config = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=5)
        with pytest.raises(GenerationError, match="Failed to generate"):
            generate_test(config, reg)


class FlakeyTemplate:
    """Template that fails N times then succeeds."""

    def __init__(self, fail_count=2, topic=Topic.ALGEBRA):
        self.topic = topic
        self.subtopic = "flakey"
        self.supported_difficulties = list(Difficulty)
        self._calls = 0
        self._fail_count = fail_count

    def generate(self, difficulty, rng):
        self._calls += 1
        if self._calls <= self._fail_count:
            raise RuntimeError("Simulated failure")
        val = rng.randint(1, 1_000_000)
        return GeneratedProblem(
            question_latex=TrustedLatex(f"q_{val}"),
            answer_latex=TrustedLatex(f"a_{val}"),
            topic=self.topic,
            difficulty=difficulty,
            subtopic=self.subtopic,
        )


class TestGeneratorRetry:
    def test_retries_with_different_template(self):
        """If one template always fails, generator uses another."""
        failing = FailingTemplate()
        working = FakeTemplate()
        reg = _make_registry(failing, working)
        config = GenerationConfig(
            topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=5, seed=42
        )
        problems = generate_test(config, reg)
        assert len(problems) == 5

    def test_flakey_template_succeeds_after_retry(self):
        reg = TemplateRegistry()
        reg.register(FlakeyTemplate(fail_count=2))
        config = GenerationConfig(
            topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=3, seed=42
        )
        problems = generate_test(config, reg)
        assert len(problems) == 3
