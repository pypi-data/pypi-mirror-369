"""Main Assets client for SFMC Assets (Content Builder) API."""

from typing import TYPE_CHECKING

from .categories import AsyncCategoriesClient, CategoriesClient
from .content import AsyncContentClient, ContentClient
from .query import AsyncQueryClient, QueryClient

if TYPE_CHECKING:
    from ..client import AsyncSFMCClient, SFMCClient


class AssetsClient:
    """Synchronous client for SFMC Assets (Content Builder) API."""

    def __init__(self, client: "SFMCClient"):
        self._client = client
        self._categories: CategoriesClient | None = None
        self._content: ContentClient | None = None
        self._query: QueryClient | None = None

    @property
    def categories(self) -> CategoriesClient:
        """Access to categories (folders) operations."""
        if self._categories is None:
            self._categories = CategoriesClient(self._client)
        return self._categories

    @property
    def content(self) -> ContentClient:
        """Access to asset content operations."""
        if self._content is None:
            self._content = ContentClient(self._client)
        return self._content

    @property
    def query(self) -> QueryClient:
        """Access to asset query operations."""
        if self._query is None:
            self._query = QueryClient(self._client)
        return self._query


class AsyncAssetsClient:
    """Asynchronous client for SFMC Assets (Content Builder) API."""

    def __init__(self, client: "AsyncSFMCClient"):
        self._client = client
        self._categories: AsyncCategoriesClient | None = None
        self._content: AsyncContentClient | None = None
        self._query: AsyncQueryClient | None = None

    @property
    def categories(self) -> AsyncCategoriesClient:
        """Access to categories (folders) operations."""
        if self._categories is None:
            self._categories = AsyncCategoriesClient(self._client)
        return self._categories

    @property
    def content(self) -> AsyncContentClient:
        """Access to asset content operations."""
        if self._content is None:
            self._content = AsyncContentClient(self._client)
        return self._content

    @property
    def query(self) -> AsyncQueryClient:
        """Access to asset query operations."""
        if self._query is None:
            self._query = AsyncQueryClient(self._client)
        return self._query
