"""Authentication module for Salesforce Marketing Cloud API."""

from datetime import datetime, timedelta
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import map_http_error


class SFMCSettings(BaseSettings):
    """SFMC API credentials and configuration."""

    client_id: SecretStr = Field(..., description="SFMC application client ID")
    client_secret: SecretStr = Field(..., description="SFMC application client secret")
    account_id: SecretStr = Field(..., description="SFMC account/MID identifier")
    subdomain: SecretStr = Field(..., description="SFMC tenant subdomain")

    model_config = SettingsConfigDict(
        env_prefix="SFMC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def auth_base_url(self) -> SecretStr:
        """Get the authentication base URL for this tenant."""
        return SecretStr(
            f"https://{self.subdomain.get_secret_value()}.auth.marketingcloudapis.com"
        )


class TokenResponse(BaseModel):
    """Response model for SFMC OAuth2 token endpoint."""

    access_token: SecretStr
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="Token lifetime in seconds")
    scope: str
    soap_instance_url: SecretStr
    rest_instance_url: SecretStr


class SFMCAuthenticator:
    """Handles SFMC OAuth2 authentication and token management."""

    def __init__(self, settings: SFMCSettings, http_client: httpx.Client | None = None):
        self.settings = settings
        self._http_client = http_client or httpx.Client()
        self._token: TokenResponse | None = None
        self._token_expires_at: datetime | None = None
        self._refresh_buffer = timedelta(minutes=2)  # Refresh 2 minutes before expiry

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._token or not self._token_expires_at:
            return False
        return datetime.now() < (self._token_expires_at - self._refresh_buffer)

    def _request_new_token(self) -> TokenResponse:
        """Request a new access token from SFMC."""
        token_url = urljoin(self.settings.auth_base_url.get_secret_value(), "/v2/token")

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.settings.client_id.get_secret_value(),
            "client_secret": self.settings.client_secret.get_secret_value(),
            "account_id": self.settings.account_id.get_secret_value(),
        }

        headers = {"Content-Type": "application/json"}

        response = self._http_client.post(token_url, json=payload, headers=headers)

        if not response.is_success:
            raise map_http_error(response)

        token_data = response.json()
        return TokenResponse(**token_data)

    def get_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if not self._is_token_valid():
            self._token = self._request_new_token()
            self._token_expires_at = datetime.now() + timedelta(
                seconds=self._token.expires_in
            )

        return self._token.access_token.get_secret_value()

    def get_auth_header(self) -> dict[str, str]:
        """Get the authorization header for API requests."""
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}

    def get_rest_base_url(self) -> str:
        """Get the REST API base URL for this tenant."""
        if not self._token:
            self.get_token()  # This will populate _token
        return self._token.rest_instance_url.get_secret_value()

    def get_soap_base_url(self) -> str:
        """Get the SOAP API base URL for this tenant."""
        if not self._token:
            self.get_token()  # This will populate _token
        return self._token.soap_instance_url.get_secret_value()

    def close(self) -> None:
        """Close the HTTP client."""
        self._http_client.close()


class AsyncSFMCAuthenticator:
    """Async version of SFMC authenticator."""

    def __init__(
        self, settings: SFMCSettings, http_client: httpx.AsyncClient | None = None
    ):
        self.settings = settings
        self._http_client = http_client or httpx.AsyncClient()
        self._token: TokenResponse | None = None
        self._token_expires_at: datetime | None = None
        self._refresh_buffer = timedelta(minutes=2)

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._token or not self._token_expires_at:
            return False
        return datetime.now() < (self._token_expires_at - self._refresh_buffer)

    async def _request_new_token(self) -> TokenResponse:
        """Request a new access token from SFMC."""
        token_url = urljoin(self.settings.auth_base_url.get_secret_value(), "/v2/token")

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.settings.client_id.get_secret_value(),
            "client_secret": self.settings.client_secret.get_secret_value(),
            "account_id": self.settings.account_id.get_secret_value(),
        }

        headers = {"Content-Type": "application/json"}

        response = await self._http_client.post(
            token_url, json=payload, headers=headers
        )

        if not response.is_success:
            raise map_http_error(response)

        token_data = response.json()
        return TokenResponse(**token_data)

    async def get_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if not self._is_token_valid():
            self._token = await self._request_new_token()
            self._token_expires_at = datetime.now() + timedelta(
                seconds=self._token.expires_in
            )

        return self._token.access_token.get_secret_value()

    async def get_auth_header(self) -> dict[str, str]:
        """Get the authorization header for API requests."""
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}

    async def get_rest_base_url(self) -> str:
        """Get the REST API base URL for this tenant."""
        if not self._token:
            await self.get_token()  # This will populate _token
        return self._token.rest_instance_url.get_secret_value()

    async def get_soap_base_url(self) -> str:
        """Get the SOAP API base URL for this tenant."""
        if not self._token:
            await self.get_token()  # This will populate _token
        return self._token.soap_instance_url.get_secret_value()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()
