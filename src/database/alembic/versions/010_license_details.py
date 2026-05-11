"""add details field to licenses

Revision ID: 010_license_details
Revises: 009_licenses
Create Date: 2026-05-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "010_license_details"
down_revision: str | None = "009_licenses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("licenses", sa.Column("details", sa.String(length=2000), nullable=True))


def downgrade() -> None:
    op.drop_column("licenses", "details")
