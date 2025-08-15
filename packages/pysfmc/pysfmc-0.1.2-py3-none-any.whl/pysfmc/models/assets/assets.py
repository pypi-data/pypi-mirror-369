"""Asset models for SFMC Assets (Content Builder) API."""

from typing import Any

from pydantic import BaseModel, Field

from ..base import SFMC_MODEL_CONFIG
from .asset_types import ASSET_TYPE_MAPPING
from .categories import Category


class AssetType(BaseModel):
    """Model for SFMC Asset Type information."""

    model_config = SFMC_MODEL_CONFIG

    id: int | None = Field(None, description="Asset type ID")
    name: str | None = Field(None, description="Asset type name")
    display_name: str | None = Field(
        None, alias="displayName", description="Asset type display name"
    )

    @classmethod
    def from_name(cls, name: str) -> "AssetType":
        if not cls.has_name(name):
            raise KeyError(
                f"Asset name '{name}' is unknown. "
                f"Available names are in {ASSET_TYPE_MAPPING.keys()}"
            )

        return cls(name=name, id=ASSET_TYPE_MAPPING[name], displayName=None)

    @classmethod
    def has_name(cls, name: str) -> bool:
        return name in ASSET_TYPE_MAPPING


class Owner(BaseModel):
    """Model for SFMC asset owner/user information."""

    model_config = SFMC_MODEL_CONFIG

    id: int | None = Field(None, description="User ID")
    user_id: str | None = Field(None, alias="userId", description="User ID as string")
    email: str | None = Field(None, description="User email")
    name: str | None = Field(None, description="User name")


class Status(BaseModel):
    """Model for SFMC asset status information."""

    model_config = SFMC_MODEL_CONFIG

    id: int | None = Field(None, description="Status ID")
    name: str | None = Field(None, description="Status name")


class ThumbNail(BaseModel):
    model_config = SFMC_MODEL_CONFIG

    thumbnail_url: str | None = Field(
        None, alias="thumbnailUrl", description="Asset thumbnail URL"
    )


class Asset(BaseModel):
    """Model for SFMC Content Builder asset.

    Based on official SFMC Asset API specification.
    All fields are optional to handle different asset response formats.
    """

    model_config = SFMC_MODEL_CONFIG

    # Core identifiers (read-only, searchable)
    id: int | None = Field(None, description="Asset ID (read-only, searchable)")
    customer_key: str | None = Field(
        None, alias="customerKey", description="Customer key reference (searchable)"
    )
    object_id: str | None = Field(
        None, alias="objectID", description="Object ID (searchable)"
    )

    # Asset metadata
    name: str | None = Field(None, description="Asset name (required for creation)")
    description: str | None = Field(None, description="Asset description")
    content_type: str | None = Field(
        None, alias="contentType", description="Content type"
    )
    asset_type: AssetType | None = Field(
        None, alias="assetType", description="Asset type information"
    )
    available_views: list[str] | None = Field(
        None, alias="availableViews", description="Available views for the asset"
    )
    legacy_data: dict[str, Any] | None = Field(
        None, alias="legacyData", description="Legacy data information"
    )
    model_version: int | None = Field(
        None, alias="modelVersion", description="Model version"
    )

    # Content and design fields
    content: str | None = Field(None, description="Asset content")
    design: str | None = Field(None, description="Asset design")
    super_content: str | None = Field(
        None, alias="superContent", description="Asset super content"
    )
    generate_from: str | None = Field(
        None, alias="generateFrom", description="Generate from reference"
    )

    # Data and metadata
    data: dict[str, Any] | None = Field(None, description="Asset data object")
    meta: dict[str, Any] | None = Field(None, description="Asset metadata")
    custom_fields: dict[str, Any] | None = Field(
        None, alias="customFields", description="Custom field data"
    )

    # Template and structure fields
    views: dict[str, Any] | None = Field(
        None, description="Asset views (email template slots, etc.)"
    )
    slots: dict[str, Any] | None = Field(None, description="Asset slots")
    blocks: dict[str, Any] | None = Field(None, description="Asset blocks")
    template: dict[str, Any] | None = Field(None, description="Template information")
    min_blocks: int | None = Field(
        None, alias="minBlocks", description="Minimum number of blocks"
    )
    max_blocks: int | None = Field(
        None, alias="maxBlocks", description="Maximum number of blocks"
    )

    # Version and status
    version: int | None = Field(
        None, description="Asset version number (read-only, searchable)"
    )
    locked: bool | None = Field(None, description="Whether asset is locked")
    status: Status | None = Field(None, description="Asset status information")

    # Date fields
    active_date: str | None = Field(
        None, alias="activeDate", description="Asset active date"
    )
    expiration_date: str | None = Field(
        None, alias="expirationDate", description="Asset expiration date"
    )
    created_date: str | None = Field(
        None, alias="createdDate", description="Creation date (read-only, searchable)"
    )
    modified_date: str | None = Field(
        None,
        alias="modifiedDate",
        description="Last modified date (read-only, searchable)",
    )

    # Organization and categorization
    category: Category | None = Field(None, description="Asset category information")
    tags: list[str] | None = Field(None, description="Asset tags")
    channels: dict[str, Any] | None = Field(None, description="Channel information")

    # Ownership (read-only, searchable)
    owner: Owner | None = Field(
        None, description="Asset owner information (read-only, searchable)"
    )
    created_by: Owner | None = Field(
        None,
        alias="createdBy",
        description="Created by user information (read-only, searchable)",
    )
    modified_by: Owner | None = Field(
        None,
        alias="modifiedBy",
        description="Last modified by user information (read-only, searchable)",
    )

    # Enterprise and member info (read-only, searchable)
    enterprise_id: int | None = Field(
        None, alias="enterpriseId", description="Enterprise ID (read-only, searchable)"
    )
    member_id: int | None = Field(
        None, alias="memberId", description="Member ID (read-only, searchable)"
    )

    # File and media properties
    file: dict[str, Any] | None = Field(None, description="File information")
    thumbnail: ThumbNail | None = Field(None, description="Asset thumbnail information")

    # Business unit and availability
    business_unit_availability: dict[str, Any] | None = Field(
        None,
        alias="businessUnitAvailability",
        description="Business unit availability settings",
    )


