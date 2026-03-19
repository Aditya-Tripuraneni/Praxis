"""Authentication API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from app.api.dependencies import AuthenticatedUser, get_current_user
from app.models.auth import (
    AuthMessage,
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SignupRequest,
    UserProfile,
    VerifyEmailRequest,
)
from app.rate_limiter import limiter
from app.security_logging import log_auth_event
from app.services.auth import (
    AuthenticationError,
    BreachedPasswordError,
    InvalidTokenError,
    auth_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=AuthMessage, status_code=201)
@limiter.limit("5/hour")
async def signup(request: Request, body: SignupRequest):
    client_ip = request.client.host if request.client else ""
    try:
        message = await auth_service.signup(body.email, body.password)
        log_auth_event("AUTH_SIGNUP", email=body.email, ip=client_ip)
        return AuthMessage(message=message)
    except BreachedPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Signup failed")
        raise HTTPException(status_code=500, detail="Signup failed")


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    client_ip = request.client.host if request.client else ""
    try:
        result = await auth_service.login(body.email, body.password)
        log_auth_event(
            "AUTH_LOGIN_SUCCESS",
            email=body.email,
            user_id=result["user"]["id"],
            ip=client_ip,
        )
        return AuthResponse(**result)
    except AuthenticationError as e:
        log_auth_event(
            "AUTH_LOGIN_FAILURE",
            email=body.email,
            success=False,
            ip=client_ip,
        )
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        log_auth_event(
            "AUTH_LOGIN_FAILURE",
            email=body.email,
            success=False,
            ip=client_ip,
        )
        logger.exception("Login failed unexpectedly")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("30/5 minutes")
async def refresh(request: Request, body: RefreshRequest):
    try:
        result = await auth_service.refresh(body.refresh_token)
        return RefreshResponse(**result)
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout", response_model=AuthMessage)
@limiter.limit("10/minute")
async def logout(request: Request, auth: AuthenticatedUser = Depends(get_current_user)):
    await auth_service.logout(auth.access_token)
    client_ip = request.client.host if request.client else ""
    log_auth_event("AUTH_LOGOUT", user_id=auth.profile.id, ip=client_ip)
    return AuthMessage(message="Logged out successfully")


@router.get("/me", response_model=UserProfile)
@limiter.limit("30/minute")
async def me(request: Request, auth: AuthenticatedUser = Depends(get_current_user)):
    return auth.profile


@router.delete("/account", response_model=AuthMessage)
@limiter.limit("3/hour")
async def delete_account(request: Request, auth: AuthenticatedUser = Depends(get_current_user)):
    client_ip = request.client.host if request.client else ""
    try:
        await auth_service.delete_user(auth.profile.id)
        log_auth_event(
            "AUTH_ACCOUNT_DELETED",
            user_id=auth.profile.id,
            email=auth.profile.email,
            ip=client_ip,
        )
        return AuthMessage(message="Account deleted successfully")
    except Exception:
        logger.exception("Account deletion failed for user %s", auth.profile.id)
        raise HTTPException(status_code=500, detail="Account deletion failed")


@router.post("/forgot-password", response_model=AuthMessage)
@limiter.limit("3/hour")
async def forgot_password(request: Request, body: ForgotPasswordRequest):
    client_ip = request.client.host if request.client else ""
    message = await auth_service.forgot_password(body.email)
    log_auth_event("AUTH_FORGOT_PASSWORD", email=body.email, ip=client_ip)
    return AuthMessage(message=message)


@router.post("/reset-password", response_model=AuthResponse)
@limiter.limit("10/minute")
async def reset_password(request: Request, body: ResetPasswordRequest):
    client_ip = request.client.host if request.client else ""
    try:
        result = await auth_service.reset_password(body.email, body.token, body.new_password)
        log_auth_event("AUTH_PASSWORD_RESET", email=body.email, ip=client_ip)
        return AuthResponse(**result)
    except BreachedPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-verification", response_model=AuthMessage)
@limiter.limit("3/hour")
async def resend_verification(request: Request, body: ResendVerificationRequest):
    message = await auth_service.resend_verification(body.email)
    return AuthMessage(message=message)


@router.post("/verify-email", response_model=AuthResponse)
@limiter.limit("10/minute")
async def verify_email(request: Request, body: VerifyEmailRequest):
    client_ip = request.client.host if request.client else ""
    try:
        result = await auth_service.verify_email(body.email, body.token)
        log_auth_event("AUTH_VERIFY_EMAIL", email=body.email, ip=client_ip)
        return AuthResponse(**result)
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
