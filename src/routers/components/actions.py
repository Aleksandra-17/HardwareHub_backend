"""Бизнес-логика роутера components."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.routers.components.dal import ComponentDAL
from src.routers.components.schemas import ComponentCreate, ComponentRead, ComponentUpdate


async def _ensure_computer(session: AsyncSession, computer_id: UUID) -> None:
    dal = ComponentDAL(session)
    device = await dal.get_device_with_type(computer_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компьютер не найден")
    if not dal.is_components_host_device(device):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="К комплектующим можно привязать только ПК или сервер",
        )


async def _to_read(session: AsyncSession, component) -> ComponentRead:
    dal = ComponentDAL(session)
    linked = await dal.get_computer_for_component(component.id)
    return ComponentRead(
        id=component.id,
        name=component.name,
        component_type=component.component_type,
        status=component.status,
        arrival_date=component.arrival_date,
        expiry_date=component.expiry_date,
        notes=component.notes,
        linked_computer_id=linked,
    )


async def list_components(session: AsyncSession, computer_id: UUID | None = None) -> list[ComponentRead]:
    """Список комплектующих."""
    dal = ComponentDAL(session)
    items = await dal.get_list(computer_id=computer_id)
    return [await _to_read(session, item) for item in items]


async def create_component(session: AsyncSession, data: ComponentCreate) -> ComponentRead:
    """Создать комплектующую."""
    dal = ComponentDAL(session)
    component = await dal.create(
        name=data.name,
        component_type=data.component_type.value,
        status=data.status.value,
        arrival_date=data.arrival_date,
        expiry_date=data.expiry_date,
        notes=data.notes,
    )
    if data.linked_computer_id is not None:
        await _ensure_computer(session, data.linked_computer_id)
        try:
            await dal.attach(component.id, data.linked_computer_id)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Комплектующая уже привязана к другому ПК",
            ) from exc
    return await _to_read(session, component)


async def update_component(
    session: AsyncSession,
    component_id: UUID,
    data: ComponentUpdate,
) -> ComponentRead:
    """Обновить комплектующую."""
    dal = ComponentDAL(session)
    component = await dal.get_by_id(component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комплектующая не найдена")
    payload = data.model_dump(exclude_unset=True, by_alias=False)
    if "component_type" in payload and payload["component_type"] is not None:
        payload["component_type"] = payload["component_type"].value
    if "status" in payload and payload["status"] is not None:
        payload["status"] = payload["status"].value
    await dal.update(component, **payload)
    return await _to_read(session, component)


async def delete_component(session: AsyncSession, component_id: UUID) -> None:
    """Удалить комплектующую."""
    dal = ComponentDAL(session)
    component = await dal.get_by_id(component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комплектующая не найдена")
    await dal.delete(component)


async def attach_component(session: AsyncSession, component_id: UUID, computer_id: UUID) -> ComponentRead:
    """Привязать комплектующую к ПК."""
    dal = ComponentDAL(session)
    component = await dal.get_by_id(component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комплектующая не найдена")
    await _ensure_computer(session, computer_id)
    await dal.attach(component_id, computer_id)
    return await _to_read(session, component)


async def detach_component(session: AsyncSession, component_id: UUID) -> ComponentRead:
    """Отвязать комплектующую от ПК."""
    dal = ComponentDAL(session)
    component = await dal.get_by_id(component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комплектующая не найдена")
    await dal.detach(component_id)
    return await _to_read(session, component)
