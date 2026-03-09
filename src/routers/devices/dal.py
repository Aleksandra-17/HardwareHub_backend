"""Data Access Layer для роутера devices."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.devices.models import AuditEntry, Device


class DeviceDAL:
    """DAL для работы с устройствами."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        device_type_id: str | None = None,
        location_id: str | None = None,
        person_id: str | None = None,
        sort: str = "inventoryNumber",
        order: str = "asc",
    ) -> list[Device]:
        """Список устройств с фильтрацией и сортировкой."""
        stmt = select(Device)
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(
                or_(
                    Device.inventory_number.ilike(q),
                    Device.name.ilike(q),
                    Device.serial_number.ilike(q),
                )
            )
        if status and status != "all":
            conditions.append(Device.status == status)
        if device_type_id and device_type_id != "all":
            conditions.append(Device.device_type_id == UUID(device_type_id))
        if location_id and location_id != "all":
            conditions.append(Device.location_id == UUID(location_id))
        if person_id and person_id != "all":
            conditions.append(Device.person_id == UUID(person_id))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        sort_map = {
            "inventoryNumber": Device.inventory_number,
            "name": Device.name,
            "status": Device.status,
            "commissionDate": Device.commission_date,
            "purchaseDate": Device.purchase_date,
            "purchasePrice": Device.purchase_price,
        }
        sort_column = sort_map.get(sort, Device.inventory_number)
        if order == "desc":
            sort_column = sort_column.desc()
        stmt = stmt.order_by(sort_column)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, device_id: UUID) -> Device | None:
        """Получить устройство по ID."""
        stmt = select(Device).where(Device.id == device_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        inventory_number: str,
        name: str,
        device_type_id: UUID,
        location_id: UUID,
        status: str,
        serial_number: str | None = None,
        model: str | None = None,
        manufacturer: str | None = None,
        person_id: UUID | None = None,
        commission_date: date | None = None,
        last_check_date: date | None = None,
        notes: str | None = None,
        purchase_price: Decimal | None = None,
        purchase_date: date | None = None,
        qr_code: str | None = None,
    ) -> Device:
        """Создать устройство."""
        device = Device(
            inventory_number=inventory_number,
            name=name,
            device_type_id=device_type_id,
            location_id=location_id,
            status=status,
            serial_number=serial_number,
            model=model,
            manufacturer=manufacturer,
            person_id=person_id,
            commission_date=commission_date,
            last_check_date=last_check_date,
            notes=notes,
            purchase_price=purchase_price,
            purchase_date=purchase_date,
            qr_code=qr_code,
        )
        self.session.add(device)
        await self.session.flush()
        await self.session.refresh(device)
        return device

    async def update(self, device: Device, **kwargs: object) -> Device:
        """Обновить устройство."""
        for key, value in kwargs.items():
            if hasattr(device, key) and value is not None:
                setattr(device, key, value)
        await self.session.flush()
        await self.session.refresh(device)
        return device

    async def delete(self, device: Device) -> None:
        """Удалить устройство."""
        await self.session.delete(device)


class AuditEntryDAL:
    """DAL для истории изменений."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        device_id: UUID | None,
        action: str,
        user: str,
    ) -> AuditEntry:
        """Создать запись аудита."""
        entry = AuditEntry(
            device_id=device_id,
            date=date.today(),
            action=action,
            user=user,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_by_device_id(self, device_id: UUID) -> list[AuditEntry]:
        """Получить историю изменений устройства."""
        stmt = (
            select(AuditEntry)
            .where(AuditEntry.device_id == device_id)
            .order_by(AuditEntry.date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
