"""Example: Query assets with filters using SFMC Assets Query API."""

import asyncio

from pysfmc import AsyncSFMCClient, SFMCClient


def sync_example():
    """Synchronous example of querying assets with filters."""
    print("=== Synchronous Asset Query Examples ===\n")

    with SFMCClient() as client:
        # Example 1: Get all assets with pagination
        print("1. Get first 10 assets:")
        assets = client.assets.query.get_assets(page=1, page_size=10)
        print(f"Total assets: {assets.count}")
        print(
            f"Page: {assets.page}/{(assets.count + assets.page_size - 1) // assets.page_size}"
        )

        for asset in assets.items:
            print(
                f"  - {asset.name} (ID: {asset.id}, Type: {asset.asset_type.name if asset.asset_type else 'N/A'})"
            )

        print("\n" + "=" * 50 + "\n")

        # Example 2: Filter by asset name
        print("2. Filter assets by name (containing 'email'):")
        assets = client.assets.query.get_assets(
            filter_expr="Name like 'email'", page_size=5
        )
        print(f"Found {assets.count} assets matching filter")

        for asset in assets.items:
            print(f"  - {asset.name} (ID: {asset.id})")

        print("\n" + "=" * 50 + "\n")

        # Example 3: Sort by creation date (newest first)
        print("3. Get assets sorted by creation date (newest first):")
        assets = client.assets.query.get_assets(
            order_by="createdDate desc", page_size=5
        )

        for asset in assets.items:
            print(f"  - {asset.name} (Created: {asset.created_date})")

        print("\n" + "=" * 50 + "\n")

        # Example 4: Selective fields
        print("4. Get only specific fields:")
        assets = client.assets.query.get_assets(
            fields="id,name,assetType,createdDate", page_size=5
        )

        for asset in assets.items:
            print(
                f"  - {asset.name} (ID: {asset.id}, Type: {asset.asset_type.name if asset.asset_type else 'N/A'})"
            )

        print("\n" + "=" * 50 + "\n")

        # Example 5: Complex filter (assets created this year)
        print("5. Filter assets created in 2024:")
        assets = client.assets.query.get_assets(
            filter_expr="createdDate gte '2024-01-01'",
            order_by="createdDate desc",
            page_size=5,
        )
        print(f"Found {assets.count} assets created in 2024")

        for asset in assets.items:
            print(f"  - {asset.name} (Created: {asset.created_date})")


async def async_example():
    """Asynchronous example of querying assets with filters."""
    print("=== Asynchronous Asset Query Example ===\n")

    async with AsyncSFMCClient() as client:
        # Get recent email templates
        assets = await client.assets.query.get_assets(
            filter_expr="assetType.name eq 'templatebasedemail'",
            order_by="modifiedDate desc",
            page_size=5,
        )

        print(f"Found {assets.count} email templates")
        print("Recent email templates:")

        for asset in assets.items:
            print(f"  - {asset.name}")
            print(f"    Modified: {asset.modified_date}")
            if asset.description:
                print(f"    Description: {asset.description}")
            print()


def main():
    """Run both sync and async examples."""
    try:
        sync_example()
        print("\n" + "=" * 60 + "\n")
        asyncio.run(async_example())
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure your SFMC credentials are configured in .env file")


if __name__ == "__main__":
    main()
