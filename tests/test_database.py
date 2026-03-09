"""Tests for database module."""



from src.database.base import resolve_table_name
from src.database.dependencies import DbSession


class TestBase:
    """Test Base and resolve_table_name."""

    def test_resolve_table_name(self):
        """resolve_table_name converts CamelCase to snake_case."""
        assert resolve_table_name("DeviceType") == "device_type"
        assert resolve_table_name("AuditEntry") == "audit_entry"


class TestDbSession:
    """Test DbSession type."""

    def test_db_session_is_annotated(self):
        """DbSession is Annotated type."""
        import typing

        origin = typing.get_origin(DbSession)
        assert origin is typing.Annotated
