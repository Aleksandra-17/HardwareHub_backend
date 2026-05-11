"""Seed initial admin and root users

Revision ID: 002_seed_admin
Revises: 001_add_users
Create Date: 2025-03-09

Creates:
- root:root — базовый пользователь (admin), всегда создаётся
- admin — если задан JWT_INITIAL_ADMIN_PASSWORD
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


def _ensure_user(conn, username: str, password: str, role: str) -> None:
    """Создать пользователя, если не существует."""
    result = conn.execute(text("SELECT id FROM users WHERE username = :u"), {"u": username})
    if result.fetchone():
        return
    user_id = str(uuid.uuid4())
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn.execute(
        text(
            "INSERT INTO users (id, username, password_hash, role, is_active, created_at, updated_at) "
            "VALUES (:id, :u, :pw_hash, :role, true, now(), now())"
        ),
        {"id": user_id, "u": username, "pw_hash": pw_hash, "role": role},
    )


def upgrade() -> None:
    conn = op.get_bind()

    _ensure_user(conn, "root", "root", "admin")

    password = os.environ.get("JWT_INITIAL_ADMIN_PASSWORD")
    if password:
        _ensure_user(conn, "admin", password, "admin")


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM users WHERE username IN ('root', 'admin')"))
