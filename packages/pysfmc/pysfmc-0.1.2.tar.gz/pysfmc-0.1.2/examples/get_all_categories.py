"""Example script to get all categories from Salesforce Marketing Cloud."""

from dotenv import load_dotenv

from pysfmc import SFMCClient


def main():
    """Get all categories and print them."""
    # Load environment variables from .env file
    load_dotenv()

    # Create client (will automatically load SFMC_* variables from environment)
    with SFMCClient() as client:
        try:
            # Get all categories
            response = client.get("/asset/v1/content/categories")

            # Print summary
            categories = response.get("items", [])
            print(f"Found {len(categories)} categories")
            print(f"Page: {response.get('page', 'N/A')}")
            print(f"Page Size: {response.get('pageSize', 'N/A')}")
            print(f"Total Count: {response.get('count', 'N/A')}")
            print()

            # Print each category
            for category in categories:
                print(f"ID: {category.get('id')}")
                print(f"Name: {category.get('name')}")
                print(f"Category Type: {category.get('categoryType')}")
                print(f"Description: {category.get('description', 'N/A')}")
                print(f"Parent ID: {category.get('parentId')}")
                print(f"Enterprise ID: {category.get('enterpriseId')}")
                print(f"Member ID: {category.get('memberId')}")
                print("-" * 40)

        except Exception as e:
            print(f"Error getting categories: {e}")
            return 1

    return 0


if __name__ == "__main__":
    exit(main())
