"""Pytest fixtures."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Set test env before importing app
os.environ.setdefault("POSTGRES_IP", "localhost")
os.environ.setdefault("POSTGRES_DATABASE_NAME", "test_db")
os.environ.setdefault("REDIS_HOST", "localhost")


@pytest.fixture(autouse=True)
def env_config():
    """Set env vars for config."""
    env = {
        "POSTGRES_DATABASE": "postgresql",
        "POSTGRES_DRIVER": "asyncpg",
        "POSTGRES_DATABASE_NAME": "test_db",
        "POSTGRES_USERNAME": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_IP": "localhost",
        "POSTGRES_PORT": "5432",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
        "REDIS_PASSWORD": "",
        "UVICORN_HOST": "0.0.0.0",
        "UVICORN_PORT": "8000",
        "JWT_SECRET_KEY": "test-secret-key-for-tests-only",
        "JWT_ALGORITHM": "HS256",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7",
    }
    with patch.dict(os.environ, env, clear=False):
        yield


@pytest.fixture
def client(env_config) -> TestClient:  # noqa: ARG001 - fixture dep for ordering
    """Sync test client."""
    from src.main import app

    return TestClient(app, base_url="http://test")


@pytest.fixture
async def async_client():
    """Async test client."""
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db_session():
    """Mock async DB session."""
    session = AsyncMock(spec=AsyncSession)

    async def execute(stmt):
        if hasattr(stmt, "compile") and "SELECT 1" in str(stmt):
            return MagicMock(scalars=lambda: MagicMock(first=lambda: 1))
        return MagicMock()

    session.execute = execute
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.is_active = True
    session.service_session_id = "test-session-id"
    return session


@pytest.fixture
def client_with_mock_db(client: TestClient, mock_db_session):
    """Client with mocked DB session."""
    from src.database.dependencies import get_db
    from src.main import app

    async def override_get_db():
        yield mock_db_session

    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_db_session
    mock_cm.__aexit__.return_value = None

    with patch("src.middlewares.database.async_session_maker") as mock_maker:
        mock_maker.return_value = mock_cm
        app.dependency_overrides[get_db] = override_get_db
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis operations."""
    storage = {}

    class MockRedis:
        async def get(self, key):
            return storage.get(key)

        async def set(self, key, value, ex=None):  # noqa: ARG002
            storage[key] = value
            return True

        async def delete(self, *keys):
            count = 0
            for k in keys:
                if k in storage:
                    del storage[k]
                    count += 1
            return count

        async def exists(self, key):
            return 1 if key in storage else 0

        async def expire(self, key, ttl):  # noqa: ARG002
            return True

        async def ttl(self, key):
            return -1 if key in storage else -2

    return MockRedis(), storage
