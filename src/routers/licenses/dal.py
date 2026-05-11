"""Data Access Layer для роутера licenses."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.licenses.models import License


class LicenseDAL:
    """DAL для работы с лицензиями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[License]:
        """Получить все лицензии."""
        stmt = select(License).order_by(License.name.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, license_id: UUID) -> License | None:
        """Получить лицензию по ID."""
        return await self.session.get(License, license_id)

    async def create(self, **kwargs) -> License:
        """Создать лицензию."""
        license_item = License(**kwargs)
        self.session.add(license_item)
        await self.session.flush()
        return license_item

    async def update_fields(self, license_item: License, **kwargs) -> License:
        """Обновить переданные поля лицензии."""
        for key, value in kwargs.items():
            setattr(license_item, key, value)
        await self.session.flush()
        return license_item

    async def delete(self, license_item: License) -> None:
        """Удалить лицензию."""
        await self.session.delete(license_item)
        await self.session.flush()
