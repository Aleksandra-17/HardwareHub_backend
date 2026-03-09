"""Pydantic schemas для роутера device_types."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
