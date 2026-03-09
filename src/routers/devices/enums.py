"""Enums для роутера devices."""

from enum import StrEnum


class DeviceStatus(StrEnum):
    """Статус устройства."""

    IN_USE = "in_use"
    REPAIR = "repair"
    SCRAPPED = "scrapped"
    ARCHIVED = "archived"
