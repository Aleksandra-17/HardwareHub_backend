"""Pydantic schemas для роутера locations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LocationRead(BaseModel):
    """Схема чтения локации."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str = Field(..., description="Название локации")
    building: str | None = Field(None, description="Корпус/здание")
    floor: str | None = Field(None, description="Этаж")
    description: str | None = Field(None, description="Описание")
    device_count: int = Field(
        0,
        description="Количество устройств",
        alias="deviceCount",
        serialization_alias="deviceCount",
    )
