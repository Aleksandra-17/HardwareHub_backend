"""Модель роутера people."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Person(Base):
    """Ответственные лица."""

    __tablename__ = "people"
    __repr_attrs__ = ["full_name"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="person",
        foreign_keys="Device.person_id",
    )
