"""Бизнес-логика роутера devices."""

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.devices.dal import AuditEntryDAL, DeviceDAL
from src.routers.devices.schemas import (
    AuditEntryRead,
    DeviceCreate,
    DeviceRead,
    DeviceUpdate,
)


async def list_devices(
    session: AsyncSession,
    *,
    search: str | None = None,
    status: str | None = None,
    device_type_id: str | None = None,
    location_id: str | None = None,
    person_id: str | None = None,
    sort: str = "inventoryNumber",
    order: str = "asc",
) -> list[DeviceRead]:
    """Список устройств с фильтрацией."""
    dal = DeviceDAL(session)
    devices = await dal.get_list(
        search=search,
        status=status,
        device_type_id=device_type_id,
        location_id=location_id,
        person_id=person_id,
        sort=sort,
        order=order,
    )
    return [_device_to_read(d) for d in devices]


async def get_device(
    session: AsyncSession,
    device_id: UUID,
    *,
    update_last_check: bool = False,
) -> DeviceRead | None:
    """Получить устройство по ID. Если update_last_check, обновить lastCheckDate."""
    dal = DeviceDAL(session)
    device = await dal.get_by_id(device_id)
    if device is None:
        return None
    if update_last_check:
        await dal.update(device, last_check_date=date.today())
    return _device_to_read(device)


async def create_device(
    session: AsyncSession,
    data: DeviceCreate,
    *,
    username: str,
) -> DeviceRead:
    """Создать устройство."""
    today = date.today()
    dal = DeviceDAL(session)
    device = await dal.create(
        inventory_number=data.inventory_number,
        name=data.name,
        device_type_id=data.device_type_id,
        location_id=data.location_id,
        status=data.status.value,
        serial_number=data.serial_number,
        model=data.model,
        manufacturer=data.manufacturer,
        person_id=data.person_id,
        commission_date=data.commission_date,
        last_check_date=data.last_check_date or today,
        notes=data.notes,
        purchase_price=data.purchase_price,
        purchase_date=data.purchase_date,
        qr_code=data.qr_code,
    )
    audit_dal = AuditEntryDAL(session)
    await audit_dal.create(
        device_id=device.id,
        action="Устройство создано",
        user=username,
    )
    return _device_to_read(device)


def _field_label(field: str) -> str:
    """Человекочитаемое название поля."""
    labels = {
        "status": "Статус",
        "name": "Наименование",
        "inventory_number": "Инвентарный номер",
        "serial_number": "Серийный номер",
        "model": "Модель",
        "manufacturer": "Производитель",
        "location_id": "Кабинет",
        "person_id": "Ответственный",
        "commission_date": "Дата ввода",
        "purchase_date": "Дата покупки",
        "purchase_price": "Стоимость",
        "notes": "Заметки",
    }
    return labels.get(field, field)


async def update_device(
    session: AsyncSession,
    device_id: UUID,
    data: DeviceUpdate,
    *,
    username: str,
) -> DeviceRead | None:
    """Обновить устройство."""
    dal = DeviceDAL(session)
    device = await dal.get_by_id(device_id)
    if device is None:
        return None
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    kwargs = {k: v for k, v in update_data.items() if hasattr(device, k)}
    if "status" in kwargs and kwargs["status"] is not None:
        kwargs["status"] = kwargs["status"].value
    audit_actions = []
    for key, new_val in kwargs.items():
        old_val = getattr(device, key, None)
        if old_val != new_val:
            if key == "status":
                audit_actions.append(f"Статус изменен на {new_val}")
            else:
                label = _field_label(key)
                audit_actions.append(f"{label} изменено с {old_val} на {new_val}")
    device = await dal.update(device, **kwargs)
    audit_dal = AuditEntryDAL(session)
    for action in audit_actions:
        await audit_dal.create(device_id=device.id, action=action, user=username)
    return _device_to_read(device)


async def delete_device(
    session: AsyncSession,
    device_id: UUID,
    *,
    username: str,
) -> tuple[bool, str | None]:
    """Удалить устройство. Возвращает (ok, error_message)."""
    dal = DeviceDAL(session)
    device = await dal.get_by_id(device_id)
    if device is None:
        return False, None
    from src.routers.devices.enums import DeviceStatus

    status = device.status if isinstance(device.status, str) else device.status.value
    if status not in (DeviceStatus.SCRAPPED.value, DeviceStatus.ARCHIVED.value):
        return False, "Можно удалять только устройства со статусом scrapped или archived"
    audit_dal = AuditEntryDAL(session)
    await audit_dal.create(
        device_id=device.id,
        action="Устройство удалено",
        user=username,
    )
    await dal.delete(device)
    return True, None


async def generate_device_qr(
    session: AsyncSession,
    device_id: UUID,
) -> str | None:
    """Сгенерировать QR-код для устройства. Возвращает base64 data URI или None если не найдено."""
    import base64
    import io

    import qrcode

    dal = DeviceDAL(session)
    device = await dal.get_by_id(device_id)
    if device is None:
        return None
    content = device.inventory_number
    img = qrcode.make(content)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    data_uri = f"data:image/png;base64,{b64}"
    return data_uri


async def get_device_audit(
    session: AsyncSession,
    device_id: UUID,
) -> list[AuditEntryRead] | None:
    """История изменений устройства."""
    dal = DeviceDAL(session)
    device = await dal.get_by_id(device_id)
    if device is None:
        return None
    audit_dal = AuditEntryDAL(session)
    entries = await audit_dal.get_by_device_id(device_id)
    return [AuditEntryRead(id=e.id, date=e.date, action=e.action, user=e.user) for e in entries]


def _device_to_read(device) -> DeviceRead:
    """Конвертировать модель Device в DeviceRead."""
    from src.routers.devices.enums import DeviceStatus

    status = (
        device.status if isinstance(device.status, DeviceStatus) else DeviceStatus(device.status)
    )
    return DeviceRead(
        id=device.id,
        inventory_number=device.inventory_number,
        name=device.name,
        device_type_id=device.device_type_id,
        serial_number=device.serial_number,
        model=device.model,
        manufacturer=device.manufacturer,
        status=status,
        location_id=device.location_id,
        person_id=device.person_id,
        commission_date=device.commission_date,
        last_check_date=device.last_check_date,
        notes=device.notes,
        purchase_price=device.purchase_price,
        purchase_date=device.purchase_date,
        qr_code=device.qr_code,
    )
