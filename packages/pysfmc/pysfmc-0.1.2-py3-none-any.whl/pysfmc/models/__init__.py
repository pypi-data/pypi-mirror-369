"""Data models for SFMC API responses and requests."""

from .assets import Category, CategoryCreate, CategoryFilter, CategoryResponse
from .base import SFMC_MODEL_CONFIG

__all__ = [
    "SFMC_MODEL_CONFIG",
    "Category",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryFilter",
]
