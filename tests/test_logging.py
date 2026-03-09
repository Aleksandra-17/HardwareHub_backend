"""Tests for database logging (SessionTracker)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.database.logging import SessionTracker


class TestSessionTracker:
    """Test SessionTracker."""

    @pytest.fixture(autouse=True)
    def clear_sessions(self):
        """Clear sessions before/after each test."""
        SessionTracker._sessions.clear()
        yield
        SessionTracker._sessions.clear()

    def test_track_session_returns_id(self):
        """track_session returns a session ID."""
        mock_session = AsyncMock()
        sid = SessionTracker.track_session(mock_session, context="test")

        assert isinstance(sid, str)
        assert len(sid) > 0
        assert sid in SessionTracker._sessions

    def test_track_session_stores_info(self):
        """track_session stores session info."""
        mock_session = AsyncMock()
        sid = SessionTracker.track_session(mock_session, context="api")

        info = SessionTracker._sessions[sid]
        assert info["session"] == mock_session
        assert info["context"] == "api"
        assert "created_at" in info

    def test_untrack_session_removes(self):
        """untrack_session removes session."""
        mock_session = AsyncMock()
        sid = SessionTracker.track_session(mock_session)

        SessionTracker.untrack_session(sid)

        assert sid not in SessionTracker._sessions

    def test_untrack_session_unknown_id(self):
        """untrack_session with unknown ID does nothing."""
        SessionTracker.untrack_session("unknown-id")
        assert "unknown-id" not in SessionTracker._sessions

    def test_get_active_sessions_empty(self):
        """get_active_sessions returns empty list when no sessions."""
        result = SessionTracker.get_active_sessions()
        assert result == []

    def test_get_active_sessions_returns_info(self):
        """get_active_sessions returns session info."""
        mock_session = MagicMock()
        sid = SessionTracker.track_session(mock_session, context="test")

        result = SessionTracker.get_active_sessions()

        assert len(result) == 1
        assert result[0]["session_id"] == sid
        assert result[0]["context"] == "test"
        assert "age_seconds" in result[0]
