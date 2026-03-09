"""Tests for Redis client."""

from unittest.mock import AsyncMock, patch

import pytest

from src.redis_client.redis import RedisController


class TestRedisController:
    """Test RedisController methods."""

    @pytest.mark.asyncio
    async def test_get(self):
        """RedisController.get returns value."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.get = AsyncMock(return_value="test_value")

            result = await RedisController.get("key")

            assert result == "test_value"
            mock_r.get.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_get_none(self):
        """RedisController.get returns None when key missing."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.get = AsyncMock(return_value=None)

            result = await RedisController.get("missing")

            assert result is None

    @pytest.mark.asyncio
    async def test_set(self):
        """RedisController.set stores value."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.set = AsyncMock(return_value=True)

            result = await RedisController.set("key", "value", ttl=60)

            assert result is True
            mock_r.set.assert_called_once_with("key", "value", ex=60)

    @pytest.mark.asyncio
    async def test_set_default_ttl(self):
        """RedisController.set uses default TTL when not specified."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.set = AsyncMock(return_value=True)

            await RedisController.set("key", "value")

            mock_r.set.assert_called_once_with("key", "value", ex=3600)

    @pytest.mark.asyncio
    async def test_get_json(self):
        """RedisController.get_json parses JSON."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.get = AsyncMock(return_value='{"a": 1}')

            result = await RedisController.get_json("key")

            assert result == {"a": 1}

    @pytest.mark.asyncio
    async def test_set_json(self):
        """RedisController.set_json serializes to JSON."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.set = AsyncMock(return_value=True)

            result = await RedisController.set_json("key", {"a": 1})

            assert result is True
            mock_r.set.assert_called_once_with("key", '{"a": 1}', ex=3600)

    @pytest.mark.asyncio
    async def test_delete(self):
        """RedisController.delete removes key."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.delete = AsyncMock(return_value=1)

            result = await RedisController.delete("key")

            assert result == 1
            mock_r.delete.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_delete_many(self):
        """RedisController.delete_many removes multiple keys."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.delete = AsyncMock(return_value=3)

            result = await RedisController.delete_many("k1", "k2", "k3")

            assert result == 3
            mock_r.delete.assert_called_once_with("k1", "k2", "k3")

    @pytest.mark.asyncio
    async def test_delete_many_empty(self):
        """RedisController.delete_many with no keys returns 0."""
        result = await RedisController.delete_many()

        assert result == 0

    @pytest.mark.asyncio
    async def test_exists(self):
        """RedisController.exists returns True when key exists."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.exists = AsyncMock(return_value=1)

            result = await RedisController.exists("key")

            assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """RedisController.exists returns False when key missing."""
        with patch("src.redis_client.redis.r") as mock_r:
            mock_r.exists = AsyncMock(return_value=0)

            result = await RedisController.exists("key")

            assert result is False
