"""Tests for misc.timezone."""

from unittest.mock import patch

import pytest

from src.misc.timezone import get_datetime


class TestGetDatetime:
    """Test get_datetime."""

    def test_get_datetime_returns_datetime(self):
        """get_datetime returns datetime object."""
        result = get_datetime("UTC")
        assert hasattr(result, "year")
        assert hasattr(result, "month")
        assert hasattr(result, "day")
        assert hasattr(result, "hour")

    def test_get_datetime_no_tzinfo(self):
        """get_datetime returns naive datetime (tzinfo removed)."""
        result = get_datetime("Europe/Moscow")
        assert result.tzinfo is None

    def test_get_datetime_valid_timezone(self):
        """get_datetime accepts valid timezone."""
        result = get_datetime("America/New_York")
        assert result is not None
