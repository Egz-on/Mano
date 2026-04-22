"""Local auth routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from mano.application.dtos.auth_dtos import (
    ForgotPasswordRequest as ForgotPasswordRequestDTO,
    LoginRequestDTO,
    RegisterRequest as RegisterRequestDTO,
    ResetPasswordRequest as ResetPasswordRequestDTO,
)
from mano.application.use_cases.auth_use_cases import AuthUseCases
from mano.dependencies import (
    AccessTokenFactory,
    authenticate_demo_credentials,
    get_access_token_factory,
    get_auth_use_cases,
    get_current_user,
    get_is_development,
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


def _build_login_response(
    user_email: str,
    name: str,
    surname: str,
    role: str,
    create_access_token_for_user: AccessTokenFactory,
) -> LoginResponse:
    access_token = create_access_token_for_user(user_email, role, name, surname)
    return LoginResponse(
        access_token=access_token,
        expires_in=60 * 60 * 12,
        user=AuthUserResponse(email=user_email, name=name, surname=surname, role=role),
    )


@moderate_auth_limiter
@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    payload: RegisterRequest,
    create_access_token_for_user: AccessTokenFactory = Depends(get_access_token_factory),
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> LoginResponse:
    _ = request
    try:
        role = use_cases.parse_role(payload.role)
        result = await use_cases.register(
            RegisterRequestDTO(
                email=str(payload.email),
                password=payload.password,
                name=payload.name,
                surname=payload.surname,
                phone=payload.phone,
                role=role,
                city=payload.city,
                company_name=payload.company_name,
            )
        )
        return _build_login_response(
            result.email, result.name, result.surname, result.role, create_access_token_for_user
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@strict_auth_limiter
@router.post("/login", response_model=LoginResponse, summary="Login with local credentials")
async def login(
    request: Request,
    payload: LoginRequest,
    create_access_token_for_user: AccessTokenFactory = Depends(get_access_token_factory),
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> LoginResponse:
    _ = request
    result = await use_cases.login(LoginRequestDTO(email=str(payload.email), password=payload.password))
    if result is not None:
        return _build_login_response(
            result.email, result.name, result.surname, result.role, create_access_token_for_user
        )

    # Backward compatibility for existing hardcoded demo users.
    demo_user = authenticate_demo_credentials(str(payload.email), payload.password)
    if not demo_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    email, name, surname, role = demo_user
    return _build_login_response(email, name, surname, role, create_access_token_for_user)


@lenient_auth_limiter
@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
    is_development: bool = Depends(get_is_development),
) -> ForgotPasswordResponse:
    _ = request
    try:
        reset_token = await use_cases.forgot_password(ForgotPasswordRequestDTO(email=str(payload.email)))
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ForgotPasswordResponse(
        message="If that email exists, a password reset link has been generated.",
        reset_token=reset_token if is_development else None,
    )


@strict_auth_limiter
@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> MessageResponse:
    _ = request
    try:
        await use_cases.reset_password(ResetPasswordRequestDTO(token=payload.token, new_password=payload.new_password))
    except InvalidPasswordResetTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return MessageResponse(message="Password has been reset successfully")


@router.get("/me", response_model=AuthUserResponse, summary="Current authenticated user")
async def me(current_user: UserProfile = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse(
        email=current_user.profile_metadata.get("email", "unknown@mano.local"),
        name=current_user.name,
        surname=current_user.surname,
        role=str(current_user.role),
    )
