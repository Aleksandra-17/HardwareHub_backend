"""Роутер locations."""

from fastapi import APIRouter

from src.database.dependencies import DbSession
from src.routers.locations.actions import list_locations
from src.routers.locations.description import LIST_LOCATIONS
from src.routers.locations.schemas import LocationRead
from src.routers.locations.summary import LIST_LOCATIONS as LIST_SUMMARY

router = APIRouter()


@router.get(
    "/",
    response_model=list[LocationRead],
    summary=LIST_SUMMARY,
    description=LIST_LOCATIONS,
    responses={
        200: {
            "description": "Список локаций",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "l1",
                            "name": "Каб. 101",
                            "building": "Корпус А",
                            "floor": "1",
                            "description": "Приёмная",
                            "deviceCount": 4,
                        }
                    ]
                }
            },
        }
    },
)
async def get_locations(session: DbSession) -> list[LocationRead]:
    """Список всех локаций."""
    return await list_locations(session)
