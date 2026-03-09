"""Бизнес-логика роутера locations."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.routers.locations.dal import LocationDAL
from src.routers.locations.schemas import LocationCreate, LocationRead


async def list_locations(session: AsyncSession) -> list[LocationRead]:
    """Получить список всех локаций."""
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


async def create_location(session: AsyncSession, data: LocationCreate) -> LocationRead:
    """Создать локацию."""
    dal = LocationDAL(session)
    location = await dal.create(**data.model_dump())
    return LocationRead(
        id=location.id,
        name=location.name,
        building=location.building,
        floor=location.floor,
        description=location.description,
        device_count=0,
    )


async def delete_location(session: AsyncSession, location_id: UUID) -> None:
    """Удалить локацию. 409 если есть привязанные устройства."""
    dal = LocationDAL(session)
    location = await dal.get_by_id(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Локация не найдена")
    count = await dal.count_devices(location_id)
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Нельзя удалить: в локации {count} устройств",
        )
    await dal.delete(location)
