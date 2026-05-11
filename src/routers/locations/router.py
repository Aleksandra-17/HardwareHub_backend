"""Роутер locations."""

from uuid import UUID

from fastapi import APIRouter, status

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.locations.actions import (
    create_location,
    delete_location,
    list_locations,
    update_location,
)
from src.routers.locations.schemas import LocationCreate, LocationRead, LocationUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[LocationRead],
    summary="Список всех локаций",
    responses={
        200: {
            "description": "Список локаций",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "l1",
                            "name": "Каб. 101",
                            "building": "Корпус А",
                            "floor": "1",
                            "description": "Приёмная",
                            "workstationCapacity": 4,
                            "deviceCount": 4,
                            "computingDeviceCount": 2,
                            "workstationDeficit": 2,
                            "needsEquipment": True,
                        }
                    ]
                }
            },
        }
    },
)
async def get_locations(
    session: DbSession,
    _user: CurrentUser,
) -> list[LocationRead]:
    """Список всех локаций."""
    return await list_locations(session)


@router.post(
    "/",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать локацию",
)
async def post_location(
    session: DbSession,
    data: LocationCreate,
    _user: CurrentUser,
) -> LocationRead:
    """Создать новую локацию."""
    return await create_location(session, data)


@router.patch(
    "/{location_id}",
    response_model=LocationRead,
    summary="Обновить локацию",
)
async def patch_location(
    session: DbSession,
    location_id: UUID,
    data: LocationUpdate,
    _user: CurrentUser,
) -> LocationRead:
    """Частично обновить кабинет (в т.ч. план рабочих мест)."""
    return await update_location(session, location_id, data)


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить локацию",
    responses={
        404: {"description": "Локация не найдена"},
        409: {"description": "Нельзя удалить — есть привязанные устройства"},
    },
)
async def delete_location_endpoint(
    session: DbSession,
    location_id: UUID,
    _user: CurrentUser,
) -> None:
    """Удалить локацию. 409 если в ней есть устройства."""
    await delete_location(session, location_id)
