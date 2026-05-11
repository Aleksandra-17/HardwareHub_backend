"""Бизнес-логика роутера devices."""

from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

from src.routers.device_types.models import DeviceType
from src.routers.devices.dal import AuditEntryDAL, DeviceDAL
from src.routers.devices.schemas import (
    AuditEntryRead,
    DeviceComponentRead,
    DeviceCreate,
    DeviceRead,
    DeviceRebuild,
    DeviceUpdate,
)

DETACHED_STATUSES = {"archived", "scrapped"}


async def _ensure_workstation_for_location(
    session: AsyncSession,
    workstation_id: UUID | None,
    location_id: UUID | None,
) -> None:
    """Убедиться, что рабочее место в том же кабинете, что и учётная привязка устройства."""
    if workstation_id is None:
        return
    if location_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Нельзя привязать рабочее место без кабинета",
        )
    from src.routers.workstations.models import Workstation

    ws = await session.get(Workstation, workstation_id)
    if ws is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Рабочее место не найдено",
        )
    if ws.location_id != location_id:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Рабочее место не принадлежит выбранному кабинету",
        )


def _validate_location_by_status(
    *,
    status_value: str,
    location_id: UUID | None,
    workstation_id: UUID | None,
) -> None:
    """Проверить правила привязки кабинета/места к статусу."""
    if status_value in DETACHED_STATUSES:
        if location_id is not None or workstation_id is not None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Для archived/scrapped кабинет и рабочее место должны быть пустыми",
            )
        return
    if status_value == "in_use" and location_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Для статуса in_use кабинет обязателен",
        )


def _supports_components(device_type: DeviceType | None) -> bool:
    """Разрешена ли сборка комплектующих для данного типа устройства."""
    if device_type is None:
        return False
    code = (device_type.code or "").upper()
    name = (device_type.name or "").strip().lower()
    return code in {"PC", "SRV"} or name in {"пк", "сервер"}


async def _ensure_components_host_type(
    session: AsyncSession,
    device_type_id: UUID,
    *,
    has_components: bool,
) -> None:
    """Проверить, что комплектующие создаются только для ПК/сервера."""
    if not has_components:
        return
    dt = await session.get(DeviceType, device_type_id)
    if not _supports_components(dt):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Комплектующие можно задавать только для ПК или сервера",
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
    status_value = data.status.value
    _validate_location_by_status(
        status_value=status_value,
        location_id=data.location_id,
        workstation_id=data.workstation_id,
    )
    await _ensure_components_host_type(
        session,
        data.device_type_id,
        has_components=len(data.components) > 0,
    )
    await _ensure_workstation_for_location(session, data.workstation_id, data.location_id)
    today = date.today()
    dal = DeviceDAL(session)
    device = await dal.create(
        inventory_number=data.inventory_number,
        name=data.name,
        device_type_id=data.device_type_id,
        location_id=data.location_id,
        workstation_id=data.workstation_id,
        status=status_value,
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
    if data.components:
        from src.routers.components.dal import ComponentDAL

        comp_dal = ComponentDAL(session)
        for comp in data.components:
            component = await comp_dal.create(
                name=comp.name,
                component_type=comp.component_type.value,
                status=comp.status.value,
                arrival_date=comp.arrival_date,
                expiry_date=comp.expiry_date,
                notes=comp.notes,
            )
            await comp_dal.attach(component.id, device.id)
    fresh = await dal.get_by_id(device.id)
    if fresh is None:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось прочитать созданное устройство",
        )
    return _device_to_read(fresh)


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
        "workstation_id": "Рабочее место",
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
    # Сменили кабинет — расходится с текущим РМ или кабинет сняли
    if "location_id" in kwargs:
        if kwargs["location_id"] is None:
            kwargs["workstation_id"] = None
        elif device.workstation_id and "workstation_id" not in update_data:
            from src.routers.workstations.models import Workstation

            ws_live = await session.get(Workstation, device.workstation_id)
            if ws_live is not None and ws_live.location_id != kwargs["location_id"]:
                kwargs["workstation_id"] = None

    effective_location = kwargs.get("location_id") if "location_id" in kwargs else device.location_id
    if "workstation_id" in kwargs:
        await _ensure_workstation_for_location(session, kwargs["workstation_id"], effective_location)

    if "status" in kwargs and kwargs["status"] is not None:
        kwargs["status"] = kwargs["status"].value
        if kwargs["status"] in DETACHED_STATUSES:
            kwargs["location_id"] = None
            kwargs["workstation_id"] = None

    final_status = kwargs.get("status", device.status)
    final_location = kwargs.get("location_id", device.location_id)
    final_workstation = kwargs.get("workstation_id", device.workstation_id)
    _validate_location_by_status(
        status_value=final_status,
        location_id=final_location,
        workstation_id=final_workstation,
    )
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
    fresh = await dal.get_by_id(device.id)
    if fresh is None:
        return None
    return _device_to_read(fresh)


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


