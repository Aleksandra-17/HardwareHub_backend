"""Роутер reports."""

from fastapi import APIRouter
from fastapi.responses import Response

from src.database.dependencies import DbSession
from src.routers.auth.dependencies import CurrentUser
from src.routers.reports.actions import create_inventory_report, export_devices
from src.routers.reports.schemas import ExportRequest, InventoryRequest, InventoryResponse

router = APIRouter()


@router.post(
    "/devices/export",
    summary="Экспорт устройств в CSV/Excel",
    responses={
        200: {
            "content": {"text/csv": {}},
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
        }
    },
)
async def post_devices_export(
    session: DbSession,
    data: ExportRequest,
    _user: CurrentUser,
) -> Response:
    """Экспорт устройств в CSV или Excel."""
    content, media_type, filename = await export_devices(session, data)
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post(
    "/inventory",
    response_model=InventoryResponse,
    summary="Акт инвентаризации",
    responses={404: {"description": "Кабинет или ответственный не найдены"}},
)
async def post_inventory(
    session: DbSession,
    data: InventoryRequest,
    _user: CurrentUser,
) -> InventoryResponse:
    """Сформировать акт инвентаризации по кабинету и ответственному."""
    return await create_inventory_report(session, data)
