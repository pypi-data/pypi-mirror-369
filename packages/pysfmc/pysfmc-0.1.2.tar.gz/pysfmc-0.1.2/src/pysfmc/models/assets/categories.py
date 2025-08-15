"""Category models for SFMC Assets (Content Builder) API."""

from pydantic import BaseModel, Field

from ..base import SFMC_MODEL_CONFIG


class Category(BaseModel):
    """Model for SFMC Content Builder category (folder)."""

    model_config = SFMC_MODEL_CONFIG

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: str | None = Field(None, description="Category description")
    parent_id: int | None = Field(
        None, alias="parentId", description="Parent category ID"
    )
    category_type: str | None = Field(
        None, alias="categoryType", description="Category type (e.g., 'asset')"
    )
    enterprise_id: int | None = Field(
        None, alias="enterpriseId", description="Enterprise ID"
    )
    member_id: int | None = Field(None, alias="memberId", description="Member ID")


class CategoryCreate(BaseModel):
    """Model for creating a new category."""

    model_config = SFMC_MODEL_CONFIG

    name: str = Field(..., alias="Name", description="Category name", min_length=1)
    parent_id: int = Field(..., alias="ParentId", description="Parent category ID")


class CategoryResponse(BaseModel):
    """Model for paginated category response."""

    model_config = SFMC_MODEL_CONFIG

    count: int = Field(..., description="Total number of categories")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(
        ..., alias="pageSize", description="Number of items per page"
    )
    items: list[Category] = Field(
        default_factory=list, description="List of categories"
    )
    links: dict = Field(default_factory=dict, description="Pagination links")


class CategoryFilter(BaseModel):
    """Model for category filtering parameters."""

    model_config = SFMC_MODEL_CONFIG

    page: int | None = Field(None, alias="$page", description="Page number", ge=1)
    page_size: int | None = Field(
        None, alias="$pageSize", description="Items per page", ge=1, le=50
    )
    order_by: str | None = Field(
        None, alias="$orderBy", description="Sort order (e.g., 'name asc')"
    )
    filter: str | None = Field(
        None,
        alias="$filter",
        description="Filter expression (only 'parentId eq <value>' is supported)",
    )
    scope: str | None = Field(None, description="Scope (e.g., 'Shared')")
    parent_id: int | None = Field(None, description="Filter by parent ID")
