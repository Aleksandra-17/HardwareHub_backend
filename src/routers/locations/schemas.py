"""Pydantic schemas для роутера locations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    """Схема создания локации."""

    name: str = Field(..., min_length=1, max_length=255, description="Название локации")
    building: str | None = Field(None, max_length=255, description="Корпус/здание")
    floor: str | None = Field(None, max_length=50, description="Этаж")
    description: str | None = Field(None, description="Описание")


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
