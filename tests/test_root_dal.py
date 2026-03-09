"""Tests for root DAL."""

from unittest.mock import AsyncMock

import pytest

from src.routers.root.dal import RootDAL


class TestRootDAL:
    """Test RootDAL."""

    def test_init_stores_session(self):
        """RootDAL stores session on init."""
        mock_session = AsyncMock()
        dal = RootDAL(mock_session)
        assert dal.session == mock_session
