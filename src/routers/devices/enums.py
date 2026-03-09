"""Enums для роутера devices."""

from enum import Enum


class DeviceStatus(str, Enum):
    """Статус устройства."""

    IN_USE = "in_use"
    REPAIR = "repair"
    SCRAPPED = "scrapped"
    ARCHIVED = "archived"
