from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CheckoutSessionRequest(BaseModel):
    plan: Literal["student", "tutor"]


class CheckoutSessionResponse(BaseModel):
    url: str


class SubscriptionStatus(BaseModel):
    status: str  # 'active', 'past_due', 'expired', 'inactive'
    is_active: bool
    current_period_end: datetime | None = None
    plan: str | None = None  # 'student', 'tutor', or None


class CancelSubscriptionResponse(BaseModel):
    message: str
    cancel_at_period_end: bool
