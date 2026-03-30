"""Minimal checks for concise algebra step explanations."""

import random

from app.engine import Difficulty, Topic, registry


def test_algebra_steps_include_short_explanations():
    templates = registry.get_templates(Topic.ALGEBRA, Difficulty.EASY)
    assert templates, "No algebra templates registered"

    for template in templates:
        problem = template.generate(Difficulty.EASY, random.Random(123))
        assert problem.solution_steps, f"{template.subtopic} has no solution steps"
        for step in problem.solution_steps:
            assert "\\text{" in step.value, f"{template.subtopic} missing explanatory text"
