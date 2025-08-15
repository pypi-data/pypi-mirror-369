"""Block models for SFMC Assets API with recursive slot/block support."""

from typing import Any, ForwardRef

from pydantic import BaseModel, Field

from ..base import SFMC_MODEL_CONFIG

# Forward references for recursive relationships
BlockRef = ForwardRef("Block")
SlotRef = ForwardRef("Slot")


class Block(BaseModel):
    """Recursive block model supporting nested slots and blocks.

    Blocks can contain:
    - Other blocks (for complex layouts)
    - Slots (for layout blocks that define content areas)
    - Both simultaneously
    """

    model_config = SFMC_MODEL_CONFIG

    # Core block properties
    asset_type: dict[str, Any] = Field(..., alias="assetType")
    content: str = Field(default="", description="HTML content of the block")
    design: str | None = Field(default="", description="Design-time HTML content")

    # Metadata and styling (simplified from nested classes)
    meta: dict[str, Any] | None = None
    data: dict[str, Any] | None = None

    # Recursive relationships - blocks can contain both blocks and slots
    blocks: dict[str, BlockRef] = Field(
        default_factory=dict, description="Nested blocks"
    )
    slots: dict[str, SlotRef] = Field(default_factory=dict, description="Nested slots")

    # Version and views
    model_version: int = Field(default=2, alias="modelVersion")
    available_views: list[str] = Field(default_factory=list, alias="availableViews")

    # Optional asset metadata (for blocks that reference actual assets)
    id: int | None = None
    customer_key: str | None = Field(None, alias="customerKey")
    object_id: str | None = Field(None, alias="objectID")
    name: str | None = None
    description: str | None = None

    # Ownership and dates (for asset-backed blocks)
    owner: dict[str, Any] | None = None
    created_by: dict[str, Any] | None = Field(None, alias="createdBy")
    modified_by: dict[str, Any] | None = Field(None, alias="modifiedBy")
    created_date: str | None = Field(None, alias="createdDate")
    modified_date: str | None = Field(None, alias="modifiedDate")

    # Enterprise info
    enterprise_id: int | None = Field(None, alias="enterpriseId")
    member_id: int | None = Field(None, alias="memberId")

    # Status and category
    status: dict[str, Any] | None = None
    category: dict[str, Any] | None = None
    thumbnail: dict[str, Any] | None = None
    file_properties: dict[str, Any] | None = Field(None, alias="fileProperties")


class Slot(BaseModel):
    """Recursive slot model supporting nested blocks and slots.

    Slots can contain:
    - Blocks (the primary content)
    - Other slots (for complex nested layouts)
    - Constraints and metadata
    """

    model_config = SFMC_MODEL_CONFIG

    # Core slot properties
    content: str = Field(default="", description="HTML content with block placeholders")
    design: str | None = Field(
        default="", description="Design-time placeholder content"
    )

    # Recursive relationships - slots can contain both blocks and slots
    blocks: dict[str, BlockRef] = Field(
        default_factory=dict, description="Blocks in this slot"
    )
    slots: dict[str, SlotRef] = Field(default_factory=dict, description="Nested slots")

    # Slot constraints and configuration
    min_blocks: int | None = Field(
        None, alias="minBlocks", description="Minimum blocks allowed"
    )
    max_blocks: int | None = Field(
        None, alias="maxBlocks", description="Maximum blocks allowed"
    )
    allowed_blocks: list[str] | None = Field(
        None, alias="allowedBlocks", description="Allowed block types"
    )

    # Metadata and styling (simplified from nested classes)
    content_type: str | None = Field(None, alias="contentType")
    locked: bool | None = None
    thumbnail: dict[str, Any] | None = Field(default_factory=dict)
    meta: dict[str, Any] | None = None
    data: dict[str, Any] | None = None

    # Version and views
    model_version: int = Field(default=2, alias="modelVersion")
    available_views: list[str] = Field(default_factory=list, alias="availableViews")


# Resolve forward references after model definitions
Block.model_rebuild()
Slot.model_rebuild()
