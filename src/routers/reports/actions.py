"""Бизнес-логика роутера reports."""

import csv
import io
import uuid
from decimal import Decimal

from fastapi import HTTPException
from openpyxl import Workbook
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.device_types.models import DeviceType
from src.routers.devices.models import Device
from src.routers.locations.models import Location
from src.routers.people.models import Person
from src.routers.reports.schemas import (
    ExportRequest,
    InventoryDeviceItem,
    InventoryRequest,
    InventoryResponse,
)

STATUS_LABELS = {
    "in_use": "в использовании",
    "repair": "в ремонте",
    "scrapped": "списано",
    "archived": "архив",
}


async def export_devices(
    session: AsyncSession,
    req: ExportRequest,
) -> tuple[bytes, str, str]:
    """Экспорт устройств в CSV или Excel. Возвращает (content, content_type, filename)."""
    stmt = (
        select(
            Device,
            DeviceType.name.label("type_name"),
            Location.name.label("location_name"),
            Person.full_name.label("person_name"),
        )
        .outerjoin(DeviceType, Device.device_type_id == DeviceType.id)
        .outerjoin(Location, Device.location_id == Location.id)
        .outerjoin(Person, Device.person_id == Person.id)
    )
    if req.location_id:
        stmt = stmt.where(Device.location_id == req.location_id)
    if req.person_id:
        stmt = stmt.where(Device.person_id == req.person_id)
    stmt = stmt.order_by(Device.inventory_number)
    result = await session.execute(stmt)
    rows = result.all()

    def _row(d, tn, ln, pn):
        return (
            d.inventory_number or "",
            d.name or "",
            tn or "",
            STATUS_LABELS.get(d.status, d.status),
            d.serial_number or "",
            d.model or "",
            d.manufacturer or "",
            ln or "",
            pn or "",
            (d.commission_date.isoformat() if d.commission_date else ""),
            (d.purchase_date.isoformat() if d.purchase_date else ""),
            str(d.purchase_price) if d.purchase_price else "",
        )

    header = (
        "Инвентарный номер",
        "Наименование",
        "Тип",
        "Статус",
        "Серийный номер",
        "Модель",
        "Производитель",
        "Кабинет",
        "Ответственный",
        "Дата ввода",
        "Дата покупки",
        "Стоимость (₽)",
    )

    if req.format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(header)
        for r in rows:
            writer.writerow(_row(r[0], r[1], r[2], r[3]))
        return buf.getvalue().encode("utf-8-sig"), "text/csv", "devices-export.csv"

    wb = Workbook()
    ws = wb.active
    ws.title = "Устройства"
    ws.append(header)
    for r in rows:
        ws.append(_row(r[0], r[1], r[2], r[3]))
    buf = io.BytesIO()
    wb.save(buf)
    return (
        buf.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "devices-export.xlsx",
    )


async def create_inventory_report(
    session: AsyncSession,
    req: InventoryRequest,
) -> InventoryResponse:
    """Акт инвентаризации."""
    loc = await session.get(Location, req.location_id)
    person = await session.get(Person, req.person_id)
    if loc is None:
        raise HTTPException(status_code=404, detail="Кабинет не найден")
    if person is None:
        raise HTTPException(status_code=404, detail="Ответственное лицо не найдено")

    stmt = (
        select(Device)
        .where(
            and_(
                Device.location_id == req.location_id,
                Device.person_id == req.person_id,
                Device.status == "in_use",
            )
        )
        .order_by(Device.inventory_number)
    )
    result = await session.execute(stmt)
    devices = list(result.scalars().all())

    total = Decimal("0")
    items: list[InventoryDeviceItem] = []
    for d in devices:
        if d.purchase_price:
            total += d.purchase_price
        items.append(
            InventoryDeviceItem(
                inventoryNumber=d.inventory_number,
                name=d.name,
                serialNumber=d.serial_number,
                status=STATUS_LABELS.get(d.status, d.status),
                purchasePrice=d.purchase_price,
            )
        )

    year = req.end_date.year
    doc_num = f"АКТ-{year}-{uuid.uuid4().hex[:6].upper()}"

    return InventoryResponse(
        id=uuid.uuid4(),
        documentNumber=doc_num,
        date=req.end_date,
        locationName=loc.name,
        personName=person.full_name,
        deviceCount=len(devices),
        totalPrice=total,
        devices=items,
    )
