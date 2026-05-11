"""add peripheral category and components domain

Revision ID: 011_peripherals_and_components
Revises: 010_license_details
Create Date: 2026-05-11

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "011_peripherals_and_components"
down_revision: str | None = "010_license_details"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERIPHERAL_TYPES = [
    ("Мышь", "MOUSE", "peripheral", "Компьютерная мышь"),
    ("Клавиатура", "KBD", "peripheral", "Клавиатура"),
    ("Наушники", "HEADSET", "peripheral", "Гарнитура/наушники"),
    ("Веб-камера", "WEBCAM", "peripheral", "Камера для видеосвязи"),
]


def _add_peripheral_types() -> None:
    conn = op.get_bind()
    for name, code, category, description in PERIPHERAL_TYPES:
        result = conn.execute(text("SELECT id FROM device_types WHERE code = :c"), {"c": code})
        if result.fetchone():
            continue
        conn.execute(
            text(
                "INSERT INTO device_types (id, name, code, category, description) "
                "VALUES (:id, :name, :code, :category, :description)"
            ),
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "code": code,
                "category": category,
                "description": description,
            },
        )


def _remove_peripheral_types() -> None:
    conn = op.get_bind()
    for _, code, _, _ in PERIPHERAL_TYPES:
        conn.execute(text("DELETE FROM device_types WHERE code = :c"), {"c": code})


def upgrade() -> None:
    op.drop_constraint("device_types_category_check", "device_types", type_="check")
    op.create_check_constraint(
        "device_types_category_check",
        "device_types",
        "category IN ('computing', 'office', 'network', 'peripheral', 'other')",
    )
    _add_peripheral_types()

    op.create_table(
        "components",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("component_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="in_use"),
        sa.Column("arrival_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "component_type IN ('cpu', 'motherboard', 'ram', 'storage', 'psu', 'gpu', 'case', 'cooler')",
            name="components_type_check",
        ),
        sa.CheckConstraint(
            "status IN ('in_use', 'repair', 'scrapped', 'archived')",
            name="components_status_check",
        ),
    )

    op.create_table(
        "computer_components",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("computer_id", sa.UUID(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("component_id", sa.UUID(), sa.ForeignKey("components.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("component_id", name="uq_computer_components_component"),
    )
    op.create_index("idx_computer_components_computer", "computer_components", ["computer_id"])


def downgrade() -> None:
    op.drop_index("idx_computer_components_computer", table_name="computer_components")
    op.drop_table("computer_components")
    op.drop_table("components")

    _remove_peripheral_types()
    op.drop_constraint("device_types_category_check", "device_types", type_="check")
    op.create_check_constraint(
        "device_types_category_check",
        "device_types",
        "category IN ('computing', 'office', 'network', 'other')",
    )
