"""Tests for people router."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.routers.people.actions import list_people
from src.routers.people.dal import PersonDAL


class TestPersonDAL:
    """Test PersonDAL."""

    @pytest.mark.asyncio
    async def test_get_all_with_count_empty(self):
        """DAL returns empty list when no people."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = PersonDAL(mock_session)
        result = await dal.get_all_with_count()

        assert result == []


class TestPeopleActions:
    """Test people actions."""

    @pytest.mark.asyncio
    async def test_list_people_empty(self):
        """list_people returns empty list."""
        mock_session = AsyncMock()
        with patch.object(PersonDAL, "get_all_with_count", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            result = await list_people(mock_session)

            assert result == []


class TestPeopleEndpoint:
    """Test people API endpoint."""

    def test_get_people_200(self, client_with_mock_db):
        """GET /api/people returns 200."""
        with patch(
            "src.routers.people.actions.list_people",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client_with_mock_db.get("/api/people/")

            assert response.status_code == 200
            assert response.json() == []
