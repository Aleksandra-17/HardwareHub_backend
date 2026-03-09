"""Tests for root router (health)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.routers.root.actions import _health
from src.routers.root.schemas import HealthStatus


class TestHealthActions:
    """Test _health action."""

    @pytest.mark.asyncio
    async def test_health_db_redis_ok(self):
        """Health returns healthy when DB and Redis work."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(
            return_value=MagicMock(scalars=lambda: MagicMock(first=lambda: 1))
        )

        with patch("src.routers.root.actions.RedisController") as MockRedis:
            mock_redis = AsyncMock()
            mock_redis.set = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(return_value="ok")
            mock_redis.delete = AsyncMock(return_value=1)
            MockRedis.set = mock_redis.set
            MockRedis.get = mock_redis.get
            MockRedis.delete = mock_redis.delete

            result = await _health(mock_session)

            assert result.status == HealthStatus.HEALTHY
            assert result.database == "connected"
            assert result.redis == "connected"

    @pytest.mark.asyncio
    async def test_health_db_fails(self):
        """Health returns unhealthy when DB fails."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=Exception("Connection refused"))

        with patch("src.routers.root.actions.RedisController") as MockRedis:
            mock_redis = AsyncMock()
            mock_redis.set = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(return_value="ok")
            mock_redis.delete = AsyncMock(return_value=1)
            MockRedis.set = mock_redis.set
            MockRedis.get = mock_redis.get
            MockRedis.delete = mock_redis.delete

            result = await _health(mock_session)

            assert result.status == HealthStatus.UNHEALTHY
            assert "error" in result.database
            assert result.redis == "connected"

    @pytest.mark.asyncio
    async def test_health_redis_fails(self):
        """Health returns unhealthy when Redis fails."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(
            return_value=MagicMock(scalars=lambda: MagicMock(first=lambda: 1))
        )

        with patch("src.routers.root.actions.RedisController") as MockRedis:
            MockRedis.set = AsyncMock(side_effect=Exception("Redis connection failed"))

            result = await _health(mock_session)

            assert result.status == HealthStatus.UNHEALTHY
            assert result.database == "connected"
            assert "error" in result.redis


class TestHealthEndpoint:
    """Test health endpoint."""

    def test_health_returns_200(self, client_with_mock_db):
        """Health endpoint returns 200 when healthy."""
        with (
            patch(
                "src.routers.root.actions.RedisController.set",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "src.routers.root.actions.RedisController.get",
                new_callable=AsyncMock,
                return_value="ok",
            ),
            patch(
                "src.routers.root.actions.RedisController.delete",
                new_callable=AsyncMock,
                return_value=1,
            ),
        ):
            response = client_with_mock_db.get("/api/root/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["redis"] == "connected"
