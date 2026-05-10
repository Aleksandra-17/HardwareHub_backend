"""Бизнес-логика роутера locations."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.routers.locations.dal import LocationDAL
from src.routers.locations.models import Location
from src.routers.locations.schemas import LocationCreate, LocationRead, LocationUpdate


def _to_read(loc: Location, device_count: int, computing_count: int) -> LocationRead:
    """Собрать ответ с метриками заполненности."""
    cap = loc.workstation_capacity
    deficit = max(0, cap - computing_count) if cap > 0 else 0
    return LocationRead(
        id=loc.id,
        name=loc.name,
        building=loc.building,
        floor=loc.floor,
        description=loc.description,
        workstation_capacity=cap,
        device_count=device_count,
        computing_device_count=computing_count,
        workstation_deficit=deficit,
        needs_equipment=deficit > 0,
    )


async def list_locations(session: AsyncSession) -> list[LocationRead]:
    """Получить список всех локаций."""
    dal = LocationDAL(session)
    rows = await dal.get_all_with_count()
    return [_to_read(loc, dev_cnt, comp_cnt) for loc, dev_cnt, comp_cnt in rows]


async def create_location(session: AsyncSession, data: LocationCreate) -> LocationRead:
    """Создать локацию."""
    dal = LocationDAL(session)
    location = await dal.create(**data.model_dump())
    return _to_read(location, 0, 0)


async def update_location(
    session: AsyncSession,
    location_id: UUID,
    data: LocationUpdate,
) -> LocationRead:
    """Обновить локацию."""
    dal = LocationDAL(session)
    location = await dal.get_by_id(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Локация не найдена")
    payload = data.model_dump(exclude_unset=True, by_alias=False)
    await dal.update_fields(location, **payload)
    dev_cnt, comp_cnt = await dal.get_device_and_computing_counts(location_id)
    return _to_read(location, dev_cnt, comp_cnt)


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
