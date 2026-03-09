"""Pydantic schemas для роутера people."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PersonCreate(BaseModel):
    """Схема создания ответственного лица."""

    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="ФИО",
        alias="fullName",
    )
    position: str | None = Field(None, max_length=255, description="Должность")
    department: str | None = Field(None, max_length=255, description="Отдел")
    email: str | None = Field(None, max_length=255, description="Email")
    phone: str | None = Field(None, max_length=50, description="Телефон")


class PersonRead(BaseModel):
    """Схема чтения ответственного лица."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    full_name: str = Field(
        ...,
        description="ФИО",
        alias="fullName",
        serialization_alias="fullName",
    )
    position: str | None = Field(None, description="Должность")
    department: str | None = Field(None, description="Отдел")
    email: str | None = Field(None, description="Email")
    phone: str | None = Field(None, description="Телефон")
    device_count: int = Field(
        0,
        description="Количество устройств",
        alias="deviceCount",
        serialization_alias="deviceCount",
    )
