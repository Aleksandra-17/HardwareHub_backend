"""Бизнес-логика роутера people."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.routers.people.dal import PersonDAL
from src.routers.people.schemas import PersonCreate, PersonRead


async def list_people(session: AsyncSession) -> list[PersonRead]:
    """Получить список всех ответственных лиц."""
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


async def create_person(session: AsyncSession, data: PersonCreate) -> PersonRead:
    """Создать ответственное лицо."""
    dal = PersonDAL(session)
    person = await dal.create(**data.model_dump(by_alias=False))
    return PersonRead(
        id=person.id,
        full_name=person.full_name,
        position=person.position,
        department=person.department,
        email=person.email,
        phone=person.phone,
        device_count=0,
    )


async def delete_person(session: AsyncSession, person_id: UUID) -> None:
    """Удалить ответственное лицо. 409 если есть привязанные устройства."""
    dal = PersonDAL(session)
    person = await dal.get_by_id(person_id)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ответственное лицо не найдено"
        )
    count = await dal.count_devices(person_id)
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Нельзя удалить: за лицом закреплено {count} устройств",
        )
    await dal.delete(person)
