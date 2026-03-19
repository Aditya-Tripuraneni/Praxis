from pydantic import BaseModel, Field


class UserStatsResponse(BaseModel):
    tests_generated: int = 0
    questions_generated: int = 0
    topic_counts: dict[str, int] = Field(default_factory=dict)
    streak_current: int = 0
    streak_best: int = 0
    is_active_today: bool = False
    last_test_duration: int | None = None


class TimerSaveRequest(BaseModel):
    duration: int = Field(gt=0, le=86400)


class TimerSaveResponse(BaseModel):
    saved: bool = True
