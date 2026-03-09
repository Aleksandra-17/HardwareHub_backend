"""Tests for SQLAlchemy models."""

from uuid import uuid4

from src.routers.device_types.models import DeviceType
from src.routers.devices.models import AuditEntry, Device
from src.routers.locations.models import Location
from src.routers.people.models import Person


class TestDeviceTypeModel:
    """Test DeviceType model."""

    def test_device_type_tablename(self):
        """DeviceType has correct tablename."""
        assert DeviceType.__tablename__ == "device_types"

    def test_device_type_creation(self):
        """DeviceType can be created with required fields."""
        dt = DeviceType(
            name="Ноутбук",
            code="NB-001",
            category="computing",
        )
        assert dt.name == "Ноутбук"
        assert dt.code == "NB-001"
        assert dt.category == "computing"


class TestLocationModel:
    """Test Location model."""

    def test_location_tablename(self):
        """Location has correct tablename."""
        assert Location.__tablename__ == "locations"

    def test_location_creation(self):
        """Location can be created."""
        loc = Location(name="Каб. 101")
        assert loc.name == "Каб. 101"


class TestPersonModel:
    """Test Person model."""

    def test_person_tablename(self):
        """Person has correct tablename."""
        assert Person.__tablename__ == "people"

    def test_person_creation(self):
        """Person can be created."""
        p = Person(full_name="Иванов И.И.")
        assert p.full_name == "Иванов И.И."


class TestDeviceModel:
    """Test Device model."""

    def test_device_tablename(self):
        """Device has correct tablename."""
        assert Device.__tablename__ == "devices"

    def test_device_creation(self):
        """Device can be created with required fields."""
        dev = Device(
            inventory_number="INV-001",
            name="Ноутбук",
            status="in_use",
            device_type_id=uuid4(),
            location_id=uuid4(),
        )
        assert dev.inventory_number == "INV-001"
        assert dev.status == "in_use"


class TestAuditEntryModel:
    """Test AuditEntry model."""

    def test_audit_entry_tablename(self):
        """AuditEntry has correct tablename."""
        assert AuditEntry.__tablename__ == "audit_entries"

    def test_audit_entry_creation(self):
        """AuditEntry can be created."""
        from datetime import date

        ae = AuditEntry(
            date=date(2025, 1, 15),
            action="Инвентаризация",
            user="Иванов",
        )
        assert ae.action == "Инвентаризация"
        assert ae.user == "Иванов"
