"""Data Access Layer для роутера locations."""

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
