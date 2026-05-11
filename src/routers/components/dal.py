"""Data Access Layer для роутера components."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.routers.components.models import Component, ComputerComponent
from src.routers.device_types.models import DeviceType
from src.routers.devices.models import Device


class ComponentDAL:
    """DAL для компонентов и привязок к ПК."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(self, computer_id: UUID | None = None) -> list[Component]:
        stmt = select(Component).options(selectinload(Component.links)).order_by(Component.name.asc())
        if computer_id is not None:
            stmt = stmt.join(ComputerComponent).where(ComputerComponent.computer_id == computer_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, component_id: UUID) -> Component | None:
        stmt = (
            select(Component)
            .options(selectinload(Component.links))
            .where(Component.id == component_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Component:
        component = Component(**kwargs)
        self.session.add(component)
        await self.session.flush()
        await self.session.refresh(component)
        return component

    async def update(self, component: Component, **kwargs) -> Component:
        for key, value in kwargs.items():
            setattr(component, key, value)
        await self.session.flush()
        await self.session.refresh(component)
        return component

    async def delete(self, component: Component) -> None:
        await self.session.delete(component)

    async def get_link(self, component_id: UUID) -> ComputerComponent | None:
        stmt = select(ComputerComponent).where(ComputerComponent.component_id == component_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def attach(self, component_id: UUID, computer_id: UUID) -> None:
        link = await self.get_link(component_id)
        if link is None:
            self.session.add(ComputerComponent(component_id=component_id, computer_id=computer_id))
        else:
            link.computer_id = computer_id
        await self.session.flush()

    async def detach(self, component_id: UUID) -> None:
        link = await self.get_link(component_id)
        if link is None:
            return
        await self.session.delete(link)
        await self.session.flush()

    async def get_computer_for_component(self, component_id: UUID) -> UUID | None:
        link = await self.get_link(component_id)
        return None if link is None else link.computer_id

    async def get_device_with_type(self, device_id: UUID) -> Device | None:
        stmt = (
            select(Device)
            .options(selectinload(Device.device_type))
            .where(Device.id == device_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def is_components_host_device(device: Device | None) -> bool:
        if device is None:
            return False
        dt: DeviceType | None = device.device_type
        if dt is None:
            return False
        code = (dt.code or "").upper()
        name = (dt.name or "").strip().lower()
        return code in {"PC", "SRV"} or name in {"пк", "сервер"}
