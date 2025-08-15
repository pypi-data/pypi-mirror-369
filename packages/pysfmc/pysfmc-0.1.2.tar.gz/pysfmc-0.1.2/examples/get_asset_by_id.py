"""Example: Get asset by ID using SFMC Assets Query API."""

from dotenv import load_dotenv

from pysfmc import SFMCClient

# Example asset ID - replace with actual asset ID from your SFMC instance
ASSET_ID = 141754


def main():
    load_dotenv()
    """Get a specific asset by ID."""
    with SFMCClient() as client:
        # Get asset by ID
        asset = client.assets.query.get_asset_by_id(ASSET_ID)

        print(f"Asset ID: {asset.id}")
        print(f"Name: {asset.name}")
        print(f"Asset Type: {asset.asset_type.name if asset.asset_type else 'N/A'}")
        print(f"Content Type: {asset.content_type}")
        print(f"Description: {asset.description or 'No description'}")
        print(f"Created Date: {asset.created_date}")
        print(f"Modified Date: {asset.modified_date}")

        if asset.owner:
            print(f"Owner: {asset.owner.name} ({asset.owner.email})")

        if asset.category:
            print(f"Category: {asset.category.name}")

        if asset.status:
            print(f"Status: {asset.status.name}")


if __name__ == "__main__":
    main()
