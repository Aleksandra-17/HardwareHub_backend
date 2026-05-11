"""Tests for device_types router."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.routers.device_types.actions import list_device_types
from src.routers.device_types.dal import DeviceTypeDAL
from src.routers.device_types.models import DeviceType


class TestDeviceTypeDAL:
    """Test DeviceTypeDAL."""

    @pytest.mark.asyncio
    async def test_get_all_with_count_empty(self):
        """DAL returns empty list when no device types."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = DeviceTypeDAL(mock_session)
        result = await dal.get_all_with_count()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_with_count(self):
        """DAL returns device types with counts."""
        dt = DeviceType(
            id=uuid4(),
            name="Ноутбук",
            code="NB-001",
            category="computing",
            description=None,
        )
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [(dt, 5)]
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = DeviceTypeDAL(mock_session)
        result = await dal.get_all_with_count()

        assert len(result) == 1
        assert result[0][0].name == "Ноутбук"
        assert result[0][1] == 5


class TestDeviceTypesActions:
    """Test device_types actions."""

    @pytest.mark.asyncio
    async def test_list_device_types_empty(self):
        """list_device_types returns empty list."""
        mock_session = AsyncMock()
        with patch.object(DeviceTypeDAL, "get_all_with_count", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            result = await list_device_types(mock_session)

            assert result == []

    @pytest.mark.asyncio
    async def test_list_device_types(self):
        """list_device_types returns DeviceTypeRead list."""
        dt = DeviceType(
            id=uuid4(),
            name="Ноутбук",
            code="NB-001",
            category="computing",
            description="ПК",
        )
        mock_session = AsyncMock()
        with patch.object(DeviceTypeDAL, "get_all_with_count", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [(dt, 3)]

            result = await list_device_types(mock_session)

            assert len(result) == 1
            assert result[0].name == "Ноутбук"
            assert result[0].device_count == 3


class TestDeviceTypesEndpoint:
    """Test device_types API endpoint."""

    def test_get_device_types_200(self, client_authenticated):
        """GET /api/device-types returns 200."""
        with patch(
            "src.routers.device_types.actions.list_device_types",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client_authenticated.get("/api/device-types/")

            assert response.status_code == 200
            assert response.json() == []
