"""Query client for SFMC Assets (Content Builder) API."""

from typing import TYPE_CHECKING

from ..models.assets import Asset, AssetFilter, AssetResponse

if TYPE_CHECKING:
    from ..client import AsyncSFMCClient, SFMCClient


class QueryClient:
    """Synchronous client for Content Builder asset query operations."""

    def __init__(self, client: "SFMCClient"):
        self._client = client

    def get_asset_by_id(self, asset_id: int) -> Asset:
        """Get a specific asset by ID.

        Args:
            asset_id: The asset ID to retrieve

        Returns:
            Asset model instance
        """
        response_data = self._client.get(f"/asset/v1/content/assets/{asset_id}")
        return Asset(**response_data)

    def get_assets(
        self,
        page: int | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        filter_expr: str | None = None,
        fields: str | None = None,
    ) -> AssetResponse:
        """Get assets with optional filtering and pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page (1-50)
            order_by: Sort order (e.g., 'Name desc', 'createdDate asc')
            filter_expr: Filter expression using SFMC operators
                (eq, neq, lt, lte, gt, gte, like)
            fields: Comma-separated list of fields to return

        Returns:
            AssetResponse with paginated results
        """
        # Create filter model and serialize to params
        filter_model = AssetFilter(
            page=page,
            page_size=page_size,
            order_by=order_by,
            filter=filter_expr,
            fields=fields,
        )
        params = filter_model.model_dump(by_alias=True, exclude_none=True)

        response_data = self._client.get("/asset/v1/content/assets", params=params)
        return AssetResponse(**response_data)


class AsyncQueryClient:
    """Asynchronous client for Content Builder asset query operations."""

    def __init__(self, client: "AsyncSFMCClient"):
        self._client = client

    async def get_asset_by_id(self, asset_id: int) -> Asset:
        """Get a specific asset by ID.

        Args:
            asset_id: The asset ID to retrieve

        Returns:
            Asset model instance
        """
        response_data = await self._client.get(f"/asset/v1/content/assets/{asset_id}")
        return Asset(**response_data)

    async def get_assets(
        self,
        page: int | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        filter_expr: str | None = None,
        fields: str | None = None,
    ) -> AssetResponse:
        """Get assets with optional filtering and pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page (1-50)
            order_by: Sort order (e.g., 'Name desc', 'createdDate asc')
            filter_expr: Filter expression using SFMC operators
                (eq, neq, lt, lte, gt, gte, like)
            fields: Comma-separated list of fields to return

        Returns:
            AssetResponse with paginated results
        """
        # Create filter model and serialize to params
        filter_model = AssetFilter(
            page=page,
            page_size=page_size,
            order_by=order_by,
            filter=filter_expr,
            fields=fields,
        )
        params = filter_model.model_dump(by_alias=True, exclude_none=True)

        response_data = await self._client.get(
            "/asset/v1/content/assets", params=params
        )
        return AssetResponse(**response_data)
