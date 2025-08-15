"""Assets clients for SFMC API."""

from .categories import AsyncCategoriesClient, CategoriesClient
from .client import AssetsClient, AsyncAssetsClient
from .query import AsyncQueryClient, QueryClient

__all__ = [
    "AssetsClient",
    "AsyncAssetsClient",
    "CategoriesClient",
    "AsyncCategoriesClient",
    "QueryClient",
    "AsyncQueryClient",
]
