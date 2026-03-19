from app.engine.registry import TemplateRegistry
from app.engine.types import Difficulty, GeneratedProblem, Topic, TrustedLatex


class FakeTemplate:
    def __init__(self, topic, subtopic="fake", difficulties=None):
        self.topic = topic
        self.subtopic = subtopic
        self.supported_difficulties = difficulties or list(Difficulty)

    def generate(self, difficulty, rng):
        return GeneratedProblem(
            question_latex=TrustedLatex("q"),
            answer_latex=TrustedLatex("a"),
            topic=self.topic,
            difficulty=difficulty,
            subtopic=self.subtopic,
        )


class TestTemplateRegistry:
    def test_register_and_retrieve(self):
        reg = TemplateRegistry()
        t = FakeTemplate(Topic.ALGEBRA)
        reg.register(t)
        assert reg.get_templates(Topic.ALGEBRA, Difficulty.EASY) == [t]

    def test_filter_by_difficulty(self):
        reg = TemplateRegistry()
        easy_only = FakeTemplate(Topic.ALGEBRA, difficulties=[Difficulty.EASY])
        hard_only = FakeTemplate(Topic.ALGEBRA, difficulties=[Difficulty.HARD])
        reg.register(easy_only)
        reg.register(hard_only)
        assert reg.get_templates(Topic.ALGEBRA, Difficulty.EASY) == [easy_only]
        assert reg.get_templates(Topic.ALGEBRA, Difficulty.HARD) == [hard_only]

    def test_empty_registry(self):
        reg = TemplateRegistry()
        assert reg.get_templates(Topic.ALGEBRA, Difficulty.EASY) == []
        assert reg.get_all_topics() == []

    def test_get_all_topics(self):
        reg = TemplateRegistry()
        reg.register(FakeTemplate(Topic.ALGEBRA))
        reg.register(FakeTemplate(Topic.CALCULUS))
        topics = reg.get_all_topics()
        assert Topic.ALGEBRA in topics
        assert Topic.CALCULUS in topics
        assert Topic.FUNCTIONS not in topics

    def test_get_topic_data(self):
        """Registry returns raw data — no display names, no API formatting."""
        reg = TemplateRegistry()
        reg.register(FakeTemplate(Topic.ALGEBRA, subtopic="linear"))
        reg.register(FakeTemplate(Topic.ALGEBRA, subtopic="quadratic"))
        data = reg.get_topic_data(Topic.ALGEBRA)
        assert data["topic"] == "algebra"
        assert "linear" in data["subtopic_ids"]
        assert "quadratic" in data["subtopic_ids"]
        assert data["template_count"] == 2
        # Verify NO display names in raw data
        assert "name" not in data
        assert "subtopics" not in data  # raw uses subtopic_ids, not subtopics

    def test_get_templates_for_subtopic(self):
        reg = TemplateRegistry()
        linear = FakeTemplate(Topic.ALGEBRA, subtopic="linear")
        quad = FakeTemplate(Topic.ALGEBRA, subtopic="quadratic")
        reg.register(linear)
        reg.register(quad)
        result_lin = reg.get_templates_for_subtopic(Topic.ALGEBRA, "linear", Difficulty.EASY)
        result_quad = reg.get_templates_for_subtopic(Topic.ALGEBRA, "quadratic", Difficulty.EASY)
        result_none = reg.get_templates_for_subtopic(Topic.ALGEBRA, "nonexistent", Difficulty.EASY)
        assert result_lin == [linear]
        assert result_quad == [quad]
        assert result_none == []
