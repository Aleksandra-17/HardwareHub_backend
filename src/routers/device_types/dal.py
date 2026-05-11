"""Data Access Layer для роутера device_types."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.device_types.models import DeviceType
from src.routers.devices.models import Device


class DeviceTypeDAL:
    """DAL для работы с типами устройств."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_with_count(self) -> list[tuple[DeviceType, int]]:
        """Получить все типы устройств с подсчётом количества устройств."""
        stmt = (
            select(DeviceType, func.count(Device.id).label("cnt"))
            .outerjoin(Device, DeviceType.id == Device.device_type_id)
            .group_by(DeviceType.id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1])) for row in result.all()]

    async def get_by_name(self, name: str) -> DeviceType | None:
        """Найти тип устройства по названию."""
        stmt = select(DeviceType).where(DeviceType.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> DeviceType | None:
        """Найти тип устройства по коду."""
        stmt = select(DeviceType).where(DeviceType.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, name: str, code: str, category: str, description: str | None
    ) -> DeviceType:
        """Создать новый тип устройства."""
        dt = DeviceType(
            name=name,
            code=code,
            category=category,
            description=description,
        )
        self.session.add(dt)
        await self.session.flush()
        return dt
