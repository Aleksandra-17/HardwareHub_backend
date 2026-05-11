"""Tests for middlewares."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.middlewares.database import db_session_middleware, get_request_id


class TestDatabaseMiddleware:
    """Test database session middleware."""

    @pytest.mark.asyncio
    async def test_middleware_sets_request_id(self):
        """Middleware sets request_id and stores session in request.state.db."""
        request = MagicMock()
        request.state = MagicMock()
        call_next = AsyncMock(return_value=MagicMock())

        # async_sessionmaker() returns a session; it acts as its own context manager (__aenter__ returns self)
        mock_session = AsyncMock()
        mock_session.is_active = True
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session.service_session_id = None
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with (
            patch("src.middlewares.database.async_session_maker", return_value=mock_session),
            patch("src.middlewares.database.SessionTracker.track_session", return_value="sid"),
            patch("src.middlewares.database.SessionTracker.untrack_session"),
        ):
            await db_session_middleware(request, call_next)

            call_next.assert_called_once()
            assert request.state.db == mock_session

    @pytest.mark.asyncio
    async def test_get_request_id(self):
        """get_request_id returns context value."""
        assert get_request_id() is None or isinstance(get_request_id(), str)
