"""Tests for dot-notation topic parsing and subtopic filtering."""

import pytest

from app.engine.types import Topic
from app.services.generation_service import _parse_topic_selections


class TestParseTopicSelections:
    def test_bare_topic_returns_no_filter(self):
        topics, subtopics = _parse_topic_selections(["algebra"])
        assert topics == [Topic.ALGEBRA]
        assert subtopics is None

    def test_multiple_bare_topics(self):
        topics, subtopics = _parse_topic_selections(["algebra", "calculus"])
        assert Topic.ALGEBRA in topics
        assert Topic.CALCULUS in topics
        assert subtopics is None

    def test_dot_notation_single(self):
        topics, subtopics = _parse_topic_selections(["algebra.linear_equations"])
        assert topics == [Topic.ALGEBRA]
        assert subtopics == {Topic.ALGEBRA: ["linear_equations"]}

    def test_dot_notation_multiple_subtopics(self):
        topics, subtopics = _parse_topic_selections(
            ["algebra.linear_equations", "algebra.quadratic_factoring"]
        )
        assert topics == [Topic.ALGEBRA]
        assert set(subtopics[Topic.ALGEBRA]) == {"linear_equations", "quadratic_factoring"}

    def test_mixed_bare_and_dot(self):
        topics, subtopics = _parse_topic_selections(["calculus", "algebra.linear_equations"])
        assert Topic.ALGEBRA in topics
        assert Topic.CALCULUS in topics
        # calculus is bare (all subtopics), algebra is filtered
        assert subtopics == {Topic.ALGEBRA: ["linear_equations"]}
        assert Topic.CALCULUS not in subtopics

    def test_cross_topic_dot_notation(self):
        topics, subtopics = _parse_topic_selections(
            ["algebra.linear_equations", "functions.domain"]
        )
        assert Topic.ALGEBRA in topics
        assert Topic.FUNCTIONS in topics
        assert subtopics[Topic.ALGEBRA] == ["linear_equations"]
        assert subtopics[Topic.FUNCTIONS] == ["domain"]

    def test_invalid_topic_raises(self):
        with pytest.raises(ValueError):
            _parse_topic_selections(["nonexistent"])

    def test_invalid_dotted_topic_raises(self):
        with pytest.raises(ValueError):
            _parse_topic_selections(["nonexistent.subtopic"])
