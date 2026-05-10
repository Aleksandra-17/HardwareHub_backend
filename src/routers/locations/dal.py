"""Data Access Layer для роутера locations."""

from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.devices.models import Device
from src.routers.device_types.models import DeviceType
from src.routers.locations.models import Location


class LocationDAL:
    """DAL для работы с локациями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_with_count(self) -> list[tuple[Location, int, int]]:
        """Все локации: (Location, число устройств, число computing-устройств)."""
        computing_per_device = case((DeviceType.category == "computing", 1), else_=0)
        stmt = (
            select(
                Location,
                func.count(Device.id),
                func.coalesce(func.sum(computing_per_device), 0),
            )
            .outerjoin(Device, Location.id == Device.location_id)
            .outerjoin(DeviceType, Device.device_type_id == DeviceType.id)
            .group_by(Location.id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1]), int(row[2])) for row in result.all()]

    async def create(self, **kwargs) -> Location:
        """Создать локацию."""
        location = Location(**kwargs)
        self.session.add(location)
        await self.session.flush()
        return location

    async def update_fields(self, location: Location, **kwargs) -> Location:
        """Обновить переданные поля."""
        for key, value in kwargs.items():
            setattr(location, key, value)
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

    async def get_device_and_computing_counts(self, location_id: UUID) -> tuple[int, int]:
        """Количество всех устройств и устройств категории computing в локации."""
        computing_per_device = case((DeviceType.category == "computing", 1), else_=0)
        stmt = (
            select(
                func.count(Device.id),
                func.coalesce(func.sum(computing_per_device), 0),
            )
            .select_from(Device)
            .outerjoin(DeviceType, Device.device_type_id == DeviceType.id)
            .where(Device.location_id == location_id)
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return int(row[0]), int(row[1])

    async def delete(self, location: Location) -> None:
        """Удалить локацию."""
        await self.session.delete(location)
        await self.session.flush()
