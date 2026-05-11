"""Бизнес-логика роутера auth."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.redis_client.redis import RedisController
from src.routers.auth.dal import UserDAL
from src.routers.auth.enums import ADMIN_ROLE
from src.routers.auth.models import User
from src.routers.auth.schemas import UserCreate, UserCreateResponse, UserRead
from src.routers.auth.security import (
    REFRESH_PREFIX,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_password,
    hash_password,
    verify_password,
)


async def login(session: AsyncSession, username: str, password: str) -> tuple[str, str, User]:
    """Вход: возвращает (access_token, refresh_token, user)."""
    dal = UserDAL(session)
    user = await dal.get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Аккаунт отключён",
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    from src.config import jwt_cfg

    ttl = jwt_cfg.refresh_token_expire_days * 24 * 3600
    await RedisController.set(f"{REFRESH_PREFIX}{refresh}", str(user.id), ttl=ttl)

    return access, refresh, user


async def refresh_tokens(
    session: AsyncSession,
    refresh_token: str,
) -> tuple[str, str, User]:
    """Обновление токенов по refresh."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен",
        )

    key = f"{REFRESH_PREFIX}{refresh_token}"
    stored_user_id = await RedisController.get(key)
    if stored_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен истёк или отозван",
        )

    await RedisController.delete(key)

    dal = UserDAL(session)
    user = await dal.get_by_id(UUID(stored_user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или отключён",
        )

    access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)

    from src.config import jwt_cfg

    ttl = jwt_cfg.refresh_token_expire_days * 24 * 3600
    await RedisController.set(f"{REFRESH_PREFIX}{new_refresh}", str(user.id), ttl=ttl)

    return access, new_refresh, user


async def logout(refresh_token: str | None) -> None:
    """Выход: удаление refresh токена из Redis."""
    if refresh_token:
        await RedisController.delete(f"{REFRESH_PREFIX}{refresh_token}")


async def get_current_user(session: AsyncSession, token_payload: dict) -> User:
    """Получить текущего пользователя по payload access токена."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )

    dal = UserDAL(session)
    user = await dal.get_by_id(UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или отключён",
        )
    return user


async def create_user_admin(
    session: AsyncSession,
    data: UserCreate,
    _admin_user: User,
) -> UserCreateResponse:
    """Создание пользователя администратором с автогенерацией пароля."""
    dal = UserDAL(session)
    existing = await dal.get_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )

    password = generate_password()
    password_hash = hash_password(password)
    user = await dal.create(
        username=data.username,
        password_hash=password_hash,
        role=data.role,
    )
    await session.flush()

    return UserCreateResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        password=password,
    )


def user_to_read(user: User) -> UserRead:
    """Преобразование User в UserRead."""
    return UserRead(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
    )


def require_admin(user: User) -> None:
    """Проверка роли администратора."""
    if user.role != ADMIN_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль администратора",
        )
