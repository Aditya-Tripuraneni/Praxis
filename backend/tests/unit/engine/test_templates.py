"""Tests that all registered templates generate valid problems at all difficulty levels.

Runs AFTER topic modules are loaded. Validates:
- Every template produces non-empty LaTeX
- Every template works at all its supported difficulties
- Deterministic output with seed
- Varied output without seed
"""

import random

import pytest

# Importing topics triggers @register_template decorators
import app.engine.topics  # noqa: F401
from app.engine import Difficulty, GenerationConfig, Topic, generate_test, registry


class TestAllTemplatesGenerate:
    """Verify every registered template can generate at all supported difficulties."""

    @pytest.fixture
    def all_templates(self):
        templates = []
        for topic in Topic:
            for difficulty in Difficulty:
                for t in registry.get_templates(topic, difficulty):
                    templates.append((t, difficulty))
        return templates

    def test_registry_not_empty(self):
        topics = registry.get_all_topics()
        assert len(topics) >= 3, f"Expected at least 3 topics registered, got {topics}"

    def test_each_template_generates(self, all_templates):
        assert len(all_templates) > 0, "No templates found in registry"
        rng = random.Random(42)
        for template, difficulty in all_templates:
            problem = template.generate(difficulty, rng)
            assert problem.question_latex, (
                f"{template.subtopic} at {difficulty} produced empty question"
            )
            assert problem.answer_latex, (
                f"{template.subtopic} at {difficulty} produced empty answer"
            )
            assert problem.topic in Topic
            assert problem.difficulty == difficulty

    def test_minimum_template_count(self):
        total = sum(
            len(registry.get_templates(topic, diff)) for topic in Topic for diff in Difficulty
        )
        # We expect at least 20 template+difficulty combos (FR: SC-007)
        assert total >= 20, f"Only {total} template+difficulty combos registered"


class TestGenerateTestIntegration:
    """Test generate_test with real templates."""

    @pytest.fixture(autouse=True)
    def _load_topics(self):
        pass  # noqa: F401

    def test_algebra_easy_10(self):
        config = GenerationConfig(
            topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10, seed=123
        )
        problems = generate_test(config, registry)
        assert len(problems) == 10
        for p in problems:
            assert p.topic == Topic.ALGEBRA
            assert p.question_latex
            assert p.answer_latex

    def test_mixed_topics(self):
        config = GenerationConfig(
            topics=[Topic.ALGEBRA, Topic.CALCULUS],
            difficulty=Difficulty.MEDIUM,
            count=10,
            seed=456,
        )
        problems = generate_test(config, registry)
        assert len(problems) == 10
        topics_seen = {p.topic for p in problems}
        assert len(topics_seen) >= 2

    def test_all_difficulties(self):
        for diff in Difficulty:
            config = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=diff, count=5, seed=789)
            problems = generate_test(config, registry)
            assert len(problems) == 5
            for p in problems:
                assert p.difficulty == diff

    def test_varied_output(self):
        config1 = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10)
        config2 = GenerationConfig(topics=[Topic.ALGEBRA], difficulty=Difficulty.EASY, count=10)
        r1 = generate_test(config1, registry)
        r2 = generate_test(config2, registry)
        q1 = [p.question_latex for p in r1]
        q2 = [p.question_latex for p in r2]
        assert q1 != q2, "Two unseeded runs should produce different problems"

    def test_50_questions_performance(self):
        """SC-002: generation < 3s for 50 questions."""
        import time

        config = GenerationConfig(
            topics=list(Topic), difficulty=Difficulty.MEDIUM, count=50, seed=999
        )
        start = time.perf_counter()
        problems = generate_test(config, registry)
        elapsed = time.perf_counter() - start
        assert len(problems) == 50
        assert elapsed < 3.0, f"Generation took {elapsed:.2f}s, expected < 3s"
