"""Example script to get all categories from Salesforce Marketing Cloud."""

from pprint import pprint

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
            response = client.get("/asset/v1/content/categories/4793")

            # Print summary
            pprint(response)

            print(f"{response['id']=}")
            print(f"{response['description']=}")
            print(f"{response['enterpriseId']=}")
            print(f"{response['memberId']=}")
            print(f"{response['name']=}")
            print(f"{response['parentId']=}")
            print(f"{response['categoryType']=}")

        except Exception as e:
            print(f"Error getting categories: {e}")
            return 1

    return 0


if __name__ == "__main__":
    exit(main())
