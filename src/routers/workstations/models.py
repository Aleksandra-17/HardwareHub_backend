"""Модели рабочих мест в кабинетах."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Workstation(Base):
    """Рабочее место внутри одного кабинета."""

    __tablename__ = "workstations"
    __repr_attrs__ = ("seat_code",)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seat_code: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_internal_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("location_id", "seat_code", name="uq_workstation_location_seat"),
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="workstations",
        foreign_keys=[location_id],
    )
    requirements: Mapped[list["WorkstationRequirement"]] = relationship(
        "WorkstationRequirement",
        back_populates="workstation",
        cascade="all, delete-orphan",
    )
    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="workstation",
        foreign_keys="Device.workstation_id",
    )


class WorkstationRequirement(Base):
    """Требуемый тип техники для рабочего места."""

    __tablename__ = "workstation_requirements"
    __repr_attrs__ = ("quantity",)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workstation_id: Mapped[UUID] = mapped_column(
        ForeignKey("workstations.id", ondelete="CASCADE"),
        nullable=False,
    )
    device_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("device_types.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint(
            "workstation_id",
            "device_type_id",
            name="uq_workstation_req_type",
        ),
        CheckConstraint("quantity >= 1", name="ck_workstation_req_qty"),
    )

    workstation: Mapped["Workstation"] = relationship(
        "Workstation",
        back_populates="requirements",
    )
    device_type: Mapped["DeviceType"] = relationship(
        "DeviceType",
        foreign_keys=[device_type_id],
    )
