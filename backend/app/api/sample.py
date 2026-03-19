"""Public sample test endpoint — no auth required.

Lets visitors experience the product before signing up. Capped at
5 questions with aggressive rate limiting to prevent abuse.
"""

import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from app.engine.types import GenerationError
from app.models.test import GenerateRequest, TestResponse
from app.rate_limiter import limiter
from app.services.generation_service import generation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sample"])

_SAMPLE_MAX_QUESTIONS = 5


@router.get("/sample-test", response_model=TestResponse)
@limiter.limit("5/hour")
def generate_sample_test(
    request: Request,
    topics: str = "algebra",
    difficulty: str = "easy",
    count: int = 5,
):
    """Generate a small sample test for unauthenticated visitors.

    - Public (no auth, no subscription)
    - Capped at 5 questions
    - Rate-limited to 5 per hour per IP
    - Does not track ownership or record stats
    """
    capped_count = min(count, _SAMPLE_MAX_QUESTIONS)
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]

    if not topic_list:
        raise HTTPException(status_code=400, detail="At least one topic is required")

    try:
        gen_request = GenerateRequest(
            topics=topic_list,
            difficulty=difficulty,
            count=capped_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        return generation_service.generate(gen_request, user_id="")
    except (ValueError, GenerationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
