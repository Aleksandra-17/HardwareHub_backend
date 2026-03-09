"""Data Access Layer для роутера people."""

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
