"""Local auth routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from mano.application.dtos.auth_dtos import (
    ForgotPasswordRequest as ForgotPasswordRequestDTO,
    LoginRequestDTO,
    RegisterRequest as RegisterRequestDTO,
    ResetPasswordRequest as ResetPasswordRequestDTO,
)
from mano.application.use_cases.auth_use_cases import AuthUseCases
from mano.dependencies import (
    get_auth_use_cases,
    get_current_user,
    get_db_session,
    get_settings,
    lenient_auth_limiter,
    moderate_auth_limiter,
    strict_auth_limiter,
)
from mano.domain.exceptions.base import (
    DomainError,
    EmailAlreadyRegisteredError,
    EmailDeliveryError,
    InvalidPasswordResetTokenError,
)
from mano.domain.models.user import UserProfile
from mano.infrastructure.config.settings import Settings
from mano.infrastructure.security.local_auth import authenticate_user, create_access_token
from mano.presentation.schemas.auth_schemas import (
    AuthUserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_login_response(user_email: str, full_name: str, role: str, settings: Settings) -> LoginResponse:
    access_token = create_access_token(
        secret_key=settings.secret_key or "dev-secret-change-me",
        subject=user_email,
        role=role,
        full_name=full_name,
    )
    return LoginResponse(
        access_token=access_token,
        expires_in=60 * 60 * 12,
        user=AuthUserResponse(email=user_email, full_name=full_name, role=role),
    )


@moderate_auth_limiter
@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    payload: RegisterRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
    db_session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    _ = request
    try:
        role = use_cases.parse_role(payload.role)
        result = await use_cases.register(
            RegisterRequestDTO(
                email=str(payload.email),
                password=payload.password,
                full_name=payload.full_name,
                phone=payload.phone,
                role=role,
                city=payload.city,
                company_name=payload.company_name,
            )
        )
        return _build_login_response(result.email, result.full_name, result.role, settings)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@strict_auth_limiter
@router.post("/login", response_model=LoginResponse, summary="Login with local credentials")
async def login(
    request: Request,
    payload: LoginRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
    db_session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    _ = request
    result = await use_cases.login(LoginRequestDTO(email=str(payload.email), password=payload.password))
    if result is not None:
        return _build_login_response(result.email, result.full_name, result.role, settings)

    # Backward compatibility for existing hardcoded demo users.
    demo_user = authenticate_user(str(payload.email), payload.password)
    if not demo_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return _build_login_response(demo_user["email"], demo_user["full_name"], demo_user["role"], settings)


@lenient_auth_limiter
@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
    db_session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> ForgotPasswordResponse:
    _ = request
    try:
        reset_token = await use_cases.forgot_password(ForgotPasswordRequestDTO(email=str(payload.email)))
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ForgotPasswordResponse(
        message="If that email exists, a password reset link has been generated.",
        reset_token=reset_token if settings.is_development else None,
    )


@strict_auth_limiter
@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
    db_session: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    _ = request
    try:
        await use_cases.reset_password(
            ResetPasswordRequestDTO(token=payload.token, new_password=payload.new_password)
        )
    except InvalidPasswordResetTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return MessageResponse(message="Password has been reset successfully")


@router.get("/me", response_model=AuthUserResponse, summary="Current authenticated user")
async def me(current_user: UserProfile = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse(
        email=current_user.profile_metadata.get("email", "unknown@mano.local"),
        full_name=current_user.full_name,
        role=str(current_user.role),
    )
