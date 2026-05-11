"""Модель роутера licenses."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class License(Base):
    """Лицензии ПО (без лимита устройств по бизнес-допущению)."""

    __tablename__ = "licenses"
    __repr_attrs__ = ["name"]

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expires_at: Mapped[date] = mapped_column(Date, nullable=False)
    details: Mapped[str | None] = mapped_column(String(2000), nullable=True)
