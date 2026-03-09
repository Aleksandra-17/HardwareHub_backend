"""Бизнес-логика роутера people."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.people.dal import PersonDAL
from src.routers.people.schemas import PersonRead


async def list_people(session: AsyncSession) -> list[PersonRead]:
    """
    Получить список всех ответственных лиц.

    Args:
        session: Сессия БД

    Returns:
        Список ответственных с подсчётом deviceCount
    """
    dal = PersonDAL(session)
    rows = await dal.get_all_with_count()
    return [
        PersonRead(
            id=p.id,
            full_name=p.full_name,
            position=p.position,
            department=p.department,
            email=p.email,
            phone=p.phone,
            device_count=count,
        )
        for p, count in rows
    ]
