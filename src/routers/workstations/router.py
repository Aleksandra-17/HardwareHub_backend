"""Роутер рабочих мест."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.workstations.actions import (
    create_workstation,
    delete_workstation,
    list_for_location,
    update_workstation,
)
from src.routers.workstations.schemas import WorkstationCreate, WorkstationRead, WorkstationUpdate

router = APIRouter()


@router.get("/", response_model=list[WorkstationRead], summary="Список мест в кабинете")
async def get_workstations(
    session: DbSession,
    _user: CurrentUser,
    location_id: UUID = Query(..., alias="locationId"),
) -> list[WorkstationRead]:
    return await list_for_location(session, location_id)


@router.post("/", response_model=WorkstationRead, status_code=status.HTTP_201_CREATED, summary="Создать место")
async def post_workstation(
    session: DbSession,
    _user: CurrentUser,
    data: WorkstationCreate,
) -> WorkstationRead:
    return await create_workstation(session, data)


@router.patch("/{workstation_id}", response_model=WorkstationRead, summary="Обновить место")
async def patch_workstation(
    session: DbSession,
    _user: CurrentUser,
    workstation_id: UUID,
    data: WorkstationUpdate,
) -> WorkstationRead:
    result = await update_workstation(session, workstation_id, data)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Рабочее место не найдено")
    return result


@router.delete("/{workstation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить место")
async def delete_workstation_endpoint(
    session: DbSession,
    _user: CurrentUser,
    workstation_id: UUID,
) -> None:
    await delete_workstation(session, workstation_id)
