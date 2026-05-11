"""Роутер components."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.components.actions import (
    attach_component,
    create_component,
    delete_component,
    detach_component,
    list_components,
    update_component,
)
from src.routers.components.schemas import (
    ComponentAttach,
    ComponentCreate,
    ComponentRead,
    ComponentUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[ComponentRead],
    summary="Список комплектующих",
)
async def get_components(
    session: DbSession,
    _user: CurrentUser,
    computer_id: UUID | None = Query(None, alias="computerId"),
) -> list[ComponentRead]:
    """Получить список комплектующих."""
    return await list_components(session, computer_id=computer_id)


@router.post(
    "/",
    response_model=ComponentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать комплектующую",
)
async def post_component(
    session: DbSession,
    data: ComponentCreate,
    _user: CurrentUser,
) -> ComponentRead:
    """Создать комплектующую."""
    return await create_component(session, data)


@router.patch(
    "/{component_id}",
    response_model=ComponentRead,
    summary="Обновить комплектующую",
    responses={404: {"description": "Комплектующая не найдена"}},
)
async def patch_component(
    session: DbSession,
    component_id: UUID,
    data: ComponentUpdate,
    _user: CurrentUser,
) -> ComponentRead:
    """Обновить комплектующую."""
    return await update_component(session, component_id, data)


@router.delete(
    "/{component_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить комплектующую",
    responses={404: {"description": "Комплектующая не найдена"}},
)
async def delete_component_endpoint(
    session: DbSession,
    component_id: UUID,
    _user: CurrentUser,
) -> None:
    """Удалить комплектующую."""
    await delete_component(session, component_id)


@router.post(
    "/{component_id}/attach",
    response_model=ComponentRead,
    summary="Привязать комплектующую к ПК",
)
async def attach_component_endpoint(
    session: DbSession,
    component_id: UUID,
    data: ComponentAttach,
    _user: CurrentUser,
) -> ComponentRead:
    """Привязать комплектующую к ПК."""
    return await attach_component(session, component_id, data.computer_id)


@router.post(
    "/{component_id}/detach",
    response_model=ComponentRead,
    summary="Отвязать комплектующую от ПК",
)
async def detach_component_endpoint(
    session: DbSession,
    component_id: UUID,
    _user: CurrentUser,
) -> ComponentRead:
    """Отвязать комплектующую от ПК."""
    return await detach_component(session, component_id)
