"""Бизнес-логика роутера licenses."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.routers.licenses.dal import LicenseDAL
from src.routers.licenses.schemas import LicenseCreate, LicenseRead, LicenseUpdate


async def list_licenses(session: AsyncSession) -> list[LicenseRead]:
    """Получить список лицензий."""
    dal = LicenseDAL(session)
    items = await dal.get_all()
    return [LicenseRead.model_validate(item) for item in items]


async def create_license(session: AsyncSession, data: LicenseCreate) -> LicenseRead:
    """Создать лицензию."""
    dal = LicenseDAL(session)
    try:
        item = await dal.create(**data.model_dump())
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Лицензия с таким названием уже существует",
        ) from exc
    return LicenseRead.model_validate(item)


async def update_license(
    session: AsyncSession,
    license_id: UUID,
    data: LicenseUpdate,
) -> LicenseRead:
    """Обновить лицензию."""
    dal = LicenseDAL(session)
    item = await dal.get_by_id(license_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Лицензия не найдена")
    payload = data.model_dump(exclude_unset=True, by_alias=False)
    try:
        await dal.update_fields(item, **payload)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Лицензия с таким названием уже существует",
        ) from exc
    return LicenseRead.model_validate(item)


async def delete_license(session: AsyncSession, license_id: UUID) -> None:
    """Удалить лицензию."""
    dal = LicenseDAL(session)
    item = await dal.get_by_id(license_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Лицензия не найдена")
    await dal.delete(item)
