"""
The goal of this example is to showcase how to create an image asset in SFMC.
"""
import os.path

from dotenv import load_dotenv
from pysfmc import SFMCClient, SFMCNotFoundError
from pysfmc.models.assets import AssetType, Asset
import base64

def create_image() -> Asset:
    load_dotenv()
    client = SFMCClient()

    image_path = "../assets/cat-eating-chicken.png"

    with open(image_path, "rb") as file:
        content = base64.b64encode(file.read())

    _, image_extension = os.path.splitext(image_path)  # ex:  .jpg
    asset_type = AssetType.from_name(image_extension[1:])

    created_asset = client.assets.content.create_asset(
        name="[TEST] Cat Eating Chicken",
        asset_type_name=asset_type.name,
        asset_type_id=asset_type.id,
        file_properties={
            "fileName": "cat-eating-chicken.png"
        },
        file=content,  # base64-encoded content
        category_id=108336  # a test category, replace by your own
    )

    return created_asset

def main():
    load_dotenv()
    client = SFMCClient()

    print("Create new asset...")
    new_asset = create_image()
    print(f"Asset '{new_asset.name}' (ID: {new_asset.id}) created")

    ret = client.assets.content.delete_asset(new_asset.id)

    print(ret)

    try:
        client.assets.query.get_asset_by_id(new_asset.id)
    except SFMCNotFoundError as e:
        print(e, "Asset deleted !")


if __name__ == '__main__':
    main()
