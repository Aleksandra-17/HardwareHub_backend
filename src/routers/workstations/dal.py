"""DAL рабочих мест."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.routers.devices.models import Device
from src.routers.workstations.models import Workstation, WorkstationRequirement


class WorkstationDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_location(self, location_id: UUID) -> list[Workstation]:
        stmt = (
            select(Workstation)
            .options(
                selectinload(Workstation.requirements).selectinload(WorkstationRequirement.device_type),
            )
            .where(Workstation.location_id == location_id)
            .order_by(Workstation.seat_code)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, workstation_id: UUID) -> Workstation | None:
        stmt = (
            select(Workstation)
            .options(
                selectinload(Workstation.requirements).selectinload(WorkstationRequirement.device_type),
            )
            .where(Workstation.id == workstation_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def count_devices(self, workstation_id: UUID) -> int:
        q = select(func.count()).where(Device.workstation_id == workstation_id)
        res = await self.session.execute(q)
        return res.scalar_one()

    async def create(self, workstation: Workstation) -> Workstation:
        self.session.add(workstation)
        await self.session.flush()
        await self.session.refresh(workstation)
        return workstation

    async def delete(self, workstation: Workstation) -> None:
        await self.session.delete(workstation)
        await self.session.flush()
