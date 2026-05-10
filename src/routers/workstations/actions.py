"""Бизнес-логика рабочих мест."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.routers.workstations.dal import WorkstationDAL
from src.routers.workstations.models import Workstation, WorkstationRequirement
from src.routers.workstations.schemas import (
    WorkstationCreate,
    WorkstationRead,
    WorkstationRequirementRead,
    WorkstationUpdate,
)


def _requirement_to_read(r: WorkstationRequirement) -> WorkstationRequirementRead:
    name = ""
    if r.device_type is not None:
        name = r.device_type.name
    return WorkstationRequirementRead(
        id=r.id,
        device_type_id=r.device_type_id,
        device_type_name=name,
        quantity=r.quantity,
    )


def _to_read(ws: Workstation) -> WorkstationRead:
    return WorkstationRead(
        id=ws.id,
        location_id=ws.location_id,
        seat_code=ws.seat_code,
        employee_internal_email=ws.employee_internal_email,
        requirements=[_requirement_to_read(r) for r in ws.requirements],
    )


async def list_for_location(session: AsyncSession, location_id: UUID) -> list[WorkstationRead]:
    dal = WorkstationDAL(session)
    rows = await dal.list_by_location(location_id)
    return [_to_read(w) for w in rows]


async def create_workstation(session: AsyncSession, data: WorkstationCreate) -> WorkstationRead:
    ws = Workstation(
        location_id=data.location_id,
        seat_code=data.seat_code.strip(),
        employee_internal_email=data.employee_internal_email.strip()
        if data.employee_internal_email
        else None,
    )
    for req in data.requirements:
        ws.requirements.append(
            WorkstationRequirement(
                device_type_id=req.device_type_id,
                quantity=req.quantity,
            )
        )
    dal = WorkstationDAL(session)
    try:
        await dal.create(ws)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Рабочее место с таким номером уже есть в этом кабинете",
        ) from exc
    await session.refresh(ws, attribute_names=["requirements"])
    ws = await dal.get_by_id(ws.id)
    assert ws is not None
    return _to_read(ws)


async def update_workstation(
    session: AsyncSession,
    workstation_id: UUID,
    data: WorkstationUpdate,
) -> WorkstationRead | None:
    dal = WorkstationDAL(session)
    ws = await dal.get_by_id(workstation_id)
    if ws is None:
        return None
    if data.seat_code is not None:
        ws.seat_code = data.seat_code.strip()
    if data.employee_internal_email is not None:
        ws.employee_internal_email = data.employee_internal_email.strip() or None
    if data.requirements is not None:
        ws.requirements.clear()
        await session.flush()
        for req in data.requirements:
            ws.requirements.append(
                WorkstationRequirement(device_type_id=req.device_type_id, quantity=req.quantity)
            )
    try:
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Рабочее место с таким номером уже есть в этом кабинете",
        ) from exc
    refreshed = await dal.get_by_id(workstation_id)
    assert refreshed is not None
    return _to_read(refreshed)


async def delete_workstation(session: AsyncSession, workstation_id: UUID) -> None:
    dal = WorkstationDAL(session)
    ws = await dal.get_by_id(workstation_id)
    if ws is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Рабочее место не найдено")
    n = await dal.count_devices(workstation_id)
    if n > 0:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Нельзя удалить: к месту привязано {n} устройств",
        )
    await dal.delete(ws)
