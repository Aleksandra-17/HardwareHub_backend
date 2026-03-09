"""Роутер people."""

from fastapi import APIRouter

from src.database.dependencies import DbSession
from src.routers.people.actions import list_people
from src.routers.people.description import LIST_PEOPLE
from src.routers.people.schemas import PersonRead
from src.routers.people.summary import LIST_PEOPLE as LIST_SUMMARY

router = APIRouter()


@router.get(
    "/",
    response_model=list[PersonRead],
    summary=LIST_SUMMARY,
    description=LIST_PEOPLE,
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
async def get_people(session: DbSession) -> list[PersonRead]:
    """Список всех ответственных лиц."""
    return await list_people(session)
