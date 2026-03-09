"""Seed initial admin user

Revision ID: 002_seed_admin
Revises: 001_add_users
Create Date: 2025-03-09

Creates initial admin user if JWT_INITIAL_ADMIN_PASSWORD is set.
Username: admin. Run: export JWT_INITIAL_ADMIN_PASSWORD=your-secure-password
"""

import os
import uuid
from collections.abc import Sequence

import bcrypt
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "002_seed_admin"
down_revision: str | None = "001_add_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    password = os.environ.get("JWT_INITIAL_ADMIN_PASSWORD")
    if not password:
        return

    conn = op.get_bind()
    result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
    if result.fetchone():
        return

    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn.execute(
        text(
            "INSERT INTO users (id, username, password_hash, role, is_active, created_at, updated_at) "
            "VALUES (:id, 'admin', :pw_hash, 'admin', true, now(), now())"
        ),
        {"id": user_id, "pw_hash": password_hash},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM users WHERE username = 'admin'"))
