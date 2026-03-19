from datetime import datetime

from pydantic import BaseModel, Field


class SaveTestRequest(BaseModel):
    test_name: str = Field(min_length=1, max_length=100)
    config: dict  # GenerateRequest as dict (topics, difficulty, count)
    seed: int
    questions: list[dict]  # QuestionResponse[] as dicts


class RenameTestRequest(BaseModel):
    test_name: str = Field(min_length=1, max_length=100)


class SavedTestResponse(BaseModel):
    id: str
    test_name: str
    config: dict
    seed: int
    questions: list[dict]
    created_at: datetime


class SavedTestSummary(BaseModel):
    """Lightweight version for list endpoint (no questions)."""

    id: str
    test_name: str
    config: dict
    seed: int
    question_count: int
    created_at: datetime
