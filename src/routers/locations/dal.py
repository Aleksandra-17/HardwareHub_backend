"""Data Access Layer для роутера locations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.devices.models import Device
from src.routers.locations.models import Location


class LocationDAL:
    """DAL для работы с локациями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_with_count(self) -> list[tuple[Location, int]]:
        """Получить все локации с подсчётом количества устройств."""
        stmt = (
            select(Location, func.count(Device.id).label("cnt"))
            .outerjoin(Device, Location.id == Device.location_id)
            .group_by(Location.id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1])) for row in result.all()]

    async def create(self, **kwargs) -> Location:
        """Создать локацию."""
        location = Location(**kwargs)
        self.session.add(location)
        await self.session.flush()
        return location

    async def get_by_id(self, location_id: UUID) -> Location | None:
        """Получить локацию по ID."""
        return await self.session.get(Location, location_id)

    async def count_devices(self, location_id: UUID) -> int:
        """Подсчитать устройства в локации."""
        stmt = select(func.count()).where(Device.location_id == location_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, location: Location) -> None:
        """Удалить локацию."""
        await self.session.delete(location)
        await self.session.flush()
