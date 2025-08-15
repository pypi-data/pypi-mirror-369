"""Python client for Salesforce Marketing Cloud (SFMC) API."""

from .assets import AssetsClient, AsyncAssetsClient
from .auth import SFMCSettings
from .client import AsyncSFMCClient, SFMCClient
from .config import SFMCConfig
from .exceptions import (
    SFMCAuthenticationError,
    SFMCAuthorizationError,
    SFMCConnectionError,
    SFMCError,
    SFMCNotFoundError,
    SFMCRateLimitError,
    SFMCServerError,
    SFMCValidationError,
)
from .models.assets import (
    AssetTypeCreate,
    Category,
    CategoryCreate,
    CategoryResponse,
    CreateAsset,
)

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "SFMCClient",
    "AsyncSFMCClient",
    "SFMCSettings",
    "SFMCConfig",
    # Assets clients
    "AssetsClient",
    "AsyncAssetsClient",
    # Models
    "Category",
    "CategoryCreate",
    "CategoryResponse",
    "CreateAsset",
    "AssetTypeCreate",
    # Exceptions
    "SFMCError",
    "SFMCAuthenticationError",
    "SFMCAuthorizationError",
    "SFMCValidationError",
    "SFMCNotFoundError",
    "SFMCRateLimitError",
    "SFMCServerError",
    "SFMCConnectionError",
]