async def rebuild_device_components(
    session: AsyncSession,
    device_id: UUID,
    data: DeviceRebuild,
    *,
    username: str,
) -> DeviceRead | None:
    """Пересобрать комплектующие ПК пакетно."""
    from src.routers.components.dal import ComponentDAL

    dev_dal = DeviceDAL(session)
    comp_dal = ComponentDAL(session)
    device = await dev_dal.get_by_id(device_id)
    if device is None:
        return None
    live = await comp_dal.get_device_with_type(device_id)
    if not comp_dal.is_components_host_device(live):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Пересборка доступна только для ПК или сервера",
        )

    existing = await comp_dal.get_list(computer_id=device_id)
    existing_by_type = {c.component_type: c for c in existing}
    desired_by_type = {item.component_type.value: item.component_id for item in data.items}

    # Отвязать то, что не входит в новую сборку.
    for comp_type, comp in existing_by_type.items():
        target_id = desired_by_type.get(comp_type)
        if target_id is None or target_id != comp.id:
            await comp_dal.detach(comp.id)

    # Привязать/заменить выбранные комплектующие.
    for item in data.items:
        component = await comp_dal.get_by_id(item.component_id)
        if component is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Комплектующая {item.component_id} не найдена",
            )
        if component.component_type != item.component_type.value:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Тип комплектующей не совпадает с позицией сборки",
            )
        await comp_dal.attach(component.id, device_id)

    audit_dal = AuditEntryDAL(session)
    await audit_dal.create(
        device_id=device.id,
        action="Выполнена пересборка комплектующих ПК",
        user=username,
    )
    device = await dev_dal.get_by_id(device_id)
    return _device_to_read(device) if device is not None else None


def _device_to_read(device) -> DeviceRead:
    """Конвертировать модель Device в DeviceRead."""
    from src.routers.devices.enums import DeviceStatus

    status = (
        device.status if isinstance(device.status, DeviceStatus) else DeviceStatus(device.status)
    )
    ws_code = None
    if device.workstation is not None:
        ws_code = device.workstation.seat_code
    components = []
    for link in device.computer_components:
        if link.component is None:
            continue
        components.append(
            DeviceComponentRead(
                id=link.component.id,
                name=link.component.name,
                component_type=link.component.component_type,
                status=link.component.status,
                arrival_date=link.component.arrival_date,
                expiry_date=link.component.expiry_date,
                notes=link.component.notes,
            )
        )
    components.sort(key=lambda c: c.component_type.value)
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
        workstation_id=device.workstation_id,
        workstation_seat_code=ws_code,
        person_id=device.person_id,
        commission_date=device.commission_date,
        last_check_date=device.last_check_date,
        notes=device.notes,
        purchase_price=device.purchase_price,
        purchase_date=device.purchase_date,
        qr_code=device.qr_code,
        components=components,
    )
