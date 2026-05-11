"""Модель роутера locations."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Location(Base):
    """Справочник локаций (кабинеты)."""

    __tablename__ = "locations"
    __repr_attrs__ = ["name"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    building: Mapped[str | None] = mapped_column(String(255), nullable=True)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workstation_capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="location",
        foreign_keys="Device.location_id",
    )
    workstations: Mapped[list["Workstation"]] = relationship(
        "Workstation",
        back_populates="location",
        cascade="all, delete-orphan",
    )
