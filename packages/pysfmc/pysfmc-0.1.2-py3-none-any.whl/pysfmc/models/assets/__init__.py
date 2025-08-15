"""Assets models for SFMC API."""

from .assets import (
    Asset,
    AssetFilter,
    AssetResponse,
    AssetType,
    AssetTypeCreate,
    CreateAsset,
    Owner,
    Status,
)
from .block_types import (
    create_block_by_name,
    create_block_by_type,
)
from .blocks import (
    Block,
    Slot,
)
from .categories import Category, CategoryCreate, CategoryFilter, CategoryResponse
from .views import (
    Channels,
    EmailViews,
    HtmlView,
    PreheaderView,
    SubjectLineView,
    TemplateReference,
    TextView,
)

__all__ = [
    # Category models
    "Category",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryFilter",
    # Asset models
    "Asset",
    "AssetResponse",
    "AssetFilter",
    "AssetType",
    "AssetTypeCreate",
    "CreateAsset",
    "Owner",
    "Status",
    # Block and slot models
    "Block",
    "Slot",
    # Specialized block types
    "create_block_by_type",
    "create_block_by_name",
    # View models
    "EmailViews",
    "HtmlView",
    "TextView",
    "SubjectLineView",
    "PreheaderView",
    "TemplateReference",
    "Channels",
]
