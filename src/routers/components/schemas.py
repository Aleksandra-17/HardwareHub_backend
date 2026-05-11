"""Pydantic schemas для роутера components."""

from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.routers.devices.enums import DeviceStatus


class ComponentType(StrEnum):
    CPU = "cpu"
    MOTHERBOARD = "motherboard"
    RAM = "ram"
    STORAGE = "storage"
    PSU = "psu"
    GPU = "gpu"
    CASE = "case"
    COOLER = "cooler"


class ComponentCreate(BaseModel):
    """Схема создания комплектующей."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=255)
    component_type: ComponentType = Field(..., alias="componentType")
    status: DeviceStatus = DeviceStatus.IN_USE
    arrival_date: date | None = Field(None, alias="arrivalDate")
    expiry_date: date | None = Field(None, alias="expiryDate")
    notes: str | None = None
    linked_computer_id: UUID | None = Field(None, alias="linkedComputerId")


class ComponentUpdate(BaseModel):
    """Схема частичного обновления комплектующей."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str | None = Field(None, min_length=1, max_length=255)
    component_type: ComponentType | None = Field(None, alias="componentType")
    status: DeviceStatus | None = None
    arrival_date: date | None = Field(None, alias="arrivalDate")
    expiry_date: date | None = Field(None, alias="expiryDate")
    notes: str | None = None


class ComponentRead(BaseModel):
    """Схема чтения комплектующей."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    component_type: ComponentType = Field(
        ...,
        alias="componentType",
        serialization_alias="componentType",
    )
    status: DeviceStatus
    arrival_date: date | None = Field(
        None,
        alias="arrivalDate",
        serialization_alias="arrivalDate",
    )
    expiry_date: date | None = Field(
        None,
        alias="expiryDate",
        serialization_alias="expiryDate",
    )
    notes: str | None = None
    linked_computer_id: UUID | None = Field(
        None,
        alias="linkedComputerId",
        serialization_alias="linkedComputerId",
    )


class ComponentAttach(BaseModel):
    """Схема привязки комплектующей к ПК."""

    model_config = ConfigDict(populate_by_name=True)

    computer_id: UUID = Field(..., alias="computerId")
