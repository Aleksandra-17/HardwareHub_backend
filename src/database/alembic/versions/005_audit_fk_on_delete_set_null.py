"""audit_entries.device_id: ON DELETE SET NULL

Revision ID: 005_audit_fk
Revises: 004_statuses
Create Date: 2025-03-09

"""

from collections.abc import Sequence

from alembic import op

revision: str = "005_audit_fk"
down_revision: str | None = "004_statuses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "audit_entries_device_id_fkey",
        "audit_entries",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "audit_entries_device_id_fkey",
        "audit_entries",
        "devices",
        ["device_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "audit_entries_device_id_fkey",
        "audit_entries",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "audit_entries_device_id_fkey",
        "audit_entries",
        "devices",
        ["device_id"],
        ["id"],
    )
