"""Роутер devices."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from src.database.dependencies import DbSession
from src.routers.devices.actions import (
    create_device,
    delete_device,
    get_device,
    get_device_audit,
    list_devices,
    update_device,
)
from src.routers.devices.description import (
    CREATE_DEVICE,
    DELETE_DEVICE,
    GET_DEVICE,
    GET_DEVICE_AUDIT,
    LIST_DEVICES,
    UPDATE_DEVICE,
)
from src.routers.devices.schemas import AuditEntryRead, DeviceCreate, DeviceRead, DeviceUpdate
from src.routers.devices.summary import (
    CREATE_DEVICE as CREATE_SUMMARY,
)
from src.routers.devices.summary import (
    DELETE_DEVICE as DELETE_SUMMARY,
)
from src.routers.devices.summary import (
    GET_DEVICE as GET_SUMMARY,
)
from src.routers.devices.summary import (
    GET_DEVICE_AUDIT as AUDIT_SUMMARY,
)
from src.routers.devices.summary import (
    LIST_DEVICES as LIST_SUMMARY,
)
from src.routers.devices.summary import (
    UPDATE_DEVICE as UPDATE_SUMMARY,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[DeviceRead],
    summary=LIST_SUMMARY,
    description=LIST_DEVICES,
)
async def get_devices(
    session: DbSession,
    search: str | None = Query(None, description="Поиск по inventoryNumber, name, serialNumber"),
    status: str | None = Query(None, description="Фильтр по статусу или all"),
    type: str | None = Query(None, alias="type", description="Фильтр по deviceTypeId или all"),
    location: str | None = Query(None, description="Фильтр по locationId или all"),
    person: str | None = Query(None, description="Фильтр по personId или all"),
    sort: str = Query("inventoryNumber", description="Поле сортировки"),
    order: str = Query("asc", description="asc или desc"),
) -> list[DeviceRead]:
    """Список устройств с фильтрацией."""
    return await list_devices(
        session,
        search=search,
        status=status,
        device_type_id=type,
        location_id=location,
        person_id=person,
        sort=sort,
        order=order,
    )


@router.get(
    "/{device_id}/audit",
    response_model=list[AuditEntryRead],
    summary=AUDIT_SUMMARY,
    description=GET_DEVICE_AUDIT,
    responses={404: {"description": "Устройство не найдено"}},
)
async def get_audit_by_device_id(
    session: DbSession,
    device_id: UUID,
) -> list[AuditEntryRead]:
    """История изменений устройства."""
    entries = await get_device_audit(session, device_id)
    if entries is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return entries


@router.get(
    "/{device_id}",
    response_model=DeviceRead,
    summary=GET_SUMMARY,
    description=GET_DEVICE,
    responses={404: {"description": "Устройство не найдено"}},
)
async def get_device_by_id(
    session: DbSession,
    device_id: UUID,
) -> DeviceRead:
    """Получить устройство по ID."""
    device = await get_device(session, device_id)
    if device is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


@router.post(
    "/",
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED,
    summary=CREATE_SUMMARY,
    description=CREATE_DEVICE,
)
async def post_device(session: DbSession, data: DeviceCreate) -> DeviceRead:
    """Создать устройство."""
    return await create_device(session, data)


@router.patch(
    "/{device_id}",
    response_model=DeviceRead,
    summary=UPDATE_SUMMARY,
    description=UPDATE_DEVICE,
    responses={404: {"description": "Устройство не найдено"}},
)
async def patch_device(
    session: DbSession,
    device_id: UUID,
    data: DeviceUpdate,
) -> DeviceRead:
    """Обновить устройство."""
    device = await update_device(session, device_id, data)
    if device is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


@router.put(
    "/{device_id}",
    response_model=DeviceRead,
    summary=UPDATE_SUMMARY,
    description=UPDATE_DEVICE,
    responses={404: {"description": "Устройство не найдено"}},
)
async def put_device(
    session: DbSession,
    device_id: UUID,
    data: DeviceUpdate,
) -> DeviceRead:
    """Обновить устройство (PUT)."""
    return await patch_device(session, device_id, data)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=DELETE_SUMMARY,
    description=DELETE_DEVICE,
    responses={404: {"description": "Устройство не найдено"}},
)
async def delete_device_by_id(session: DbSession, device_id: UUID) -> None:
    """Удалить устройство."""
    deleted = await delete_device(session, device_id)
    if not deleted:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Устройство не найдено")
