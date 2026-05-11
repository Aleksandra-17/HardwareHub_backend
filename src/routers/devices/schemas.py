"""Pydantic schemas для роутера devices."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.routers.components.schemas import ComponentType
from src.routers.devices.enums import DeviceStatus


class DeviceComponentCreate(BaseModel):
    """Комплектующая для создания вместе с устройством."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=255)
    component_type: ComponentType = Field(..., alias="componentType")
    status: DeviceStatus = DeviceStatus.IN_USE
    arrival_date: date | None = Field(None, alias="arrivalDate")
    expiry_date: date | None = Field(None, alias="expiryDate")
    notes: str | None = None


class DeviceComponentRead(BaseModel):
    """Комплектующая в карточке устройства."""

    model_config = ConfigDict(populate_by_name=True)

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


class DeviceRead(BaseModel):
    """Схема чтения устройства."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    id: UUID
    inventory_number: str = Field(..., alias="inventoryNumber")
    name: str
    device_type_id: UUID | None = Field(None, alias="deviceTypeId")
    serial_number: str | None = Field(None, alias="serialNumber")
    model: str | None = None
    manufacturer: str | None = None
    status: DeviceStatus
    location_id: UUID | None = Field(None, alias="locationId")
    workstation_id: UUID | None = Field(None, alias="workstationId")
    workstation_seat_code: str | None = Field(None, alias="workstationSeatCode")
    person_id: UUID | None = Field(None, alias="personId")
    commission_date: date | None = Field(None, alias="commissionDate")
    last_check_date: date | None = Field(None, alias="lastCheckDate")
    notes: str | None = None
    purchase_price: Decimal | None = Field(None, alias="purchasePrice")
    purchase_date: date | None = Field(None, alias="purchaseDate")
    qr_code: str | None = Field(None, alias="qrCode")
    components: list[DeviceComponentRead] = []


class DeviceCreate(BaseModel):
    """Схема создания устройства."""

    model_config = ConfigDict(populate_by_name=True)

    inventory_number: str = Field(..., alias="inventoryNumber")
    name: str
    device_type_id: UUID = Field(..., alias="deviceTypeId")
    serial_number: str | None = Field(None, alias="serialNumber")
    model: str | None = None
    manufacturer: str | None = None
    status: DeviceStatus
    location_id: UUID | None = Field(None, alias="locationId")
    workstation_id: UUID | None = Field(None, alias="workstationId")
    person_id: UUID | None = Field(None, alias="personId")
    commission_date: date | None = Field(None, alias="commissionDate")
    last_check_date: date | None = Field(None, alias="lastCheckDate")
    notes: str | None = None
    purchase_price: Decimal | None = Field(None, alias="purchasePrice")
    purchase_date: date | None = Field(None, alias="purchaseDate")
    qr_code: str | None = Field(None, alias="qrCode")
    components: list[DeviceComponentCreate] = []


class DeviceUpdate(BaseModel):
    """Схема частичного обновления устройства."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    inventory_number: str | None = Field(None, alias="inventoryNumber")
    name: str | None = None
    device_type_id: UUID | None = Field(None, alias="deviceTypeId")
    serial_number: str | None = Field(None, alias="serialNumber")
    model: str | None = None
    manufacturer: str | None = None
    status: DeviceStatus | None = None
    location_id: UUID | None = Field(None, alias="locationId")
    workstation_id: UUID | None = Field(None, alias="workstationId")
    person_id: UUID | None = Field(None, alias="personId")
    commission_date: date | None = Field(None, alias="commissionDate")
    last_check_date: date | None = Field(None, alias="lastCheckDate")
    notes: str | None = None
    purchase_price: Decimal | None = Field(None, alias="purchasePrice")
    purchase_date: date | None = Field(None, alias="purchaseDate")
    qr_code: str | None = Field(None, alias="qrCode")


class DeviceRebuildItem(BaseModel):
    """Одна позиция для пересборки ПК."""

    model_config = ConfigDict(populate_by_name=True)

    component_id: UUID = Field(..., alias="componentId")
    component_type: ComponentType = Field(..., alias="componentType")


class DeviceRebuild(BaseModel):
    """Пакетная пересборка ПК."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[DeviceRebuildItem]


class QRCodeResponse(BaseModel):
    """QR-код в формате base64 data URI."""

    model_config = ConfigDict(populate_by_name=True)

    qr_code: str = Field(..., alias="qrCode", serialization_alias="qrCode")


class AuditEntryRead(BaseModel):
    """Схема чтения записи аудита."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    date: date
    action: str
    user: str
