"""Pydantic schemas для роутера auth."""

from uuid import UUID

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Ответ с токенами."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Запрос на вход."""

    username: str
    password: str


class RefreshRequest(BaseModel):
    """Запрос на обновление токена."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Запрос на выход (опционально)."""

    refresh_token: str | None = None


class UserCreate(BaseModel):
    """Создание пользователя (админ)."""

    username: str = Field(..., min_length=3, max_length=255)
    role: str = Field(default="user", pattern="^(admin|user)$")


class UserCreateResponse(BaseModel):
    """Ответ при создании пользователя (пароль только один раз)."""

    id: UUID
    username: str
    role: str
    password: str  # Автогенерированный пароль, показывается только при создании


class UserRead(BaseModel):
    """Чтение пользователя."""

    id: UUID
    username: str
    role: str
    is_active: bool
