"""Tests for enums."""

from src.routers.device_types.enums import Category
from src.routers.devices.enums import DeviceStatus


class TestDeviceStatus:
    """Test DeviceStatus enum."""

    def test_device_status_values(self):
        """DeviceStatus has expected values."""
        assert DeviceStatus.IN_USE.value == "in_use"
        assert DeviceStatus.REPAIR.value == "repair"
        assert DeviceStatus.SCRAPPED.value == "scrapped"
        assert DeviceStatus.ARCHIVED.value == "archived"


class TestCategory:
    """Test Category enum."""

    def test_category_values(self):
        """Category has expected values."""
        assert Category.COMPUTING.value == "computing"
        assert Category.OFFICE.value == "office"
        assert Category.NETWORK.value == "network"
        assert Category.OTHER.value == "other"
