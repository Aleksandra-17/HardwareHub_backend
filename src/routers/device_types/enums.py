"""Enums для роутера device_types."""

from enum import StrEnum


class Category(StrEnum):
    """Категория типа устройства."""

    COMPUTING = "computing"
    OFFICE = "office"
    NETWORK = "network"
    OTHER = "other"
