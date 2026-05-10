"""Схемы рабочих мест."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequirementItemCreate(BaseModel):
    """Строка требований при создании/обновлении."""

    model_config = ConfigDict(populate_by_name=True)

    device_type_id: UUID = Field(..., alias="deviceTypeId")
    quantity: int = Field(..., ge=1)


class WorkstationRequirementRead(BaseModel):
    """Требование в ответе."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    device_type_id: UUID = Field(..., alias="deviceTypeId", serialization_alias="deviceTypeId")
    device_type_name: str = Field("", alias="deviceTypeName", serialization_alias="deviceTypeName")
    quantity: int


class WorkstationCreate(BaseModel):
    """Создание рабочего места."""

    model_config = ConfigDict(populate_by_name=True)

    location_id: UUID = Field(..., alias="locationId")
    seat_code: str = Field(..., min_length=1, max_length=50, alias="seatCode")
    employee_internal_email: str | None = Field(None, max_length=255, alias="employeeInternalEmail")
    requirements: list[RequirementItemCreate] = Field(default_factory=list)


class WorkstationUpdate(BaseModel):
    """Обновление рабочего места."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    seat_code: str | None = Field(None, min_length=1, max_length=50, alias="seatCode")
    employee_internal_email: str | None = Field(None, max_length=255, alias="employeeInternalEmail")
    requirements: list[RequirementItemCreate] | None = None


class WorkstationRead(BaseModel):
    """Чтение рабочего места."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    location_id: UUID = Field(..., alias="locationId", serialization_alias="locationId")
    seat_code: str = Field(..., alias="seatCode", serialization_alias="seatCode")
    employee_internal_email: str | None = Field(
        None,
        alias="employeeInternalEmail",
        serialization_alias="employeeInternalEmail",
    )
    requirements: list[WorkstationRequirementRead] = Field(default_factory=list)

