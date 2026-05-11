"""locations: workstation_capacity

Revision ID: 007_ws_cap
Revises: 006_seed_types
Create Date: 2026-05-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_ws_cap"
down_revision: str | None = "006_seed_types"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "locations",
        sa.Column(
            "workstation_capacity",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("locations", "workstation_capacity")
