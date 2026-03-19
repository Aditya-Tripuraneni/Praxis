"""Saved tests API endpoints -- save, list, replay, rename, delete."""

import logging
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from app.api.dependencies import AuthenticatedUser, require_tutor_subscription
from app.models.saved_tests import (
    RenameTestRequest,
    SavedTestResponse,
    SavedTestSummary,
    SaveTestRequest,
)
from app.rate_limiter import limiter
from app.services.saved_tests import SavedTestLimitError, saved_tests_service
from app.services.stats import stats_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/saved-tests", tags=["saved-tests"])


@router.post("", response_model=SavedTestSummary, status_code=201)
@limiter.limit("30/minute")
async def save_test(
    request: Request,
    body: SaveTestRequest,
    auth: AuthenticatedUser = Depends(require_tutor_subscription),
):
    try:
        result = await saved_tests_service.save_test(
            user_id=auth.profile.id,
            test_name=body.test_name,
            config=body.config,
            seed=body.seed,
            questions=body.questions,
        )
        return SavedTestSummary(**result)
    except SavedTestLimitError:
        raise HTTPException(status_code=409, detail="Maximum of 100 saved tests reached")
    except Exception:
        logger.exception("Failed to save test for user %s", auth.profile.id)
        raise HTTPException(status_code=500, detail="Failed to save test")


@router.get("", response_model=list[SavedTestSummary])
@limiter.limit("30/minute")
async def list_tests(
    request: Request,
    auth: AuthenticatedUser = Depends(require_tutor_subscription),
):
    try:
        results = await saved_tests_service.list_tests(auth.profile.id)
        return [SavedTestSummary(**r) for r in results]
    except Exception:
        logger.exception("Failed to list saved tests for user %s", auth.profile.id)
        raise HTTPException(status_code=500, detail="Failed to list saved tests")


@router.get("/{test_id}/replay", response_model=SavedTestResponse)
@limiter.limit("20/minute")
async def replay_test(
    request: Request,
    test_id: str,
    auth: AuthenticatedUser = Depends(require_tutor_subscription),
):
    test = await saved_tests_service.get_test(test_id, auth.profile.id)
    if test is None:
        raise HTTPException(status_code=404, detail="Saved test not found")

    # Record stats + streak (non-blocking -- errors logged, not raised)
    try:
        topic_dist = dict(Counter(q["topic"] for q in test["questions"]))
        await stats_service.record_generation(
            user_id=auth.profile.id,
            question_count=len(test["questions"]),
            topic_counts=topic_dist,
        )
        await stats_service.update_streak(auth.profile.id)
    except Exception:
        logger.warning("Failed to record stats for replay", exc_info=True)

    return SavedTestResponse(**test)


@router.patch("/{test_id}", response_model=SavedTestSummary)
@limiter.limit("30/minute")
async def rename_test(
    request: Request,
    test_id: str,
    body: RenameTestRequest,
    auth: AuthenticatedUser = Depends(require_tutor_subscription),
):
    result = await saved_tests_service.rename_test(test_id, auth.profile.id, body.test_name)
    if result is None:
        raise HTTPException(status_code=404, detail="Saved test not found")
    return SavedTestSummary(**result)


@router.delete("/{test_id}")
@limiter.limit("30/minute")
async def delete_test(
    request: Request,
    test_id: str,
    auth: AuthenticatedUser = Depends(require_tutor_subscription),
):
    deleted = await saved_tests_service.delete_test(test_id, auth.profile.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Saved test not found")
    return {"message": "Test deleted"}
