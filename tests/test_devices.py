"""Tests for devices router."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.routers.devices.actions import (
    delete_device,
    get_device,
    get_device_audit,
    list_devices,
)
from src.routers.devices.dal import AuditEntryDAL, DeviceDAL
from src.routers.devices.schemas import AuditEntryRead, DeviceRead


class TestDeviceDAL:
    """Test DeviceDAL."""

    @pytest.mark.asyncio
    async def test_get_list_empty(self):
        """DAL get_list returns empty when no devices."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = DeviceDAL(mock_session)
        result = await dal.get_list()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_id_none(self):
        """DAL get_by_id returns None when not found."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = DeviceDAL(mock_session)
        result = await dal.get_by_id(uuid4())

        assert result is None


class TestAuditEntryDAL:
    """Test AuditEntryDAL."""

    @pytest.mark.asyncio
    async def test_get_by_device_id_empty(self):
        """DAL get_by_device_id returns empty list."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        dal = AuditEntryDAL(mock_session)
        result = await dal.get_by_device_id(uuid4())

        assert result == []


class TestDevicesActions:
    """Test devices actions."""

    @pytest.mark.asyncio
    async def test_list_devices_empty(self):
        """list_devices returns empty list."""
        mock_session = AsyncMock()
        with patch.object(DeviceDAL, "get_list", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            result = await list_devices(mock_session)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_device_not_found(self):
        """get_device returns None when not found."""
        mock_session = AsyncMock()
        with patch.object(DeviceDAL, "get_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await get_device(mock_session, uuid4())

            assert result is None

    @pytest.mark.asyncio
    async def test_delete_device_not_found(self):
        """delete_device returns (False, None) when not found."""
        mock_session = AsyncMock()
        with patch.object(DeviceDAL, "get_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            ok, err = await delete_device(mock_session, uuid4(), username="test")

            assert ok is False
            assert err is None

    @pytest.mark.asyncio
    async def test_get_device_audit_not_found(self):
        """get_device_audit returns None when device not found."""
        mock_session = AsyncMock()
        with patch.object(DeviceDAL, "get_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await get_device_audit(mock_session, uuid4())

            assert result is None


class TestDevicesEndpoint:
    """Test devices API endpoints."""

    def test_get_devices_200(self, client_authenticated):
        """GET /api/devices returns 200."""
        with patch(
            "src.routers.devices.router.list_devices",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client_authenticated.get("/api/devices/")

            assert response.status_code == 200
            assert response.json() == []

    def test_get_device_404(self, client_authenticated):
        """GET /api/devices/{id} returns 404 when not found."""
        with patch(
            "src.routers.devices.router.get_device",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = client_authenticated.get(f"/api/devices/{uuid4()}")

            assert response.status_code == 404

    def test_post_device_201(self, client_authenticated):
        """POST /api/devices creates device."""
        uid = uuid4()
        device_read = DeviceRead(
            id=uid,
            inventoryNumber="INV-001",
            name="Ноутбук",
            status="in_use",
            deviceTypeId=uid,
            locationId=uid,
        )

        with patch(
            "src.routers.devices.router.create_device",
            new_callable=AsyncMock,
            return_value=device_read,
        ):
            response = client_authenticated.post(
                "/api/devices/",
                json={
                    "inventoryNumber": "INV-001",
                    "name": "Ноутбук",
                    "deviceTypeId": str(uid),
                    "locationId": str(uid),
                    "status": "in_use",
                },
            )

            assert response.status_code == 201

    def test_delete_device_404(self, client_authenticated):
        """DELETE /api/devices/{id} returns 404 when not found."""
        with patch(
            "src.routers.devices.router.delete_device",
            new_callable=AsyncMock,
            return_value=(False, None),
        ):
            response = client_authenticated.delete(f"/api/devices/{uuid4()}")

            assert response.status_code == 404

    def test_get_audit_404(self, client_authenticated):
        """GET /api/devices/{id}/audit returns 404 when device not found."""
        with patch(
            "src.routers.devices.router.get_device_audit",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = client_authenticated.get(f"/api/devices/{uuid4()}/audit")

            assert response.status_code == 404

    def test_get_device_200(self, client_authenticated):
        """GET /api/devices/{id} returns 200 when found."""
        uid = uuid4()
        device_read = DeviceRead(
            id=uid,
            inventoryNumber="INV-001",
            name="Ноутбук",
            status="in_use",
            deviceTypeId=uid,
            locationId=uid,
        )
        with patch(
            "src.routers.devices.router.get_device",
            new_callable=AsyncMock,
            return_value=device_read,
        ):
            response = client_authenticated.get(f"/api/devices/{uid}")

            assert response.status_code == 200
            assert response.json()["inventoryNumber"] == "INV-001"

    def test_patch_device_200(self, client_authenticated):
        """PATCH /api/devices/{id} returns 200 when updated."""
        uid = uuid4()
        device_read = DeviceRead(
            id=uid,
            inventoryNumber="INV-002",
            name="Обновлённый",
            status="in_use",
            deviceTypeId=uid,
            locationId=uid,
        )
        with patch(
            "src.routers.devices.router.update_device",
            new_callable=AsyncMock,
            return_value=device_read,
        ):
            response = client_authenticated.patch(
                f"/api/devices/{uid}",
                json={"name": "Обновлённый"},
            )

            assert response.status_code == 200

    def test_put_device_200(self, client_authenticated):
        """PUT /api/devices/{id} returns 200 when updated."""
        uid = uuid4()
        device_read = DeviceRead(
            id=uid,
            inventoryNumber="INV-002",
            name="Обновлённый",
            status="in_use",
            deviceTypeId=uid,
            locationId=uid,
        )
        with patch(
            "src.routers.devices.router.update_device",
            new_callable=AsyncMock,
            return_value=device_read,
        ):
            response = client_authenticated.put(
                f"/api/devices/{uid}",
                json={
                    "inventoryNumber": "INV-002",
                    "name": "Обновлённый",
                    "deviceTypeId": str(uid),
                    "locationId": str(uid),
                    "status": "in_use",
                },
            )

            assert response.status_code == 200

    def test_patch_device_404(self, client_authenticated):
        """PATCH /api/devices/{id} returns 404 when not found."""
        with patch(
            "src.routers.devices.router.update_device",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = client_authenticated.patch(
                f"/api/devices/{uuid4()}",
                json={"name": "test"},
            )

            assert response.status_code == 404

    def test_delete_device_204(self, client_authenticated):
        """DELETE /api/devices/{id} returns 204 when deleted."""
        with patch(
            "src.routers.devices.router.delete_device",
            new_callable=AsyncMock,
            return_value=(True, None),
        ):
            response = client_authenticated.delete(f"/api/devices/{uuid4()}")

            assert response.status_code == 204

    def test_get_audit_200(self, client_authenticated):
        """GET /api/devices/{id}/audit returns 200 with audit entries."""
        uid = uuid4()
        audit_data = [
            AuditEntryRead(id=uuid4(), date=date(2025, 1, 1), action="create", user="admin")
        ]
        with patch(
            "src.routers.devices.router.get_device_audit",
            new_callable=AsyncMock,
            return_value=audit_data,
        ):
            response = client_authenticated.get(f"/api/devices/{uid}/audit")

            assert response.status_code == 200
