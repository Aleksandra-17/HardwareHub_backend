"""Модели роутера components."""

from __future__ import annotations

import uuid
from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Component(Base):
    """Комплектующая как самостоятельная учётная единица."""

    __tablename__ = "components"
    __repr_attrs__ = ["name", "component_type"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="in_use", server_default="in_use")
    arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "component_type IN ('cpu', 'motherboard', 'ram', 'storage', 'psu', 'gpu', 'case', 'cooler')",
            name="components_type_check",
        ),
        CheckConstraint(
            "status IN ('in_use', 'repair', 'scrapped', 'archived')",
            name="components_status_check",
        ),
    )

    links: Mapped[list["ComputerComponent"]] = relationship(
        "ComputerComponent",
        back_populates="component",
        cascade="all, delete-orphan",
    )


class ComputerComponent(Base):
    """Текущая привязка комплектующей к ПК."""

    __tablename__ = "computer_components"
    __repr_attrs__ = ["computer_id", "component_id"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    computer_id: Mapped[UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    component_id: Mapped[UUID] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("component_id", name="uq_computer_components_component"),
    )

    computer: Mapped["Device"] = relationship("Device", back_populates="computer_components")
    component: Mapped["Component"] = relationship("Component", back_populates="links")
