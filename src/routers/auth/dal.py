"""Data Access Layer для auth."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.auth.models import User


class UserDAL:
    """DAL для пользователей."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Получить пользователя по username."""
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, username: str, password_hash: str, role: str = "user") -> User:
        """Создать пользователя."""
        user = User(username=username, password_hash=password_hash, role=role)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
