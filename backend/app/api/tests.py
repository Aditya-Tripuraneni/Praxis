import logging
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from app.api.dependencies import AuthenticatedUser, require_active_subscription
from app.engine.types import GenerationError
from app.models.test import GenerateRequest, TestResponse, TopicInfo
from app.rate_limiter import limiter
from app.services.generation_service import generation_service
from app.services.stats import stats_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tests", tags=["tests"])


@router.post("/generate", response_model=TestResponse)
@limiter.limit("20/minute")
async def generate_test(
    request: Request,
    body: GenerateRequest,
    auth: AuthenticatedUser = Depends(require_active_subscription),
):
    try:
        response = generation_service.generate(body, user_id=auth.profile.id)
    except (ValueError, GenerationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Record stats + streak (non-blocking -- errors logged, not raised)
    try:
        topic_dist = dict(Counter(q.topic for q in response.questions))
        await stats_service.record_generation(
            user_id=auth.profile.id,
            question_count=len(response.questions),
            topic_counts=topic_dist,
        )
        await stats_service.update_streak(auth.profile.id)
    except Exception:
        logger.warning("Failed to record stats", exc_info=True)

    return response


@router.get("/topics", response_model=list[TopicInfo])
@limiter.limit("60/minute")
def get_topics(request: Request):
    """Public endpoint — no auth required."""
    return generation_service.get_topics()


@router.get("/{test_id}", response_model=TestResponse)
@limiter.limit("30/minute")
def get_test(
    request: Request,
    test_id: str,
    auth: AuthenticatedUser = Depends(require_active_subscription),
):
    result = generation_service.get_test_for_user(test_id, auth.profile.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return result
