"""Seed default device types

Revision ID: 006_seed_types
Revises: 005_audit_fk
Create Date: 2025-03-09

"""

import uuid
from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "006_seed_types"
down_revision: str | None = "005_audit_fk"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEED_TYPES = [
    ("Ноутбук", "NB", "computing", "Портативный компьютер"),
    ("ПК", "PC", "computing", "Персональный компьютер"),
    ("Монитор", "MON", "office", "Монитор"),
    ("Принтер", "PRN", "office", "Принтер"),
    ("Сканер", "SCN", "office", "Сканер"),
    ("МФУ", "MFU", "office", "Многофункциональное устройство"),
    ("Сервер", "SRV", "network", "Сервер"),
    ("Коммутатор", "SW", "network", "Сетевой коммутатор"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for name, code, category, description in SEED_TYPES:
        result = conn.execute(text("SELECT id FROM device_types WHERE code = :c"), {"c": code})
        if result.fetchone():
            continue
        uid = str(uuid.uuid4())
        conn.execute(
            text(
                "INSERT INTO device_types (id, name, code, category, description) "
                "VALUES (:id, :name, :code, :category, :description)"
            ),
            {
                "id": uid,
                "name": name,
                "code": code,
                "category": category,
                "description": description,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    for _, code, _, _ in SEED_TYPES:
        conn.execute(text("DELETE FROM device_types WHERE code = :c"), {"c": code})
