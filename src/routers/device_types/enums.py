"""Enums для роутера device_types."""

from enum import Enum


class Category(str, Enum):
    """Категория типа устройства."""

    COMPUTING = "computing"
    OFFICE = "office"
    NETWORK = "network"
    OTHER = "other"