class AssetResponse(BaseModel):
    """Model for paginated asset response."""

    model_config = SFMC_MODEL_CONFIG

    count: int = Field(..., description="Total number of assets")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(
        ..., alias="pageSize", description="Number of items per page"
    )
    items: list[Asset] = Field(default_factory=list, description="List of assets")
    links: dict[str, Any] | None = Field(
        default_factory=dict, description="Pagination links"
    )


class AssetTypeCreate(BaseModel):
    """Model for asset type information when creating assets."""

    model_config = SFMC_MODEL_CONFIG

    name: str = Field(..., description="Asset type name (e.g., 'htmlemail')")
    id: int = Field(..., description="Asset type ID")


class CreateAsset(BaseModel):
    """Model for creating a new SFMC asset.

    Based on the official SFMC Asset API specification for asset creation.
    """

    model_config = SFMC_MODEL_CONFIG

    # Required fields
    customer_key: str | None = Field(
        None, alias="customerKey", description="Customer key reference"
    )
    content_type: str | None = Field(
        None, alias="contentType", description="Content type"
    )
    asset_type: AssetTypeCreate = Field(
        ..., alias="assetType", description="Asset type info"
    )
    name: str = Field(..., max_length=200, description="Asset name")

    # Core optional fields
    description: str | None = Field(None, description="Asset description")

    # Content structure fields
    views: dict[str, Any] | None = Field(
        None, description="Asset views (html, text, subjectline, preheader)"
    )
    channels: dict[str, bool] | None = Field(
        None, description="Channel configuration (email, web, mobile)"
    )
    content: str | None = Field(None, description="Asset content")
    design: str | None = Field(None, description="Asset design")
    super_content: str | None = Field(
        None, alias="superContent", description="Super content"
    )

    # Organization fields
    category: dict[str, int] | None = Field(
        None, description="Category reference (e.g., {'id': 123})"
    )
    tags: list[str] | None = Field(None, description="Asset tags")

    # Advanced fields with aliases
    custom_fields: dict[str, Any] | None = Field(
        None, alias="customFields", description="Custom field data"
    )
    file_properties: dict[str, Any] | None = Field(
        None, alias="fileProperties", description="File properties"
    )
    business_unit_availability: dict[str, Any] | None = Field(
        None, alias="businessUnitAvailability", description="Business unit availability"
    )
    sharing_properties: dict[str, Any] | None = Field(
        None, alias="sharingProperties", description="Sharing properties"
    )
    generate_from: str | None = Field(
        None, alias="generateFrom", description="Generate from reference"
    )

    # Template/block fields
    template: dict[str, Any] | None = Field(None, description="Template information")
    blocks: dict[str, Any] | None = Field(None, description="Asset blocks")
    slots: dict[str, Any] | None = Field(None, description="Asset slots")
    min_blocks: int | None = Field(
        None, alias="minBlocks", description="Minimum blocks", ge=0
    )
    max_blocks: int | None = Field(
        None, alias="maxBlocks", description="Maximum blocks", ge=0
    )
    allowed_blocks: list[str] | None = Field(
        None, alias="allowedBlocks", description="Allowed block types"
    )

    # System fields
    data: dict[str, Any] | None = Field(None, description="Asset data object")
    meta: dict[str, Any] | None = Field(None, description="Asset metadata")
    version: int | None = Field(None, description="Asset version", ge=1)
    locked: bool | None = Field(None, description="Whether asset is locked")
    file: str | None = Field(None, description="Base64 encoded file content")


class AssetFilter(BaseModel):
    """Model for asset filtering parameters."""

    model_config = SFMC_MODEL_CONFIG

    page: int | None = Field(None, alias="$page", description="Page number", ge=1)
    page_size: int | None = Field(
        None, alias="$pageSize", description="Items per page", ge=1, le=50
    )
    order_by: str | None = Field(
        None, alias="$orderBy", description="Sort order (e.g., 'Name desc')"
    )
    filter: str | None = Field(
        None,
        alias="$filter",
        description="Filter expression (supports eq, neq, lt, lte, gt, gte, like "
        "operators)",
    )
    fields: str | None = Field(
        None, alias="$fields", description="Comma-separated list of fields to return"
    )
