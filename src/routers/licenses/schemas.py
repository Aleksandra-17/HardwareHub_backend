"""Pydantic schemas для роутера licenses."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LicenseCreate(BaseModel):
    """Схема создания лицензии."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., ge=0)
    expires_at: date = Field(..., alias="expiresAt")
    details: str | None = Field(None, max_length=2000)


class LicenseUpdate(BaseModel):
    """Схема частичного обновления лицензии."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str | None = Field(None, min_length=1, max_length=255)
    price: Decimal | None = Field(None, ge=0)
    expires_at: date | None = Field(None, alias="expiresAt")
    details: str | None = Field(None, max_length=2000)


class LicenseRead(BaseModel):
    """Схема чтения лицензии."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    price: Decimal
    expires_at: date = Field(
        ...,
        alias="expiresAt",
        serialization_alias="expiresAt",
    )
    details: str | None = None
