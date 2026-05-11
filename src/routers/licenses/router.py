"""Роутер licenses."""

from uuid import UUID

from fastapi import APIRouter, status

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.licenses.actions import (
    create_license,
    delete_license,
    list_licenses,
    update_license,
)
from src.routers.licenses.schemas import LicenseCreate, LicenseRead, LicenseUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[LicenseRead],
    summary="Список лицензий",
)
async def get_licenses(
    session: DbSession,
    _user: CurrentUser,
) -> list[LicenseRead]:
    """Список всех лицензий."""
    return await list_licenses(session)


@router.post(
    "/",
    response_model=LicenseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать лицензию",
)
async def post_license(
    session: DbSession,
    data: LicenseCreate,
    _user: CurrentUser,
) -> LicenseRead:
    """Создать лицензию."""
    return await create_license(session, data)


@router.patch(
    "/{license_id}",
    response_model=LicenseRead,
    summary="Обновить лицензию",
    responses={404: {"description": "Лицензия не найдена"}},
)
async def patch_license(
    session: DbSession,
    license_id: UUID,
    data: LicenseUpdate,
    _user: CurrentUser,
) -> LicenseRead:
    """Обновить лицензию."""
    return await update_license(session, license_id, data)


@router.delete(
    "/{license_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить лицензию",
    responses={404: {"description": "Лицензия не найдена"}},
)
async def delete_license_endpoint(
    session: DbSession,
    license_id: UUID,
    _user: CurrentUser,
) -> None:
    """Удалить лицензию."""
    await delete_license(session, license_id)
