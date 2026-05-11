"""Pydantic schemas для роутера device_types."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.routers.device_types.enums import Category


class DeviceTypeCreate(BaseModel):
    """Схема создания типа устройства."""

    name: str = Field(..., min_length=1, max_length=255, description="Название типа устройства")
    code: str = Field(..., min_length=1, max_length=50, description="Код типа (например, NB-001)")
    category: Category = Field(..., description="Категория: computing, office, network, other")
    description: str | None = Field(None, max_length=2000, description="Описание")


class DeviceTypeRead(BaseModel):
    """Схема чтения типа устройства."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str = Field(..., description="Название типа устройства")
    code: str = Field(..., description="Код типа (например, NB-001)")
    category: str = Field(..., description="Категория: computing, office, network, other")
    description: str | None = Field(None, description="Описание")
    device_count: int = Field(
        0,
        description="Количество устройств",
        alias="deviceCount",
        serialization_alias="deviceCount",
    )
