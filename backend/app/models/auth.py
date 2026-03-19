from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UserProfile(BaseModel):
    id: str
    email: str
    email_verified: bool
    created_at: datetime | None = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    user: UserProfile


class RefreshResponse(BaseModel):
    """Token refresh response -- no user field (unlike login)."""

    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str = Field(min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


class AuthMessage(BaseModel):
    message: str
