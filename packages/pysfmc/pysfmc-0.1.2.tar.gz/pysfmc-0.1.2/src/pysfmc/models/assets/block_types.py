"""Block type mappings and utilities for SFMC block types."""

from .blocks import Block

# SFMC Block Types (from official documentation)
BLOCK_TYPES = {
    195: "freeformblock",
    196: "textblock",
    197: "htmlblock",
    198: "textplusimageblock",
    199: "imageblock",
    200: "abtestblock",
    201: "dynamicblock",
    202: "stylingblock",
    203: "einsteincontentblock",
    210: "socialshareblock",
    211: "socialfollowblock",
    212: "buttonblock",
    213: "layoutblock",
    215: "smartcaptureblock",
    219: "externalcontentblock",
    220: "codesnippetblock",
    221: "rssfeedblock",
    222: "formstylingblock",
    223: "referenceblock",
    224: "imagecarouselblock",
    225: "customblock",
    226: "liveimageblock",
    227: "livesettingblock",
    229: "enhanceddynamicblock",
    233: "icecloudpageblock",
    234: "einsteincontentselectionblock",
    238: "einsteincontenttestingblock",
    239: "coderesourceblock",
}

# Reverse mapping
BLOCK_NAMES = {name: id for id, name in BLOCK_TYPES.items()}


def create_block_by_type(asset_type_id: int, **kwargs) -> Block:
    """Create a block instance with the specified asset type ID."""
    asset_type = {
        "id": asset_type_id,
        "name": BLOCK_TYPES.get(asset_type_id, "unknownblock"),
    }
    return Block(assetType=asset_type, **kwargs)


def create_block_by_name(asset_type_name: str, **kwargs) -> Block:
    """Create a block instance with the specified asset type name."""
    asset_type_id = BLOCK_NAMES.get(asset_type_name, 0)
    asset_type = {"id": asset_type_id, "name": asset_type_name}
    return Block(assetType=asset_type, **kwargs)
