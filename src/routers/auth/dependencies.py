"""Зависимости для auth."""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from src.database.dependencies import DbSession
from src.routers.auth.actions import get_current_user, require_admin
from src.routers.auth.models import User
from src.routers.auth.security import decode_token

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: DbSession,
) -> User | None:
    """Текущий пользователь или None (если не авторизован)."""
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        return None
    try:
        return await get_current_user(session, payload)
    except HTTPException:
        return None


async def get_current_user_required(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: DbSession,
) -> User:
    """Текущий пользователь (обязательно авторизован)."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_current_user(session, payload)


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user_required)],
) -> User:
    """Текущий пользователь с ролью admin."""
    require_admin(user)
    return user


CurrentUser = Annotated[User, Depends(get_current_user_required)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
