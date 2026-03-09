"""Pydantic schemas для роутера reports."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExportRequest(BaseModel):
    """Запрос экспорта устройств."""

    model_config = ConfigDict(populate_by_name=True)

    format: str = Field(..., pattern="^(csv|xlsx)$")
    location_id: UUID | None = Field(None, alias="locationId")
    person_id: UUID | None = Field(None, alias="personId")


class InventoryRequest(BaseModel):
    """Запрос акта инвентаризации."""

    model_config = ConfigDict(populate_by_name=True)

    location_id: UUID = Field(..., alias="locationId")
    person_id: UUID = Field(..., alias="personId")
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")


class InventoryDeviceItem(BaseModel):
    """Элемент списка устройств в акте."""

    model_config = ConfigDict(populate_by_name=True)

    inventory_number: str = Field(
        ..., alias="inventoryNumber", serialization_alias="inventoryNumber"
    )
    name: str
    serial_number: str | None = Field(
        None, alias="serialNumber", serialization_alias="serialNumber"
    )
    status: str
    purchase_price: Decimal | None = Field(
        None, alias="purchasePrice", serialization_alias="purchasePrice"
    )


class InventoryResponse(BaseModel):
    """Ответ акта инвентаризации."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    document_number: str = Field(..., alias="documentNumber", serialization_alias="documentNumber")
    date: date
    location_name: str = Field(..., alias="locationName", serialization_alias="locationName")
    person_name: str = Field(..., alias="personName", serialization_alias="personName")
    device_count: int = Field(..., alias="deviceCount", serialization_alias="deviceCount")
    total_price: Decimal = Field(..., alias="totalPrice", serialization_alias="totalPrice")
    devices: list[InventoryDeviceItem]
