"""Роутер people."""

from uuid import UUID

from fastapi import APIRouter, status

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.people.actions import create_person, delete_person, list_people
from src.routers.people.schemas import PersonCreate, PersonRead

router = APIRouter()


@router.get(
    "/",
    response_model=list[PersonRead],
    summary="Список всех ответственных лиц",
    responses={
        200: {
            "description": "Список ответственных лиц",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "p1",
                            "fullName": "Иванов Иван Иванович",
                            "position": "Системный администратор",
                            "department": "IT-отдел",
                            "email": "ivanov@company.ru",
                            "phone": "+7 (999) 111-22-33",
                            "deviceCount": 5,
                        }
                    ]
                }
            },
        }
    },
)
async def get_people(
    session: DbSession,
    _user: CurrentUser,
) -> list[PersonRead]:
    """Список всех ответственных лиц."""
    return await list_people(session)


@router.post(
    "/",
    response_model=PersonRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать ответственное лицо",
)
async def post_person(
    session: DbSession,
    data: PersonCreate,
    _user: CurrentUser,
) -> PersonRead:
    """Создать нового ответственного."""
    return await create_person(session, data)


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ответственное лицо",
    responses={
        404: {"description": "Ответственное лицо не найдено"},
        409: {"description": "Нельзя удалить — есть привязанные устройства"},
    },
)
async def delete_person_endpoint(
    session: DbSession,
    person_id: UUID,
    _user: CurrentUser,
) -> None:
    """Удалить ответственное лицо. 409 если за ним закреплены устройства."""
    await delete_person(session, person_id)
