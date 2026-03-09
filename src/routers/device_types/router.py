"""Роутер device_types."""

from fastapi import APIRouter

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.device_types.actions import list_device_types
from src.routers.device_types.description import LIST_DEVICE_TYPES
from src.routers.device_types.schemas import DeviceTypeRead
from src.routers.device_types.summary import LIST_DEVICE_TYPES as LIST_SUMMARY

router = APIRouter()


@router.get(
    "/",
    response_model=list[DeviceTypeRead],
    summary=LIST_SUMMARY,
    description=LIST_DEVICE_TYPES,
    responses={
        200: {
            "description": "Список типов устройств",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "dt1",
                            "name": "Ноутбук",
                            "code": "NB-001",
                            "category": "computing",
                            "description": "Портативный компьютер",
                            "deviceCount": 12,
                        }
                    ]
                }
            },
        }
    },
)
async def get_device_types(
    session: DbSession,
    _user: CurrentUser,
) -> list[DeviceTypeRead]:
    """Список всех типов устройств."""
    return await list_device_types(session)
