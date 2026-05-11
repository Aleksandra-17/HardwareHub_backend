"""Add device_types, locations, people, devices, audit_entries tables

Revision ID: 003_add_core
Revises: 002_seed_admin
Create Date: 2025-03-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_core"
down_revision: str | None = "002_seed_admin"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "device_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.CheckConstraint(
            "category IN ('computing', 'office', 'network', 'other')",
            name="device_types_category_check",
        ),
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("building", sa.String(255), nullable=True),
        sa.Column("floor", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "people",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("position", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("inventory_number", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_type_id", sa.UUID(), sa.ForeignKey("device_types.id"), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("location_id", sa.UUID(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("person_id", sa.UUID(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("commission_date", sa.Date(), nullable=True),
        sa.Column("last_check_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("purchase_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("qr_code", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inventory_number"),
        sa.CheckConstraint(
            "status IN ('in_use', 'reserve', 'decommissioned', 'repair')",
            name="devices_status_check",
        ),
    )
    op.create_index("idx_devices_status", "devices", ["status"])
    op.create_index("idx_devices_device_type", "devices", ["device_type_id"])
    op.create_index("idx_devices_location", "devices", ["location_id"])
    op.create_index("idx_devices_person", "devices", ["person_id"])
    op.create_index("idx_devices_inventory", "devices", ["inventory_number"])

    op.create_table(
        "audit_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("user", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_entries")
    op.drop_index("idx_devices_inventory", table_name="devices")
    op.drop_index("idx_devices_person", table_name="devices")
    op.drop_index("idx_devices_location", table_name="devices")
    op.drop_index("idx_devices_device_type", table_name="devices")
    op.drop_index("idx_devices_status", table_name="devices")
    op.drop_table("devices")
    op.drop_table("people")
    op.drop_table("locations")
    op.drop_table("device_types")
