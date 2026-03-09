"""Модели роутера devices."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Device(Base):
    """Устройства (связь с device_types, locations, people)."""

    __tablename__ = "devices"
    __repr_attrs__ = ["inventory_number", "name"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    inventory_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("device_types.id"),
        nullable=True,
    )
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True,
    )
    person_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )
    commission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_check_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    qr_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_use', 'repair', 'scrapped', 'archived')",
            name="devices_status_check",
        ),
        Index("idx_devices_status", "status"),
        Index("idx_devices_device_type", "device_type_id"),
        Index("idx_devices_location", "location_id"),
        Index("idx_devices_person", "person_id"),
        Index("idx_devices_inventory", "inventory_number"),
    )

    device_type: Mapped["DeviceType | None"] = relationship(
        "DeviceType",
        back_populates="devices",
        foreign_keys=[device_type_id],
    )
    location: Mapped["Location | None"] = relationship(
        "Location",
        back_populates="devices",
        foreign_keys=[location_id],
    )
    person: Mapped["Person | None"] = relationship(
        "Person",
        back_populates="devices",
        foreign_keys=[person_id],
    )
    audit_entries: Mapped[list["AuditEntry"]] = relationship(
        "AuditEntry",
        back_populates="device",
        foreign_keys="AuditEntry.device_id",
    )


class AuditEntry(Base):
    """История изменений по устройствам."""

    __tablename__ = "audit_entries"
    __repr_attrs__ = ["action", "date"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    device_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("devices.id"),
        nullable=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    user: Mapped[str] = mapped_column(String(255), nullable=False)

    device: Mapped["Device | None"] = relationship(
        "Device",
        back_populates="audit_entries",
        foreign_keys=[device_id],
    )
