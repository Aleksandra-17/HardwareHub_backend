"""Модель роутера device_types."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class DeviceType(Base):
    """Справочник типов устройств."""

    __tablename__ = "device_types"
    __repr_attrs__ = ["name", "code"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "category IN ('computing', 'office', 'network', 'peripheral', 'other')",
            name="device_types_category_check",
        ),
    )

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="device_type",
        foreign_keys="Device.device_type_id",
    )
