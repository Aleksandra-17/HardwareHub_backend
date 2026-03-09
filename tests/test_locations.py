"""Tests for locations router."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.routers.locations.actions import list_locations
from src.routers.locations.dal import LocationDAL
from src.routers.locations.models import Location


class TestLocationDAL:
    """Test LocationDAL."""

    @pytest.mark.asyncio
    async def test_get_all_with_count_empty(self):
        """DAL returns empty list when no locations."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = LocationDAL(mock_session)
        result = await dal.get_all_with_count()

        assert result == []


class TestLocationsActions:
    """Test locations actions."""

    @pytest.mark.asyncio
    async def test_list_locations_empty(self):
        """list_locations returns empty list."""
        mock_session = AsyncMock()
        with patch.object(LocationDAL, "get_all_with_count", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            result = await list_locations(mock_session)

            assert result == []


class TestLocationsEndpoint:
    """Test locations API endpoint."""

    def test_get_locations_200(self, client_with_mock_db):
        """GET /api/locations returns 200."""
        with patch(
            "src.routers.locations.actions.list_locations",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client_with_mock_db.get("/api/locations/")

            assert response.status_code == 200
            assert response.json() == []
