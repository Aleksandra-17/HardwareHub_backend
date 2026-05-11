"""Pydantic schemas для роутера locations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    """Схема создания локации."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=255, description="Название локации")
    building: str | None = Field(None, max_length=255, description="Корпус/здание")
    floor: str | None = Field(None, max_length=50, description="Этаж")
    description: str | None = Field(None, description="Описание")
    workstation_capacity: int = Field(
        0,
        ge=0,
        description="Плановое число рабочих мест в кабинете",
        alias="workstationCapacity",
    )


class LocationUpdate(BaseModel):
    """Схема частичного обновления локации."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str | None = Field(None, min_length=1, max_length=255)
    building: str | None = Field(None, max_length=255)
    floor: str | None = Field(None, max_length=50)
    description: str | None = None
    workstation_capacity: int | None = Field(
        None,
        ge=0,
        alias="workstationCapacity",
    )


class LocationRead(BaseModel):
    """Схема чтения локации."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str = Field(..., description="Название локации")
    building: str | None = Field(None, description="Корпус/здание")
    floor: str | None = Field(None, description="Этаж")
    description: str | None = Field(None, description="Описание")
    workstation_capacity: int = Field(
        0,
        description="Плановое число рабочих мест",
        alias="workstationCapacity",
        serialization_alias="workstationCapacity",
    )
    device_count: int = Field(
        0,
        description="Количество устройств",
        alias="deviceCount",
        serialization_alias="deviceCount",
    )
    computing_device_count: int = Field(
        0,
        description="Устройства с типом категории computing (ПК, ноутбук и т.п.)",
        alias="computingDeviceCount",
        serialization_alias="computingDeviceCount",
    )
    workstation_deficit: int = Field(
        0,
        description="Не хватает единиц computing-техники до плана мест (0 если план не задан)",
        alias="workstationDeficit",
        serialization_alias="workstationDeficit",
    )
    needs_equipment: bool = Field(
        False,
        description="True если задан план мест и computing-техники меньше плана",
        alias="needsEquipment",
        serialization_alias="needsEquipment",
    )
