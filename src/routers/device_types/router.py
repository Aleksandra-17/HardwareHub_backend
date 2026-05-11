"""Роутер device_types."""

from fastapi import APIRouter, status

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.device_types.actions import create_device_type, list_device_types
from src.routers.device_types.description import LIST_DEVICE_TYPES
from src.routers.device_types.schemas import DeviceTypeCreate, DeviceTypeRead
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


@router.post(
    "/",
    response_model=DeviceTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тип устройства",
    description="Создать новый тип устройства (требует авторизации). category: computing | office | network | other",
    responses={
        201: {"description": "Тип устройства создан"},
        400: {"description": "name или code уже существуют"},
        422: {"description": "Ошибка валидации"},
    },
)
async def post_device_type(
    session: DbSession,
    data: DeviceTypeCreate,
    _user: CurrentUser,
) -> DeviceTypeRead:
    """Создать новый тип устройства."""
    return await create_device_type(session, data)
