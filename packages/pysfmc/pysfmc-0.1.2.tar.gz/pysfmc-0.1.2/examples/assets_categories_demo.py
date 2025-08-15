"""Demo script showing the new Assets (Content Builder) Categories client."""

import asyncio

from dotenv import load_dotenv

from pysfmc import AsyncSFMCClient, SFMCClient


def sync_demo():
    """Demonstrate synchronous assets categories client."""
    print("=== Synchronous Assets Categories Demo ===")

    # Load environment variables
    load_dotenv()

    with SFMCClient() as client:
        try:
            # Get all categories with pagination
            print("\n1. Getting first 10 categories:")
            categories_response = client.assets.categories.get_categories(
                page=1, page_size=10
            )

            print(f"Total categories: {categories_response.count}")
            print(f"Page: {categories_response.page}")
            print(f"Page size: {categories_response.page_size}")
            print(f"Categories on this page: {len(categories_response.items)}")

            # Show first few categories
            for category in categories_response.items[:3]:
                print(
                    f"  - {category.name} (ID: {category.id}, Parent: {category.parent_id})"
                )

            # Get a specific category by ID
            if categories_response.items:
                first_category = categories_response.items[0]
                print(f"\n2. Getting category by ID ({first_category.id}):")
                specific_category = client.assets.categories.get_category_by_id(
                    first_category.id
                )
                print(f"  Name: {specific_category.name}")
                print(f"  Description: {specific_category.description or 'N/A'}")
                print(f"  Type: {specific_category.category_type}")
                print(f"  Enterprise ID: {specific_category.enterprise_id}")
                print(f"  Member ID: {specific_category.member_id}")

            # Filter categories by parent ID
            print("\n3. Getting child categories of root folder:")
            root_categories = client.assets.categories.get_categories(
                parent_id=0,
                page_size=5,  # Root level
            )

            print(f"Root level categories: {len(root_categories.items)}")
            for category in root_categories.items:
                print(f"  - {category.name} (ID: {category.id})")

            # Example of creating a category (commented out to avoid creating test folders)
            print("\n4. Category creation example (not executed):")
            print("  # new_category = client.assets.categories.create_category(")
            print("  #     name='Demo Folder',")
            print("  #     parent_id=4793,  # Use actual parent ID")
            print("  #     description='Created via pysfmc demo'")
            print("  # )")

        except Exception as e:
            print(f"Error: {e}")


async def async_demo():
    """Demonstrate asynchronous assets categories client."""
    print("\n=== Asynchronous Assets Categories Demo ===")

    # Load environment variables
    load_dotenv()

    async with AsyncSFMCClient() as client:
        try:
            # Get categories with parentId filtering (only supported filter)
            print("\n1. Getting categories with parentId filter:")
            filtered_categories = await client.assets.categories.get_categories(
                filter_expr="parentId eq 4793",  # Only parentId filtering is supported
                page_size=5,
            )

            print(f"Categories with parentId=4793: {len(filtered_categories.items)}")
            for category in filtered_categories.items:
                print(f"  - {category.name} (ID: {category.id})")

            # Get multiple categories concurrently
            if len(filtered_categories.items) >= 2:
                print("\n2. Getting multiple categories concurrently:")
                category_ids = [cat.id for cat in filtered_categories.items[:2]]

                # Fetch multiple categories concurrently
                category_tasks = [
                    client.assets.categories.get_category_by_id(cat_id)
                    for cat_id in category_ids
                ]

                categories = await asyncio.gather(*category_tasks)

                for category in categories:
                    print(f"  - {category.name} (Enterprise: {category.enterprise_id})")

        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run both sync and async demos."""
    print("Assets Categories Client Demo")
    print("=" * 40)

    # Run synchronous demo
    sync_demo()

    # Run asynchronous demo
    asyncio.run(async_demo())

    print("\n=== Demo Complete ===")
    print("The Assets client provides a clean, typed interface to SFMC Categories API:")
    print("  - Structured models with Pydantic validation")
    print("  - Simple method signatures hiding API complexity")
    print("  - Support for filtering, pagination, and ordering")
    print("  - Both sync and async implementations")


if __name__ == "__main__":
    main()
