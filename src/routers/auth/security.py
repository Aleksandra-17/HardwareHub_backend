"""JWT и хеширование паролей."""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

from src.config import jwt_cfg

REFRESH_PREFIX = "refresh:"


def hash_password(password: str) -> str:
    """Хеширование пароля."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Проверка пароля."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def generate_password(length: int = 12) -> str:
    """Генерация случайного пароля."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_access_token(subject: str | UUID) -> str:
    """Создание access токена."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=jwt_cfg.access_token_expire_minutes)
    payload = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "access",
    }
    return jwt.encode(
        payload,
        jwt_cfg.secret_key,
        algorithm=jwt_cfg.algorithm,
    )


def create_refresh_token(subject: str | UUID) -> str:
    """Создание refresh токена."""
    now = datetime.now(UTC)
    expire = now + timedelta(days=jwt_cfg.refresh_token_expire_days)
    payload = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        jwt_cfg.secret_key,
        algorithm=jwt_cfg.algorithm,
    )


def decode_token(token: str) -> dict | None:
    """Декодирование JWT токена."""
    try:
        return jwt.decode(
            token,
            jwt_cfg.secret_key,
            algorithms=[jwt_cfg.algorithm],
        )
    except jwt.PyJWTError:
        return None
