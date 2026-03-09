"""Update device statuses: reserve->archived, decommissioned->scrapped

Revision ID: 004_statuses
Revises: 003_add_core
Create Date: 2025-03-09

"""

from collections.abc import Sequence

from alembic import op

revision: str = "004_statuses"
down_revision: str | None = "003_add_core"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Migrate existing data
    op.execute("UPDATE devices SET status = 'archived' WHERE status = 'reserve'")
    op.execute("UPDATE devices SET status = 'scrapped' WHERE status = 'decommissioned'")

    # Replace constraint
    op.drop_constraint("devices_status_check", "devices", type_="check")
    op.create_check_constraint(
        "devices_status_check",
        "devices",
        "status IN ('in_use', 'repair', 'scrapped', 'archived')",
    )


def downgrade() -> None:
    op.drop_constraint("devices_status_check", "devices", type_="check")
    op.execute("UPDATE devices SET status = 'reserve' WHERE status = 'archived'")
    op.execute("UPDATE devices SET status = 'decommissioned' WHERE status = 'scrapped'")
    op.create_check_constraint(
        "devices_status_check",
        "devices",
        "status IN ('in_use', 'reserve', 'decommissioned', 'repair')",
    )
