"""Роутер auth."""

from fastapi import APIRouter, Body, status

from src.database.dependencies import DbSession
from src.routers.auth.actions import (
    create_user_admin,
    login,
    logout,
    refresh_tokens,
    user_to_read,
)
from src.routers.auth.dependencies import CurrentAdmin, CurrentUser
from src.routers.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserCreateResponse,
    UserRead,
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    session: DbSession,
    data: LoginRequest,
) -> TokenResponse:
    """Вход: username + password -> access_token, refresh_token."""
    access, refresh, _ = await login(session, data.username, data.password)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_endpoint(
    session: DbSession,
    data: RefreshRequest,
) -> TokenResponse:
    """Обновление токенов по refresh_token."""
    access, refresh, _ = await refresh_tokens(session, data.refresh_token)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(data: LogoutRequest | None = Body(None)) -> None:
    """Выход: инвалидация refresh токена."""
    if data and data.refresh_token:
        await logout(data.refresh_token)


@router.get("/me", response_model=UserRead)
async def me_endpoint(user: CurrentUser) -> UserRead:
    """Текущий пользователь."""
    return user_to_read(user)


@router.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    session: DbSession,
    data: UserCreate,
    admin: CurrentAdmin,
) -> UserCreateResponse:
    """Создание пользователя администратором (автогенерация пароля)."""
    return await create_user_admin(session, data, admin)
