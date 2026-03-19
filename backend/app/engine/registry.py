from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.engine.types import Difficulty, ProblemTemplate, Topic


class TemplateRegistry:
    def __init__(self):
        self._templates: dict[str, list[ProblemTemplate]] = defaultdict(list)

    def register(self, template: ProblemTemplate) -> None:
        self._templates[template.topic].append(template)

    def get_templates(self, topic: Topic, difficulty: Difficulty) -> list[ProblemTemplate]:
        return [
            t for t in self._templates.get(topic, []) if difficulty in t.supported_difficulties
        ]

    def get_all_topics(self) -> list[Topic]:
        from app.engine.types import Topic

        return [t for t in Topic if self._templates.get(t)]

    def get_templates_for_subtopic(
        self, topic: Topic, subtopic: str, difficulty: Difficulty
    ) -> list[ProblemTemplate]:
        return [
            t
            for t in self._templates.get(topic, [])
            if t.subtopic == subtopic and difficulty in t.supported_difficulties
        ]

    def get_topic_data(self, topic: Topic) -> dict:
        """Return raw topic data. No display names — that's the service layer's job."""
        templates = self._templates.get(topic, [])
        subtopic_ids = sorted({t.subtopic for t in templates})
        difficulties = sorted({d.value for t in templates for d in t.supported_difficulties})
        return {
            "topic": topic.value,
            "subtopic_ids": subtopic_ids,
            "difficulties": difficulties,
            "template_count": len(templates),
        }


registry = TemplateRegistry()


def register_template(cls):
    """Class decorator that instantiates and registers a template."""
    instance = cls()
    registry.register(instance)
    return cls
