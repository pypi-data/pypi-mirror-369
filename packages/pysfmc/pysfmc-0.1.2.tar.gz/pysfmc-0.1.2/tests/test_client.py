"""Tests for SFMC client functionality."""

import httpx
import pytest
import respx

from pysfmc import SFMCClient, SFMCSettings
from pysfmc.exceptions import SFMCAuthenticationError, SFMCNotFoundError


class TestSFMCClient:
    """Test cases for synchronous SFMC client."""

    def setup_method(self):
        """Setup test client with mock settings."""
        self.settings = SFMCSettings(
            client_id="test_client_id",
            client_secret="test_client_secret",
            account_id="123456789",
            subdomain="test-subdomain",
        )

    @respx.mock
    def test_get_categories_success(self):
        """Test successful retrieval of asset categories."""
        # Mock the authentication token request
        auth_url = f"https://{self.settings.subdomain.get_secret_value()}.auth.marketingcloudapis.com/v2/token"
        auth_response = {
            "access_token": "mock_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "asset_read",
            "soap_instance_url": "https://mock.soap.marketingcloudapis.com/",
            "rest_instance_url": "https://mock.rest.marketingcloudapis.com/",
        }
        respx.post(auth_url).mock(return_value=httpx.Response(200, json=auth_response))

        # Mock the categories API request
        categories_url = (
            "https://mock.rest.marketingcloudapis.com/asset/v1/content/categories"
        )
        categories_response = {
            "page": 1,
            "pageSize": 50,
            "count": 2,
            "items": [
                {
                    "id": 1001,
                    "name": "Email Templates",
                    "customerKey": "email_templates",
                    "parentId": 0,
                    "createdDate": "2024-01-01T10:00:00.000Z",
                    "modifiedDate": "2024-01-01T10:00:00.000Z",
                },
                {
                    "id": 1002,
                    "name": "Images",
                    "customerKey": "images",
                    "parentId": 0,
                    "createdDate": "2024-01-01T10:00:00.000Z",
                    "modifiedDate": "2024-01-01T10:00:00.000Z",
                },
            ],
        }
        respx.get(categories_url).mock(
            return_value=httpx.Response(200, json=categories_response)
        )

        # Test the client
        with SFMCClient(settings=self.settings) as client:
            response = client.get("/asset/v1/content/categories")

        # Assertions
        assert response["count"] == 2
        assert len(response["items"]) == 2
        assert response["items"][0]["name"] == "Email Templates"
        assert response["items"][1]["name"] == "Images"

    @respx.mock
    def test_get_categories_authentication_error(self):
        """Test handling of authentication errors."""
        # Mock failed authentication
        auth_url = f"https://{self.settings.subdomain.get_secret_value()}.auth.marketingcloudapis.com/v2/token"
        respx.post(auth_url).mock(
            return_value=httpx.Response(401, json={"message": "Invalid credentials"})
        )

        # Test that authentication error is raised
        with (
            pytest.raises(SFMCAuthenticationError),
            SFMCClient(settings=self.settings) as client,
        ):
            client.get("/asset/v1/content/categories")

    @respx.mock
    def test_get_categories_not_found(self):
        """Test handling of 404 errors."""
        # Mock successful authentication
        auth_url = f"https://{self.settings.subdomain.get_secret_value()}.auth.marketingcloudapis.com/v2/token"
        auth_response = {
            "access_token": "mock_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "asset_read",
            "soap_instance_url": "https://mock.soap.marketingcloudapis.com/",
            "rest_instance_url": "https://mock.rest.marketingcloudapis.com/",
        }
        respx.post(auth_url).mock(return_value=httpx.Response(200, json=auth_response))

        # Mock 404 response for categories
        categories_url = (
            "https://mock.rest.marketingcloudapis.com/asset/v1/content/categories"
        )
        respx.get(categories_url).mock(
            return_value=httpx.Response(404, json={"message": "Resource not found"})
        )

        # Test that not found error is raised
        with (
            pytest.raises(SFMCNotFoundError),
            SFMCClient(settings=self.settings) as client,
        ):
            client.get("/asset/v1/content/categories")

    @respx.mock
    def test_get_categories_with_params(self):
        """Test categories request with query parameters."""
        # Mock authentication
        auth_url = f"https://{self.settings.subdomain.get_secret_value()}.auth.marketingcloudapis.com/v2/token"
        auth_response = {
            "access_token": "mock_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "asset_read",
            "soap_instance_url": "https://mock.soap.marketingcloudapis.com/",
            "rest_instance_url": "https://mock.rest.marketingcloudapis.com/",
        }
        respx.post(auth_url).mock(return_value=httpx.Response(200, json=auth_response))

        # Mock categories with filtering
        categories_url = (
            "https://mock.rest.marketingcloudapis.com/asset/v1/content/categories"
        )
        categories_response = {
            "page": 1,
            "pageSize": 10,
            "count": 1,
            "items": [
                {
                    "id": 1001,
                    "name": "Email Templates",
                    "customerKey": "email_templates",
                    "parentId": 0,
                    "createdDate": "2024-01-01T10:00:00.000Z",
                    "modifiedDate": "2024-01-01T10:00:00.000Z",
                }
            ],
        }
        respx.get(categories_url).mock(
            return_value=httpx.Response(200, json=categories_response)
        )

        # Test with query parameters
        with SFMCClient(settings=self.settings) as client:
            response = client.get(
                "/asset/v1/content/categories", params={"$pageSize": 10, "$page": 1}
            )

        # Assertions
        assert response["count"] == 1
        assert response["pageSize"] == 10
        assert len(response["items"]) == 1
