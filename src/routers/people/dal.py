"""Data Access Layer для роутера people."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.devices.models import Device
from src.routers.people.models import Person


class PersonDAL:
    """DAL для работы с ответственными лицами."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_with_count(self) -> list[tuple[Person, int]]:
        """Получить всех ответственных с подсчётом количества устройств."""
        stmt = (
            select(Person, func.count(Device.id).label("cnt"))
            .outerjoin(Device, Person.id == Device.person_id)
            .group_by(Person.id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1])) for row in result.all()]

    async def create(self, **kwargs) -> Person:
        """Создать ответственное лицо."""
        person = Person(**kwargs)
        self.session.add(person)
        await self.session.flush()
        return person

    async def get_by_id(self, person_id: UUID) -> Person | None:
        """Получить ответственное лицо по ID."""
        return await self.session.get(Person, person_id)

    async def count_devices(self, person_id: UUID) -> int:
        """Подсчитать устройства, закреплённые за ответственным."""
        stmt = select(func.count()).where(Device.person_id == person_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, person: Person) -> None:
        """Удалить ответственное лицо."""
        await self.session.delete(person)
        await self.session.flush()
