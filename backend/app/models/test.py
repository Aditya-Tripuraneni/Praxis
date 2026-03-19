from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    topics: list[str] = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]
    count: int = Field(ge=1, le=50, default=20)
    seed: int | None = None

    @field_validator("topics")
    @classmethod
    def validate_topics(cls, v: list[str]) -> list[str]:
        from app.engine.types import Topic

        valid_topics = {t.value for t in Topic}
        for entry in v:
            base = entry.split(".")[0]
            if base not in valid_topics:
                raise ValueError(
                    f"Unknown topic '{base}'. Valid topics: {', '.join(sorted(valid_topics))}"
                )
        return v


class QuestionResponse(BaseModel):
    id: int
    question_latex: str
    answer_latex: str
    topic: str
    difficulty: str
    subtopic: str = ""
    solution_steps: list[str] = Field(default_factory=list)


class TestResponse(BaseModel):
    test_id: str
    questions: list[QuestionResponse]
    created_at: datetime
    config: GenerateRequest


class SubtopicInfo(BaseModel):
    id: str
    name: str


class TopicInfo(BaseModel):
    id: str
    name: str
    subtopics: list[SubtopicInfo]
    difficulties: list[str]
    template_count: int
