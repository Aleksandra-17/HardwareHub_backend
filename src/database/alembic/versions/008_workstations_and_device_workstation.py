"""workstations, requirements, device.workstation_id

Revision ID: 008_ws
Revises: 007_ws_cap
Create Date: 2026-05-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "008_ws"
down_revision: str | None = "007_ws_cap"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workstations",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("location_id", sa.UUID(), sa.ForeignKey("locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seat_code", sa.String(length=50), nullable=False),
        sa.Column("employee_internal_email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "location_id",
            "seat_code",
            name="uq_workstation_location_seat",
        ),
    )
    op.create_index("idx_workstations_location", "workstations", ["location_id"])

    op.create_table(
        "workstation_requirements",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "workstation_id",
            sa.UUID(),
            sa.ForeignKey("workstations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("device_type_id", sa.UUID(), sa.ForeignKey("device_types.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("quantity >= 1", name="ck_workstation_requirement_qty"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workstation_id",
            "device_type_id",
            name="uq_workstation_req_type",
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "workstation_id",
            sa.UUID(),
            sa.ForeignKey("workstations.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("idx_devices_workstation", "devices", ["workstation_id"])


def downgrade() -> None:
    op.drop_index("idx_devices_workstation", table_name="devices")
    op.drop_column("devices", "workstation_id")
    op.drop_table("workstation_requirements")
    op.drop_index("idx_workstations_location", table_name="workstations")
    op.drop_table("workstations")
