"""Categories client for SFMC Assets (Content Builder) API."""

from typing import TYPE_CHECKING, Literal

from ..models.assets import Category, CategoryCreate, CategoryFilter, CategoryResponse

if TYPE_CHECKING:
    from ..client import AsyncSFMCClient, SFMCClient


class CategoriesClient:
    """Synchronous client for Content Builder category operations."""

    def __init__(self, client: "SFMCClient"):
        self._client = client

    def get_categories(
        self,
        page: int | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        filter_expr: str | None = None,
        scope: str | None = None,
        parent_id: int | None = None,
    ) -> CategoryResponse:
        """Get categories with optional filtering and pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page (1-50)
            order_by: Sort order (e.g., 'name asc', 'name desc')
            filter_expr: Filter expression (only 'parentId eq <value>' supported)
            scope: Scope filter (e.g., 'Shared')
            parent_id: Filter by parent category ID

        Returns:
            CategoryResponse with paginated results
        """
        # Build filter expression combining filter_expr and parent_id
        combined_filter = filter_expr
        if parent_id is not None:
            parent_filter = f"parentId eq {parent_id}"
            if filter_expr:
                combined_filter = f"({filter_expr}) and ({parent_filter})"
            else:
                combined_filter = parent_filter

        # Create filter model and serialize to params
        filter_model = CategoryFilter(
            page=page,
            page_size=page_size,
            order_by=order_by,
            filter=combined_filter,
            scope=scope,
        )
        params = filter_model.model_dump(by_alias=True, exclude_none=True)

        response_data = self._client.get("/asset/v1/content/categories", params=params)
        return CategoryResponse(**response_data)

    def get_category_by_id(self, category_id: int) -> Category:
        """Get a specific category by ID.

        Args:
            category_id: The category ID to retrieve

        Returns:
            Category model instance
        """
        response_data = self._client.get(f"/asset/v1/content/categories/{category_id}")
        return Category(**response_data)

    def create_category(
        self,
        name: str,
        parent_id: int,
    ) -> Category:
        """Create a new category.

        Args:
            name: Category name
            parent_id: Parent category ID

        Returns:
            Created Category model instance
        """
        category_data = CategoryCreate(name=name, parent_id=parent_id)

        response_data = self._client.post(
            "/asset/v1/content/categories", json=category_data
        )
        return Category(**response_data)

    def delete_category_by_id(self, category_id: int) -> Literal["OK"]:
        return self._client.delete(f"/asset/v1/content/categories/{category_id}")  # type: ignore


class AsyncCategoriesClient:
    """Asynchronous client for Content Builder category operations."""

    def __init__(self, client: "AsyncSFMCClient"):
        self._client = client

    async def get_categories(
        self,
        page: int | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        filter_expr: str | None = None,
        scope: str | None = None,
        parent_id: int | None = None,
    ) -> CategoryResponse:
        """Get categories with optional filtering and pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page (1-50)
            order_by: Sort order (e.g., 'name asc', 'name desc')
            filter_expr: Filter expression (only 'parentId eq <value>' supported)
            scope: Scope filter (e.g., 'Shared')
            parent_id: Filter by parent category ID

        Returns:
            CategoryResponse with paginated results
        """
        # Build filter expression combining filter_expr and parent_id
        combined_filter = filter_expr
        if parent_id is not None:
            parent_filter = f"parentId eq {parent_id}"
            if filter_expr:
                combined_filter = f"({filter_expr}) and ({parent_filter})"
            else:
                combined_filter = parent_filter

        # Create filter model and serialize to params
        filter_model = CategoryFilter(
            page=page,
            page_size=page_size,
            order_by=order_by,
            filter=combined_filter,
            scope=scope,
        )
        params = filter_model.model_dump(by_alias=True, exclude_none=True)

        response_data = await self._client.get(
            "/asset/v1/content/categories", params=params
        )
        return CategoryResponse(**response_data)

    async def get_category_by_id(self, category_id: int) -> Category:
        """Get a specific category by ID.

        Args:
            category_id: The category ID to retrieve

        Returns:
            Category model instance
        """
        response_data = await self._client.get(
            f"/asset/v1/content/categories/{category_id}"
        )
        return Category(**response_data)

    async def create_category(
        self,
        name: str,
        parent_id: int,
    ) -> Category:
        """Create a new category.

        Args:
            name: Category name
            parent_id: Parent category ID

        Returns:
            Created Category model instance
        """
        category_data = CategoryCreate(
            name=name,
            parent_id=parent_id,
        )

        response_data = await self._client.post(
            "/asset/v1/content/categories", json=category_data
        )
        return Category(**response_data)

    async def delete_category_by_id(self, category_id: int) -> Literal["OK"]:
        response = await self._client.delete(
            f"/asset/v1/content/categories/{category_id}"
        )
        return response  # type: ignore
