"""Tests for Pydantic schemas."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from src.routers.device_types.schemas import DeviceTypeRead
from src.routers.devices.enums import DeviceStatus
from src.routers.devices.schemas import AuditEntryRead, DeviceCreate, DeviceRead, DeviceUpdate
from src.routers.locations.schemas import LocationRead
from src.routers.people.schemas import PersonRead
from src.routers.root.schemas import HealthCheckResponse, HealthStatus


class TestRootSchemas:
    """Test root router schemas."""

    def test_health_check_response(self):
        """HealthCheckResponse validates correctly."""
        data = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            database="connected",
            redis="connected",
        )
        assert data.status == HealthStatus.HEALTHY
        assert data.database == "connected"


class TestDeviceTypeRead:
    """Test DeviceTypeRead schema."""

    def test_device_type_read(self):
        """DeviceTypeRead serializes with deviceCount."""
        uid = uuid4()
        data = DeviceTypeRead(
            id=uid,
            name="Ноутбук",
            code="NB-001",
            category="computing",
            description="ПК",
            device_count=5,
        )
        assert data.name == "Ноутбук"
        assert data.device_count == 5
        assert data.model_dump(by_alias=True)["deviceCount"] == 5


class TestLocationRead:
    """Test LocationRead schema."""

    def test_location_read(self):
        """LocationRead validates."""
        uid = uuid4()
        data = LocationRead(
            id=uid,
            name="Каб. 101",
            building="Корпус А",
            floor="1",
            device_count=3,
        )
        assert data.name == "Каб. 101"
        assert data.device_count == 3


class TestPersonRead:
    """Test PersonRead schema."""

    def test_person_read(self):
        """PersonRead validates with fullName."""
        uid = uuid4()
        data = PersonRead(
            id=uid,
            full_name="Иванов И.И.",
            position="Админ",
            device_count=2,
        )
        assert data.full_name == "Иванов И.И."
        assert data.model_dump(by_alias=True)["fullName"] == "Иванов И.И."


class TestDeviceSchemas:
    """Test device schemas."""

    def test_device_read(self):
        """DeviceRead validates."""
        uid = uuid4()
        data = DeviceRead(
            id=uid,
            inventory_number="INV-001",
            name="Ноутбук",
            status=DeviceStatus.IN_USE,
            device_type_id=uid,
            location_id=uid,
        )
        assert data.status == DeviceStatus.IN_USE
        assert data.inventory_number == "INV-001"

    def test_device_create(self):
        """DeviceCreate validates required fields."""
        uid = uuid4()
        data = DeviceCreate(
            inventory_number="INV-001",
            name="Ноутбук",
            device_type_id=uid,
            location_id=uid,
            status=DeviceStatus.IN_USE,
        )
        assert data.name == "Ноутбук"
        assert data.person_id is None

    def test_device_update_partial(self):
        """DeviceUpdate allows partial updates."""
        data = DeviceUpdate(status=DeviceStatus.REPAIR)
        assert data.status == DeviceStatus.REPAIR
        assert data.name is None

    def test_audit_entry_read(self):
        """AuditEntryRead validates."""
        uid = uuid4()
        data = AuditEntryRead(
            id=uid,
            date=date(2025, 1, 15),
            action="Проведена инвентаризация",
            user="Иванов",
        )
        assert data.action == "Проведена инвентаризация"
        assert str(data.date) == "2025-01-15"
