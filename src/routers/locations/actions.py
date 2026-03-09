"""Бизнес-логика роутера locations."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.locations.dal import LocationDAL
from src.routers.locations.schemas import LocationRead


async def list_locations(session: AsyncSession) -> list[LocationRead]:
    """
    Получить список всех локаций.

    Args:
        session: Сессия БД

    Returns:
        Список локаций с подсчётом deviceCount
    """
    dal = LocationDAL(session)
    rows = await dal.get_all_with_count()
    return [
        LocationRead(
            id=loc.id,
            name=loc.name,
            building=loc.building,
            floor=loc.floor,
            description=loc.description,
            device_count=count,
        )
        for loc, count in rows
    ]
