# pysfmc

A modern, type-safe Python client library for Salesforce Marketing Cloud (SFMC) API.

## Features

- **🔄 Sync & Async**: Full support for both synchronous and asynchronous operations
- **🔐 Auto Authentication**: Automatic OAuth2 token management with refresh
- **📝 Type Safety**: Comprehensive Pydantic models for request/response validation
- **🚀 Modern**: Built with httpx, supports Python 3.10+
- **⚡ Rate Limiting**: Built-in rate limiting and error handling
- **🎯 Assets API**: Complete support for Content Builder (Categories, Query, Content)

### Implemented endpoints

As of right now, only parts of the [Content Builder REST API](https://developer.salesforce.com/docs/marketing/marketing-cloud/guide/content-api.html)
is implemented:

| HTTP Method | Resource | Description | Supported |
|-------------|----------|-------------|----------|
| GET | `/asset/v1/content/assets` | Gets an asset collection with filtering and pagination. | ✅ |
| GET | `/asset/v1/content/assets/{id}` | Gets an asset by ID. | ✅ |
| POST | `/asset/v1/content/assets` | Inserts an asset. | ✅ |
| PUT | `/asset/v1/content/assets/{id}` | Updates a full asset. | ❌ |
| PATCH | `/asset/v1/content/assets/{id}` | Updates part of an asset deleted in the last 30 days. | ❌ |
| DELETE | `/asset/v1/content/assets/{id}` | Deletes an asset. | ✅ |
| GET | `/asset/v1/content/assets/{id}/file` | Gets the binary file for an asset. | ❌ |
| GET | `/asset/v1/content/assets/salutations` | Gets the default header and footer for an account. | ❌ |
| GET | `/asset/v1/content/assets/{id}/salutations` | Gets the header and footer for a message. | ❌ |
| GET | `/asset/v1/content/assets/{id}/channelviews/{viewname}` | Returns the requested channel view's compiled HTML for the asset. | ❌ |
| POST | `/asset/v1/content/categories` | Inserts a category. | ✅ |
| GET | `/asset/v1/content/categories` | Gets a collection of categories. | ✅ |
| GET | `/asset/v1/content/categories/{id}` | Gets a category by ID. | ✅ |
| PUT | `/asset/v1/content/categories/{id}` | Updates a category by ID. | ❌ |
| DELETE | `/asset/v1/content/categories/{id}` | Deletes a category by ID. | ✅ |


## Installation

Install using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv add pysfmc
```

Or with pip:

```bash
pip install pysfmc
```

## Quick Start

### 1. Environment Setup

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

Configure your SFMC credentials:

```env
SFMC_CLIENT_ID=your_client_id
SFMC_CLIENT_SECRET=your_client_secret
SFMC_ACCOUNT_ID=your_account_id
SFMC_SUBDOMAIN=your_subdomain
```

### 2. Basic Usage

```python
from pysfmc import SFMCClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Synchronous client
with SFMCClient() as client:
    # Get categories
    categories = client.assets.categories.get_categories(page_size=10)
    print(f"Found {categories.count} categories")

    for category in categories.items:
        print(f"- {category.name} (ID: {category.id})")
```

### 3. Async Usage

```python
import asyncio
from pysfmc import AsyncSFMCClient
from dotenv import load_dotenv

async def main():
    load_dotenv()

    async with AsyncSFMCClient() as client:
        # Query assets with filters
        assets = await client.assets.query.get_assets(
            filter_expr="Name like 'newsletter'",
            order_by="createdDate desc",
            page_size=5
        )

        print(f"Found {assets.count} matching assets")
        for asset in assets.items:
            print(f"- {asset.name} (Type: {asset.asset_type.name})")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Features

### Assets Categories API

Manage Content Builder categories (folders):

```python
with SFMCClient() as client:
    # Get all categories with pagination
    categories = client.assets.categories.get_categories(
        page=1,
        page_size=20,
        order_by="name asc"
    )

    # Get specific category
    category = client.assets.categories.get_category_by_id(12345)

    # Create new category
    new_category = client.assets.categories.create_category(
        name="My New Folder",
        parent_id=4793,
        description="Created via pysfmc"
    )

    # Filter by parent (only supported filter)
    root_categories = client.assets.categories.get_categories(
        parent_id=0  # Root level categories
    )
```

### Assets Query API

Search and filter assets with advanced queries:

```python
with SFMCClient() as client:
    # Basic asset search
    assets = client.assets.query.get_assets(page_size=10)

    # Filter by name
    email_assets = client.assets.query.get_assets(
        filter_expr="Name like 'email'"
    )

    # Filter by asset type
    templates = client.assets.query.get_assets(
        filter_expr="assetType.name eq 'templatebasedemail'"
    )

    # Complex filtering with date ranges
    recent_assets = client.assets.query.get_assets(
        filter_expr="createdDate gte '2024-01-01'",
        order_by="createdDate desc",
        page_size=20
    )

    # Get specific fields only
    minimal_assets = client.assets.query.get_assets(
        fields="id,name,assetType,createdDate",
        page_size=50
    )

    # Get asset by ID
    asset = client.assets.query.get_asset_by_id(141754)
    print(f"Asset: {asset.name}")
    print(f"Type: {asset.asset_type.name}")
    print(f"Created: {asset.created_date}")
```

### Advanced Async Operations

```python
import asyncio
from pysfmc import AsyncSFMCClient

async def fetch_multiple_categories(client, category_ids):
    """Fetch multiple categories concurrently."""
    tasks = [
        client.assets.categories.get_category_by_id(cat_id)
        for cat_id in category_ids
    ]
    return await asyncio.gather(*tasks)

async def main():
    async with AsyncSFMCClient() as client:
        # Get category IDs
        categories = await client.assets.categories.get_categories(page_size=5)
        category_ids = [cat.id for cat in categories.items]

        # Fetch all categories concurrently
        detailed_categories = await fetch_multiple_categories(client, category_ids)

        for category in detailed_categories:
            print(f"Category: {category.name} (Enterprise: {category.enterprise_id})")
```

## Error Handling

The library provides structured exception handling:

```python
from pysfmc import SFMCClient
from pysfmc.exceptions import (
    SFMCAuthenticationError,
    SFMCRateLimitError,
    SFMCNotFoundError,
    SFMCServerError
)

with SFMCClient() as client:
    try:
        category = client.assets.categories.get_category_by_id(99999)
    except SFMCNotFoundError:
        print("Category not found")
    except SFMCAuthenticationError:
        print("Authentication failed - check credentials")
    except SFMCRateLimitError as e:
        print(f"Rate limited - retry after {e.retry_after} seconds")
    except SFMCServerError:
        print("SFMC server error - try again later")
```

## Configuration

### Environment Variables

All configuration uses the `SFMC_` prefix:

```env
# Required
SFMC_CLIENT_ID=your_app_client_id
SFMC_CLIENT_SECRET=your_app_client_secret
SFMC_ACCOUNT_ID=your_account_mid
SFMC_SUBDOMAIN=your_tenant_subdomain

# Optional
SFMC_CLIENT__TIMEOUT=30.0
SFMC_RATE_LIMIT__REQUESTS_PER_MINUTE=2500
SFMC_DEBUG=false
```

### Programmatic Configuration

```python
from pysfmc import SFMCClient, SFMCSettings

# Custom settings
settings = SFMCSettings(
    client_id="your_client_id",
    client_secret="your_client_secret",
    account_id="your_account_id",
    subdomain="your_subdomain"
)

with SFMCClient(settings=settings) as client:
    # Use client with custom settings
    pass
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd pysfmc

# Install with development dependencies
uv sync --group dev

# Run tests
uv run pytest
```

### Running Examples

```bash
# Set up environment
cp .env.example .env
# Edit .env with your credentials
```

The [examples](./examples) folder is there to answer your questions

## Requirements

- Python 3.9+

## License

This project is licensed under the MIT License.

## Support

- **Documentation**: Check the `examples/` directory for usage patterns
- **Issues**: Report bugs and feature requests on GitHub
- **SFMC API**: Refer to [Salesforce Marketing Cloud API documentation](https://developer.salesforce.com/docs/marketing/marketing-cloud/overview)
