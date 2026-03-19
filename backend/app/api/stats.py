import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from app.api.dependencies import AuthenticatedUser, get_current_user
from app.models.stats import TimerSaveRequest, TimerSaveResponse, UserStatsResponse
from app.rate_limiter import limiter
from app.services.stats import stats_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/me", response_model=UserStatsResponse)
@limiter.limit("30/minute")
async def get_my_stats(
    request: Request,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    data = await stats_service.get_user_stats(auth.profile.id)
    return UserStatsResponse(**data)


@router.put("/timer", response_model=TimerSaveResponse)
@limiter.limit("30/minute")
async def save_timer(
    request: Request,
    body: TimerSaveRequest,
    auth: AuthenticatedUser = Depends(get_current_user),
):
    try:
        await stats_service.save_timer_duration(auth.profile.id, body.duration)
        return TimerSaveResponse()
    except Exception:
        logger.exception("Failed to save timer for user %s", auth.profile.id)
        raise HTTPException(status_code=500, detail="Failed to save timer duration")
