"""Бизнес-логика роутера device_types."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.device_types.dal import DeviceTypeDAL
from src.routers.device_types.schemas import DeviceTypeRead


async def list_device_types(session: AsyncSession) -> list[DeviceTypeRead]:
    """
    Получить список всех типов устройств.

    Args:
        session: Сессия БД

    Returns:
        Список типов устройств с подсчётом deviceCount
    """
    dal = DeviceTypeDAL(session)
    rows = await dal.get_all_with_count()
    return [
        DeviceTypeRead(
            id=dt.id,
            name=dt.name,
            code=dt.code,
            category=dt.category,
            description=dt.description,
            device_count=count,
        )
        for dt, count in rows
    ]
