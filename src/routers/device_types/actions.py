"""Бизнес-логика роутера device_types."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.device_types.dal import DeviceTypeDAL
from src.routers.device_types.schemas import DeviceTypeCreate, DeviceTypeRead


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


async def create_device_type(session: AsyncSession, data: DeviceTypeCreate) -> DeviceTypeRead:
    """
    Создать новый тип устройства.

    Args:
        session: Сессия БД
        data: Данные для создания

    Returns:
        Созданный тип устройства

    Raises:
        HTTPException: 400 если name или code уже существуют
    """
    dal = DeviceTypeDAL(session)
    if await dal.get_by_name(data.name):
        raise HTTPException(
            status_code=400,
            detail="Тип устройства с таким названием уже существует",
        )
    if await dal.get_by_code(data.code):
        raise HTTPException(
            status_code=400,
            detail="Тип устройства с таким кодом уже существует",
        )
    dt = await dal.create(
        name=data.name,
        code=data.code,
        category=data.category.value,
        description=data.description,
    )
    return DeviceTypeRead(
        id=dt.id,
        name=dt.name,
        code=dt.code,
        category=dt.category,
        description=dt.description,
        device_count=0,
    )
