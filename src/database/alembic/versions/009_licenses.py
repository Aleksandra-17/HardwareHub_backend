"""licenses table

Revision ID: 009_licenses
Revises: 008_ws
Create Date: 2026-05-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "009_licenses"
down_revision: str | None = "008_ws"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "licenses",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("expires_at", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("licenses")
